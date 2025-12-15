# Order Return Agent - Implementation Plan

## Executive Summary

This project implements an AI customer service agent for order returns using LangChain, Ollama (local LLM), RAG, and a mock database. Yesterday's work established the **complete foundation** - all infrastructure, tools, and data are ready. What remains is the **orchestration layer** to tie everything together into a working conversational agent.

---

## What Has Been Completed ✅

### 1. **Database Layer (100% Complete)**
- **Schema**: 6 tables (Customer, Order, OrderItem, ReturnPolicy, RMA, ConversationLog)
- **Connection**: SQLite with SQLAlchemy ORM at `/data/order_return.db`
- **Seed Data**: 20 customers, 53 orders, 5 policies, 3 completed RMAs
- **Test Cases**: All PRD example orders included (77893, 45110, 10552)
- Files: [src/db/schema.py], [src/db/connection.py], [src/db/seed.py]

### 2. **Data Models (100% Complete)**
- **Enums**: 7 enums covering all business states (LoyaltyTier, OrderStatus, EligibilityReasonCode, etc.)
- **Schemas**: Pydantic input/output models for all 6 tools with validation
- Files: [src/models/enums.py], [src/models/schemas.py]

### 3. **Tool Implementations (100% Complete - 6 Tools)**
All tools are **fully functional** and **deterministic** (no LLM decision-making):

1. **GetOrderDetails** - Lookup by order# or email, returns order history
2. **CheckEligibility** - **Critical**: Implements all PRD business rules
   - Damaged item detection → DAMAGED_MANUAL
   - Fraud flag check → RISK_MANUAL
   - High return count (3+ in 30 days) → RISK_MANUAL
   - Final sale check → ITEM_EXCL
   - Return window validation → TIME_EXP
   - VIP policy for Gold/Platinum members
3. **CreateRMA** - Generates RMA number, calculates refund, updates DB
4. **GenerateReturnLabel** - Creates tracking# and label URL, updates RMA
5. **SendEmail** - 3 Jinja2 templates (approved, rejected, label_ready)
6. **EscalateToHuman** - Creates escalation ticket, retrieves conversation history

Files: [src/tools/order_tools.py], [src/tools/eligibility_tools.py], [src/tools/rma_tools.py], [src/tools/logistics_tools.py], [src/tools/email_tools.py], [src/tools/escalation_tools.py], [src/tools/base.py]

### 4. **Configuration & Prompts (100% Complete)**
- **Settings**: Comprehensive config using Pydantic with environment variables
  - Ollama settings (qwen2.5:3b for chat, mxbai-embed-large for embeddings)
  - Database, ChromaDB, RAG parameters
  - Agent parameters (temperature, max iterations, timeouts)
- **System Prompt**: Detailed agent instructions with 7-step conversation flow
- **Templates**: RAG query and escalation summary prompts
- Files: [src/config/settings.py], [src/config/prompts.py]

### 5. **Knowledge Base (100% Complete)**
4 comprehensive markdown documents ready for RAG ingestion:
1. **return_policy.md** - All return policies (Standard, Electronics, VIP Extended, etc.)
2. **exception_handling.md** - Edge cases, fraud prevention, compassionate circumstances
3. **communication_templates.md** - 15+ situational response templates
4. **troubleshooting_guide.md** - Agent debugging, error recovery, QA checklists

