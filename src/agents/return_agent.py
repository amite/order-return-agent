"""Order Return Agent - Main agent for processing customer returns"""

import json
import uuid
from typing import Optional

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from loguru import logger

from src.config.settings import settings
from src.config.prompts import AGENT_SYSTEM_PROMPT, ESCALATION_SUMMARY_PROMPT
from src.db.connection import get_db_session
from src.db.schema import ConversationLog
from src.rag.knowledge_base import KnowledgeBase
from src.tools.order_tools import GetOrderDetailsTool
from src.tools.eligibility_tools import CheckEligibilityTool
from src.tools.rma_tools import CreateRMATool
from src.tools.logistics_tools import GenerateReturnLabelTool
from src.tools.email_tools import SendEmailTool
from src.tools.escalation_tools import EscalateToHumanTool


class ReturnAgent:
    """
    Agent for processing customer returns.

    Orchestrates tool calling, RAG retrieval, and conversation flow.
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the Return Agent.

        Args:
            session_id: Optional session ID for conversation tracking.
                       If not provided, a new UUID will be generated.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.settings = settings
        self.logger = logger

        # Initialize LLM
        self._initialize_llm()

        # Initialize tools
        self._initialize_tools()

        # Initialize RAG
        self._initialize_rag()

        # Create agent
        self.agent_executor = self._create_agent()

        self.logger.info(f"ReturnAgent initialized with session_id: {self.session_id}")

    def _initialize_llm(self) -> None:
        """Initialize the Ollama LLM for the agent"""
        self.llm = ChatOllama(
            base_url=self.settings.ollama_base_url,
            model=self.settings.ollama_model,
            temperature=self.settings.agent_temperature,
            timeout=self.settings.agent_max_execution_time,
        )
        self.logger.debug(
            f"LLM initialized: {self.settings.ollama_model} "
            f"@ {self.settings.ollama_base_url}"
        )

    def _initialize_tools(self) -> None:
        """Initialize all available tools for the agent"""
        self.tools = [
            GetOrderDetailsTool(),
            CheckEligibilityTool(),
            CreateRMATool(),
            GenerateReturnLabelTool(),
            SendEmailTool(),
            EscalateToHumanTool(),
        ]
        self.logger.debug(f"Initialized {len(self.tools)} tools")

    def _initialize_rag(self) -> None:
        """Initialize the RAG knowledge base"""
        self.knowledge_base = KnowledgeBase()

        # Check if knowledge base is healthy
        if not self.knowledge_base.health_check():
            self.logger.warning(
                "Knowledge base health check failed. "
                "Attempting to ingest documents..."
            )
            num_docs = self.knowledge_base.ingest_documents()
            self.logger.info(f"Ingested {num_docs} documents into knowledge base")
        else:
            self.logger.debug("Knowledge base is healthy")

    def _create_agent(self):
        """
        Create the LangChain agent with tools.

        Returns:
            Agent configured for the return process
        """
        # Create the agent using the new LangChain v1 API
        # Note: max_iterations and timeout are handled at invocation time
        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=AGENT_SYSTEM_PROMPT,
        )

        self.logger.debug("Agent created with create_agent")
        return agent

    def run(self, user_input: str) -> str:
        """
        Execute the agent with user input.

        Follows the conversation flow:
        1. Accept user input
        2. Execute agent with tools
        3. Log conversation
        4. Return formatted response

        Args:
            user_input: The customer's message

        Returns:
            The agent's response to the customer
        """
        self.logger.info(f"[{self.session_id}] Processing user input")

        # Log user message
        self._log_conversation(message_type="user", content=user_input)

        try:
            # Execute agent with LangChain v1 API
            # The agent expects a dict with "messages" key
            from langchain_core.messages import HumanMessage

            result = self.agent_executor.invoke(
                {"messages": [HumanMessage(content=user_input)]},
            )

            # Extract response from result
            # result contains the final message(s) from the agent
            response = ""
            if isinstance(result, dict) and "messages" in result:
                # Get the last message's content
                messages = result["messages"]
                if messages and hasattr(messages[-1], "content"):
                    response = messages[-1].content
            elif isinstance(result, str):
                response = result
            else:
                # Try to extract text from result object
                response = str(result)

            # Format response for clarity
            formatted_response = self._format_response(response)

            # Log agent response
            self._log_conversation(
                message_type="assistant",
                content=formatted_response,
            )

            self.logger.debug(f"[{self.session_id}] Agent response: {formatted_response}")

            return formatted_response

        except Exception as e:
            self.logger.error(f"[{self.session_id}] Error during agent execution: {e}")

            # Handle tool errors with retry logic
            error_response = self._handle_tool_errors(e)

            # Log error
            self._log_conversation(
                message_type="system",
                content=error_response,
                meta_data={"error": str(e)},
            )

            return error_response

    def _format_response(self, response: str) -> str:
        """
        Format agent response for better readability.

        Cleans up thinking text and ensures clear communication.

        Args:
            response: Raw response from agent

        Returns:
            Formatted response
        """
        # Remove thinking tags if present
        response = response.replace("<thinking>", "").replace("</thinking>", "")

        # Remove extra whitespace
        response = response.strip()

        # Ensure response is not empty
        if not response:
            return (
                "I apologize, but I wasn't able to process your request. "
                "Could you please try again?"
            )

        return response

    def _handle_tool_errors(self, error: Exception) -> str:
        """
        Handle errors during tool execution with fallback responses.

        Args:
            error: The exception that occurred

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        self.logger.error(f"Tool error ({error_type}): {str(error)}")

        # Check for specific error types
        if "timeout" in str(error).lower():
            return (
                "I'm currently experiencing high load. "
                "Let me connect you with a specialist who can help right away."
            )

        if "database" in str(error).lower():
            return (
                "I'm having trouble accessing our system. "
                "Let me get a human agent to assist you."
            )

        if "model" in str(error).lower() or "ollama" in str(error).lower():
            return (
                "I'm temporarily unavailable. "
                "Please hold while I connect you with a specialist."
            )

        # Generic fallback
        return (
            "I apologize for the inconvenience. "
            "Let me transfer you to a human agent who can better assist you."
        )

    def _log_conversation(
        self,
        message_type: str,
        content: str,
        meta_data: Optional[dict] = None,
    ) -> None:
        """
        Log conversation to database.

        Stores both user and agent messages for audit trail and learning.

        Args:
            message_type: Type of message (user, assistant, tool, system)
            content: Message content
            meta_data: Optional metadata dictionary (tool results, errors, etc.)
        """
        try:
            with get_db_session() as session:
                meta_data_json = json.dumps(meta_data) if meta_data else None

                log_entry = ConversationLog(
                    session_id=self.session_id,
                    message_type=message_type,
                    content=content,
                    meta_data=meta_data_json,
                )

                session.add(log_entry)
                session.commit()

                self.logger.debug(
                    f"Logged {message_type} message to conversation history"
                )

        except Exception as e:
            self.logger.error(f"Failed to log conversation: {e}")

    def get_conversation_history(self) -> list[dict]:
        """
        Retrieve conversation history for this session.

        Returns:
            List of conversation log entries
        """
        try:
            with get_db_session() as session:
                logs = (
                    session.query(ConversationLog)
                    .filter(ConversationLog.session_id == self.session_id)
                    .order_by(ConversationLog.created_at)
                    .all()
                )

                history = [
                    {
                        "timestamp": log.created_at.isoformat(),
                        "type": log.message_type,
                        "content": log.content,
                        "metadata": json.loads(log.meta_data) if log.meta_data else None,
                    }
                    for log in logs
                ]

                return history

        except Exception as e:
            self.logger.error(f"Failed to retrieve conversation history: {e}")
            return []

    def escalate(self, reason: str) -> str:
        """
        Escalate the conversation to a human agent.

        Prepares context and summary for handoff.

        Args:
            reason: Reason for escalation

        Returns:
            Confirmation message
        """
        self.logger.info(f"[{self.session_id}] Escalating conversation: {reason}")

        # Get conversation history
        history = self.get_conversation_history()

        # Format conversation for summary
        conversation_text = "\n".join(
            f"{entry['type']}: {entry['content']}" for entry in history
        )

        # Create escalation summary prompt
        summary_prompt = PromptTemplate.from_template(ESCALATION_SUMMARY_PROMPT)

        # Generate summary using LLM
        try:
            summary_response = self.llm.invoke(
                summary_prompt.format(conversation=conversation_text)
            )
            summary = summary_response.content

            # Log escalation
            self._log_conversation(
                message_type="system",
                content=f"Escalated to human: {reason}",
                meta_data={"escalation_reason": reason, "summary": summary},
            )

            return f"Thank you for your patience. I've escalated your case to our specialist team. Summary of your case has been prepared for quick resolution."

        except Exception as e:
            self.logger.error(f"Failed to generate escalation summary: {e}")

            # Log escalation without summary
            self._log_conversation(
                message_type="system",
                content=f"Escalated to human: {reason}",
                meta_data={"escalation_reason": reason},
            )

            return "Thank you for your patience. I've connected you with a specialist who will assist you shortly."
