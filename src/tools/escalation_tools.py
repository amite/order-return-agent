"""Human escalation and handoff tools"""

import time
from typing import List

from langchain.tools import BaseTool
from loguru import logger
from pydantic import BaseModel

from src.db.connection import get_db_session
from src.db.schema import ConversationLog, RMA
from src.models.enums import EscalationPriority, MessageType
from src.models.schemas import EscalateToHumanInput, EscalateToHumanOutput


class EscalateToHumanTool(BaseTool):
    """
    Tool to escalate cases to human agents.

    Creates an escalation ticket and generates a handoff summary.
    """

    name: str = "EscalateToHuman"
    description: str = """
    Escalate a case to a human agent for manual review.

    Use this tool when:
    - Customer has fraud flag or high return count
    - Items are damaged/defective (require inspection)
    - Customer expresses frustration or dissatisfaction
    - Situation is too complex for automated handling
    - CheckEligibility returns requires_manual_review=True

    Input:
    - session_id: Conversation session ID (required)
    - reason: Reason for escalation (required)
    - priority: Priority level - LOW, MEDIUM, HIGH, URGENT (default: MEDIUM)

    Returns:
    - ticket_id: Unique escalation ticket ID
    - summary: Brief summary of the conversation for human agent
    - success: Boolean indicating success
    """

    args_schema: type[BaseModel] = EscalateToHumanInput

    def _generate_ticket_id(self) -> str:
        """Generate a unique escalation ticket ID"""
        return f"TICKET-{int(time.time())}-{hash(time.time()) % 10000}"

    def _generate_summary(self, conversation_logs: List[ConversationLog], reason: str) -> str:
        """
        Generate a handoff summary from conversation logs.

        In a full implementation, this would use RAG to create an intelligent summary.
        For now, we'll create a simple structured summary.
        """
        if not conversation_logs:
            return f"Escalation reason: {reason}. No conversation history available."

        # Extract key information
        user_messages = [log for log in conversation_logs if str(log.message_type) == MessageType.USER]
        tool_calls = [log for log in conversation_logs if str(log.message_type) == MessageType.TOOL]

        # Create summary
        summary_parts = []
        summary_parts.append(f"ESCALATION REASON: {reason}")
        summary_parts.append(f"\nCONVERSATION LENGTH: {len(conversation_logs)} messages")

        if user_messages:
            summary_parts.append(f"\nCUSTOMER REQUEST: {user_messages[0].content[:200]}")

        if tool_calls:
            summary_parts.append(f"\nACTIONS TAKEN: {len(tool_calls)} tool calls executed")

        # Recommend next steps based on reason
        if "fraud" in reason.lower() or "risk" in reason.lower():
            summary_parts.append("\nRECOMMENDED ACTION: Verify customer identity and review account history")
        elif "damaged" in reason.lower() or "defective" in reason.lower():
            summary_parts.append("\nRECOMMENDED ACTION: Request photos and initiate quality control inspection")
        else:
            summary_parts.append("\nRECOMMENDED ACTION: Review case details and provide personalized assistance")

        return " ".join(summary_parts)

    def _run(
        self,
        session_id: str,
        reason: str,
        priority: str = "MEDIUM",
    ) -> str:
        """Execute escalation"""
        try:
            # 1. Generate ticket ID
            ticket_id = self._generate_ticket_id()

            # 2. Retrieve conversation history
            with get_db_session() as session:
                conversation_logs = (
                    session.query(ConversationLog)
                    .filter(ConversationLog.session_id == session_id)
                    .order_by(ConversationLog.created_at)
                    .all()
                )

                # 3. Generate summary
                summary = self._generate_summary(conversation_logs, reason)

                # 4. Mark any related RMAs as escalated
                # Find RMAs mentioned in conversation meta_data
                for log in conversation_logs:
                    # Extract meta_data value (type checker sees Column, but runtime is str)
                    meta_data_value = getattr(log, 'meta_data', None)
                    if meta_data_value is not None:
                        meta_data_str = str(meta_data_value)
                        if "rma_number" in meta_data_str:
                            try:
                                import json
                                meta_data = json.loads(meta_data_str)
                                rma_number = meta_data.get("rma_number")
                                if rma_number:
                                    rma = session.query(RMA).filter(RMA.rma_number == rma_number).first()
                                    if rma is not None:
                                        # Type checker sees Column, but runtime is Python value
                                        setattr(rma, 'escalated', True)
                                        setattr(rma, 'escalation_reason', reason)
                            except:
                                pass

                # 5. Log escalation
                escalation_log = ConversationLog(
                    session_id=session_id,
                    message_type=MessageType.SYSTEM,
                    content=f"Case escalated to human agent. Ticket: {ticket_id}",
                    meta_data=f'{{"ticket_id": "{ticket_id}", "priority": "{priority}", "reason": "{reason}"}}',
                )
                session.add(escalation_log)
                session.commit()

            logger.info(f"Escalated session {session_id} to human agent. Ticket: {ticket_id}")
            logger.info(f"Escalation summary: {summary}")

            return EscalateToHumanOutput(
                success=True,
                ticket_id=ticket_id,
                summary=summary,
                message=f"Case escalated successfully. Ticket ID: {ticket_id}. A specialist will assist you shortly.",
            ).model_dump_json()

        except Exception as e:
            logger.error(f"Error escalating to human: {e}")
            return EscalateToHumanOutput(
                success=False,
                error=str(e),
                message="An error occurred while escalating your case. Please try again.",
            ).model_dump_json()

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented, falls back to sync)"""
        return self._run(*args, **kwargs)