Files: [data/knowledge_base/*.md]

### 6. **Environment Configuration**
- **.env** exists with all necessary settings
- Ollama configured for local LLM usage
- Database paths set
- ChromaDB directory configured

---

## What Needs To Be Built 🔨

### **PHASE 1: RAG Implementation** (High Priority)
**Goal**: Enable the agent to retrieve policy information and personalized context

**Implementation**: [src/rag/knowledge_base.py]
```python
class KnowledgeBase:
    - __init__(): Initialize ChromaDB, load settings
    - ingest_documents(): Load markdown files from data/knowledge_base/
    - chunk_documents(): Split using RecursiveCharacterTextSplitter
    - create_embeddings(): Use OllamaEmbeddings with mxbai-embed-large
    - store_vectors(): Persist to ChromaDB collection
    - query(query: str, top_k: int): Retrieve relevant documents
    - get_policy_context(reason_code: str): Get specific policy explanations
```

**Key Requirements**:
- Use ChromaDB with Ollama embeddings (mxbai-embed-large)
- Chunk size: 500, overlap: 50 (from settings)
- Collection name: "order_return_policies"
- Similarity threshold: 0.7
- Top K: 3 results

**Use Cases**:
1. Policy explanations when eligibility check fails
2. Edge case handling guidance
3. Communication templates for responses
4. Troubleshooting for complex scenarios

---

### **PHASE 2: Agent Orchestration** (Critical Path)
**Goal**: Create the conversational agent that uses tools and RAG

**Implementation**: [src/agents/return_agent.py]
```python
class ReturnAgent:
    - __init__(): Initialize LLM, tools, RAG, session
    - create_agent(): Build LangChain agent with tool calling
    - run(user_input: str): Execute agent loop
    - _log_conversation(): Store in ConversationLog table
    - _format_response(): Clean up agent output
    - _handle_tool_errors(): Retry logic and fallbacks
```

**Agent Architecture**:
- **LLM**: Ollama with qwen2.5:3b model
- **Tools**: All 6 tools registered as LangChain tools
- **Memory**: ConversationBufferMemory for session context
- **RAG Integration**: Query knowledge base for policy context
- **System Prompt**: Use AGENT_SYSTEM_PROMPT from config

**Conversation Flow** (from PRD):
1. Greet customer and request Order ID or email
2. Execute GetOrderDetails tool
3. Verify order details with customer
4. Ask which item and return reason
5. Execute CheckEligibility tool
6. If approved: CreateRMA → GenerateReturnLabel → SendEmail
7. If rejected: Query RAG for policy explanation → SendEmail
8. If escalation needed: EscalateToHuman

---

### **PHASE 3: Main Application** (User Interface)
**Goal**: Create interactive CLI for testing the agent

**Implementation**: [src/main.py]
```python
def main():
    - Initialize database (seed if needed)
    - Initialize RAG (ingest documents if first run)
    - Create ReturnAgent instance
    - Start interactive chat loop
    - Handle user input/output
    - Graceful shutdown
```

**CLI Features**:
- Welcome message with instructions
- Session ID generation
- Multi-turn conversation support
- Commands: /exit, /reset, /help
- Pretty-print agent responses
- Error handling and recovery

---

### **PHASE 4: Testing & Validation** (Quality Assurance)
**Goal**: Ensure all components work correctly

**Implementation**: Create comprehensive test suite

**Test Files**:
1. [tests/test_tools.py] - Unit tests for all 6 tools
2. [tests/test_rag.py] - RAG ingestion and retrieval tests
3. [tests/test_agent.py] - End-to-end conversation tests
4. [tests/test_database.py] - Database operations tests

**Test Scenarios** (from PRD examples):
1. **Standard Return** (Order 77893) - Happy path
2. **Expired Window** (Order 45110) - Policy enforcement
3. **Missing Order Details** - Lookup by email
4. **Damaged Item** (Order 10552) - Escalation trigger
5. **Refund Status Check** - RMA lookup

---

## Implementation Order (Recommended)

### Step 1: RAG Module
- Create `src/rag/knowledge_base.py`
- Implement document ingestion
- Test with sample queries
- **Why first**: Agent needs RAG for policy explanations

### Step 2: Agent Orchestration
- Create `src/agents/return_agent.py`
- Initialize LangChain agent with tools + RAG
- Implement conversation loop
- **Why second**: Core business logic

### Step 3: Main Application
- Update `src/main.py`
- Create CLI interface
- Add database initialization
- **Why third**: User-facing entry point

### Step 4: Testing
- Write unit tests for tools
- Write integration tests for agent
- Test all PRD scenarios
- **Why last**: Validate everything works

---

## Critical Files to Create/Modify

### New Files:
1. `src/rag/knowledge_base.py` - RAG implementation
2. `src/agents/return_agent.py` - Agent orchestration
3. `tests/test_tools.py` - Tool unit tests
4. `tests/test_rag.py` - RAG tests
5. `tests/test_agent.py` - Agent integration tests
6. `tests/test_database.py` - Database tests

### Files to Modify:
1. `src/main.py` - Replace "Hello World" with interactive CLI

---

## Technical Dependencies

### Already Installed ✅:
- langchain, langchain-community, langchain-core, langchain-ollama
- chromadb (vector database)
- sqlalchemy (ORM)
- pydantic (validation)
- jinja2 (templates)
- loguru (logging)
- pytest, pytest-cov (testing)

### External Requirements:
- **Ollama** must be running locally via Docker with:
  - `qwen2.5:3b` model (chat)
  - `mxbai-embed-large` model (embeddings)

**IMPORTANT - Ollama Commands**:
All Ollama commands must be executed from `/home/amite/code/docker/ollama-docker/` directory:
```bash
# Check available models
cd /home/amite/code/docker/ollama-docker/ && docker compose exec ollama ollama list

# Pull a model
cd /home/amite/code/docker/ollama-docker/ && docker compose exec ollama ollama pull qwen2.5:3b

# Check Ollama status
cd /home/amite/code/docker/ollama-docker/ && docker compose ps
```

---

## Success Criteria

The project is complete when:
1. ✅ User can start the agent with `uv run python -m src.main`
2. ✅ Agent successfully handles all 5 PRD test scenarios
3. ✅ RAG retrieves relevant policy context
4. ✅ All tools execute correctly and log to database
5. ✅ Conversation history is persisted
6. ✅ Tests pass with >80% coverage
7. ✅ Agent follows the 7-step conversation flow
8. ✅ Escalations trigger correctly for edge cases

---

## Risk Mitigation

### Risk 1: LLM Hallucinations
- **Mitigation**: All business logic in deterministic tools, not LLM
- **Verification**: CheckEligibility returns ONLY hard-coded rules

### Risk 2: Ollama Model Performance
- **Mitigation**: Use lightweight model (qwen2.5:3b) with clear prompts
- **Fallback**: Can swap to larger model (7b) if needed

### Risk 3: RAG Relevance
- **Mitigation**: Test similarity thresholds, adjust chunk size if needed
- **Verification**: Manual review of retrieval results

---

## Next Actions

**Ready to implement in this order:**
1. Build RAG module (30 min)
2. Build agent orchestration (45 min)
3. Update main.py CLI (20 min)
4. Write comprehensive tests (30 min)
5. End-to-end testing with PRD scenarios (15 min)

**Total estimated time**: ~2.5 hours

**Starting point**: Create `src/rag/knowledge_base.py` with ChromaDB integration
