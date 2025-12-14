# Phase 4.4: Agent Integration Tests - Implementation Plan

## Overview

Phase 4.4 focuses on comprehensive integration testing of the ReturnAgent orchestration layer. Building on the 100% passing tool unit tests (Phase 4.3), we'll test how the agent:
- Initializes with LLM, tools, RAG, and session management
- Orchestrates tools in proper order
- Manages conversation flow and logging
- Handles errors and edge cases
- Enforces business policies

**Target**: ~12 integration tests covering agent behavior, conversation flow, and error scenarios
**Expected Coverage**: Agent orchestration layer with focus on interaction between components

---

## Architecture Context

### Agent Component Stack

```
ReturnAgent
├─ Session Management
│  ├─ session_id (UUID)
│  └─ ConversationLog persistence
├─ LLM Integration (ChatOllama)
│  ├─ llama3.1:8b-instruct-q4_K_M
│  ├─ Temperature: 0.0 (deterministic)
│  └─ Max iterations: 15
├─ Tool Orchestration (6 tools)
│  ├─ GetOrderDetailsTool
│  ├─ CheckEligibilityTool
│  ├─ CreateRMATool
│  ├─ GenerateReturnLabelTool
│  ├─ SendEmailTool
│  └─ EscalateToHumanTool
├─ RAG Integration (KnowledgeBase)
│  ├─ ChromaDB + OllamaEmbeddings
│  └─ Knowledge base retrieval
└─ Error Handling
   └─ Tool errors → Escalation
```

### Critical Integration Points

1. **Agent Initialization** - All components (LLM, tools, RAG, session) ready
2. **Tool Invocation** - Agent → LLM → Tool → Database → Response
3. **Conversation Logging** - Each message logged with type/metadata
4. **Session Persistence** - History retrievable via session_id
5. **Error Escalation** - Tool failures → Escalation tool
6. **State Updates** - Database modifications verified after tool calls

---

## Test Design

### Test File Structure

**File**: `tests/test_agent.py` (~500 lines)

**Test Classes**:
1. `TestAgentInitialization` - 3 tests
2. `TestConversationFlow` - 5 tests
3. `TestErrorHandling` - 3 tests
4. `TestSessionManagement` - 2 tests

**Total**: 13 integration tests covering agent behavior with real tools and mocked LLM

---

## Detailed Test Cases

### Test Class 1: Agent Initialization (3 tests)

#### Test 1.1: `test_agent_initialization_with_session_id`

**Purpose**: Verify agent initializes with all components ready

**Setup**:
- Create ReturnAgent with explicit session_id (UUID)

**Verification**:
1. Agent object created successfully
2. session_id stored correctly
3. LLM initialized (ChatOllama)
4. 6 tools registered and accessible:
   - GetOrderDetailsTool
   - CheckEligibilityTool
   - CreateRMATool
   - GenerateReturnLabelTool
   - SendEmailTool
   - EscalateToHumanTool
5. RAG knowledge base initialized
6. Agent executor ready (agent_executor exists)

**Expected**:
```
✓ Agent initialized with session_id
✓ All 6 tools registered
✓ LLM ready
✓ RAG health check passed
✓ Agent executor ready
```

#### Test 1.2: `test_agent_initializes_without_session_id`

**Purpose**: Verify agent generates session_id if not provided

**Setup**:
- Create ReturnAgent without session_id argument

**Verification**:
1. Agent initializes successfully
2. session_id auto-generated (not None, is UUID-like)
3. All components initialized

**Expected**:
```
✓ Agent generates session_id if not provided
✓ Components initialized correctly
```

#### Test 1.3: `test_agent_rag_health_check`

**Purpose**: Verify RAG initialization and health check

**Setup**:
- Create ReturnAgent
- Monitor health check flow

**Verification**:
1. RAG knowledge base created
2. ChromaDB connection verified
3. Health check passes or triggers ingestion

**Expected**:
```
✓ RAG knowledge base initialized
✓ Health check successful
```

---

### Test Class 2: Conversation Flow (5 tests)

#### Test 2.1: `test_agent_greeting_and_initial_message`

**Purpose**: Verify agent responds to initial user message

**Setup**:
- Create agent with session_id
- Mock LLM to return greeting asking for order ID
- User message: "Hi, I need to return an item"

**Verification**:
1. Agent processes message via LLM
2. Returns response asking for order information
3. ConversationLog entries created:
   - User message logged
   - Assistant response logged
4. Message types correct (USER, ASSISTANT)
5. Session ID persisted in logs

**Expected**:
```
✓ Agent responds with greeting
✓ Asks for order_id or email
✓ Messages logged with correct types
✓ Session ID consistent
```

#### Test 2.2: `test_agent_order_lookup_flow`

**Purpose**: Verify agent calls GetOrderDetailsTool correctly

**Setup**:
- Agent initialized with seeded database (Order 77893)
- Mock LLM to:
  - First message: ask for order details
  - Second message: call GetOrderDetailsTool with order_id="77893"
  - Final message: confirm order found, ask for items to return

**Flow**:
1. User: "I want to return my order"
2. Agent: "What's your order number?"
3. User: "77893"
4. Agent: Calls GetOrderDetailsTool
5. Agent: "Found order 77893 for john.doe@example.com. Which items?"

**Verification**:
1. GetOrderDetailsTool invoked
2. Order 77893 retrieved successfully
3. Order details include items and customer
4. Tool response logged with metadata
5. Conversation history includes all messages

**Expected**:
```
✓ Order lookup tool called
✓ Order 77893 retrieved
✓ Items included in response
✓ Tool result logged to database
✓ Conversation history complete
```

#### Test 2.3: `test_agent_eligibility_check_flow`

**Purpose**: Verify agent calls CheckEligibilityTool and validates returns

**Setup**:
- Agent with session_id
- Mock LLM to:
  1. Call GetOrderDetailsTool (Order 77893)
  2. Call CheckEligibilityTool with item_ids and reason
  3. Respond with eligibility result

**Flow**:
1. User: "Order 77893, I want to return item 1 (wrong size)"
2. Agent: GetOrderDetailsTool("77893")
3. Agent: CheckEligibilityTool(order_id="77893", item_ids=[1], return_reason="wrong size")
4. Agent: "Return approved! RMA: RMA-..."

**Verification**:
1. CheckEligibilityTool called with correct params
2. Eligible=True for recent order
3. Reason code = APPROVED
4. Result includes policy_applied
5. All steps logged to ConversationLog

**Expected**:
```
✓ Eligibility tool invoked
✓ Returns: eligible=True, reason=APPROVED
✓ Policy applied correctly
✓ Conversation history shows decision
```

#### Test 2.4: `test_agent_rma_creation_flow`

**Purpose**: Verify complete approval flow: order lookup → eligibility → RMA → label → email

**Setup**:
- Agent with session_id and seeded_db
- Mock LLM orchestration:
  1. GetOrderDetailsTool
  2. CheckEligibilityTool → APPROVED
  3. CreateRMATool → RMA-123456-XXXX
  4. GenerateReturnLabelTool
  5. SendEmailTool

**Flow**:
```
User: "Return order 77893, item 1, wrong size"
Agent:
  1. GetOrderDetails(77893)
  2. CheckEligibility(77893, [1], "wrong size")
  3. CreateRMA(77893, customer_id=1, [1], "wrong size", APPROVED)
  4. GenerateLabel(77893, rma_number)
  5. SendEmail(john.doe@example.com, "return_approved", {...})
Response: "Return approved! Your RMA is [number]. Label sent to your email."
```

**Verification**:
1. GetOrderDetailsTool executed
2. CheckEligibilityTool executed, returned eligible=True
3. CreateRMATool executed:
   - RMA number generated (RMA-{ts}-{suffix})
   - RMA persisted to database
4. GenerateReturnLabelTool executed:
   - Tracking number generated
   - Label URL generated
   - RMA status updated to LABEL_SENT
5. SendEmailTool executed:
   - Template: "return_approved"
   - Message ID generated
   - Email logged to database
6. Database state verified:
   - Order status = RETURN_INITIATED
   - RMA created with correct fields
   - RMA status = LABEL_SENT
7. Conversation history complete with all messages and tool results

**Expected**:
```
✓ Full approval flow executed
✓ 5 tools called in sequence
✓ RMA created and stored
✓ Label generated
✓ Email sent
✓ Database state consistent
✓ Conversation history complete
```

#### Test 2.5: `test_agent_rejection_flow`

**Purpose**: Verify agent handles ineligible returns (expired window)

**Setup**:
- Agent with session_id
- Mock LLM:
  1. GetOrderDetailsTool(Order 45110, expired >30 days)
  2. CheckEligibilityTool → TIME_EXP (not eligible)
  3. SendEmailTool with rejection template

**Flow**:
```
User: "Return order 45110"
Agent:
  1. GetOrderDetails(45110)
  2. CheckEligibility(45110, [...], "...")
  3. SendEmail(..., "return_rejected", "Your return window has expired")
Response: "Unfortunately, we cannot process this return because..."
```

**Verification**:
1. GetOrderDetailsTool executed (Order 45110)
2. CheckEligibilityTool returned:
   - eligible=False
   - reason_code=TIME_EXP
   - days_since_order > 30
3. RMA NOT created
4. SendEmailTool called with "return_rejected" template
5. Email includes rejection reason
6. Order status NOT changed (no RMA)
7. Conversation includes rejection explanation

**Expected**:
```
✓ Ineligible return detected
✓ No RMA created
✓ Rejection email sent
✓ Order status unchanged
✓ Clear rejection reason provided
```

---

### Test Class 3: Error Handling & Escalation (3 tests)

#### Test 3.1: `test_agent_escalates_damaged_items`

**Purpose**: Verify agent escalates damaged/defective items

**Setup**:
- Agent with session_id
- Mock LLM:
  1. GetOrderDetailsTool
  2. CheckEligibilityTool returns:
     - eligible=False
     - reason_code=DAMAGED_MANUAL
     - requires_manual_review=True
  3. EscalateToHumanTool

**Flow**:
```
User: "Return order 77893, item arrived damaged"
Agent:
  1. GetOrderDetails(77893)
  2. CheckEligibility(77893, [...], "arrived damaged")
     → reason_code=DAMAGED_MANUAL
  3. EscalateToHuman(session_id, "Item reported as damaged - requires inspection")
Response: "I'm escalating this to our specialist team..."
```

**Verification**:
1. CheckEligibilityTool detected "damaged" keyword
2. Returned DAMAGED_MANUAL + requires_manual_review=True
3. EscalateToHumanTool called:
   - session_id provided
   - reason includes "damaged"
   - priority appropriate
4. Escalation logged:
   - ConversationLog entry with SYSTEM message
   - Meta data includes ticket_id
5. Ticket created with proper format
6. No RMA created (requires human review)
7. Summary includes conversation context

**Expected**:
```
✓ Damaged item detected
✓ Escalation triggered
✓ Ticket generated
✓ Specialist notified
✓ Summary includes context
✓ No RMA auto-created
```

#### Test 3.2: `test_agent_escalates_fraud_flag`

**Purpose**: Verify agent escalates fraud-flagged customers

**Setup**:
- Agent with session_id
- Use fraud.user customer (fraud_flag=True)
- Mock LLM:
  1. GetOrderDetailsTool
  2. CheckEligibilityTool returns:
     - eligible=False
     - reason_code=RISK_MANUAL
     - requires_manual_review=True
  3. EscalateToHumanTool

**Flow**:
```
User: "I need to return items"
Agent:
  1. GetOrderDetails (retrieves customer with fraud_flag=True)
  2. CheckEligibility → reason_code=RISK_MANUAL
  3. EscalateToHuman(reason="Fraud flag detected on account")
Response: "Thank you. A specialist will review your request..."
```

**Verification**:
1. GetOrderDetailsTool retrieved customer record
2. CheckEligibilityTool detected fraud_flag
3. Returned RISK_MANUAL + requires_manual_review=True
4. EscalateToHumanTool called with fraud reason
5. Escalation logged with URGENT priority recommended
6. Ticket summary includes fraud risk
7. RMA not created
8. Conversation logged

**Expected**:
```
✓ Fraud flag detected
✓ Escalation triggered
✓ High priority (URGENT) recommended
✓ Fraud context in summary
✓ No RMA created
```

#### Test 3.3: `test_agent_handles_tool_error_gracefully`

**Purpose**: Verify agent handles tool exceptions with escalation

**Setup**:
- Agent with session_id
- Mock GetOrderDetailsTool to raise exception (database error)
- Mock LLM to call GetOrderDetailsTool

**Flow**:
```
User: "Return order 77893"
Agent:
  1. GetOrderDetailsTool() → Exception
  2. Catch exception
  3. Log error to ConversationLog
  4. Respond with friendly message
  5. Offer escalation
```

**Verification**:
1. Tool exception caught
2. ConversationLog entry with error details
3. Meta data includes error type
4. User receives friendly message (not stack trace)
5. Escalation offered to user
6. Error logged via loguru

**Expected**:
```
✓ Tool error caught gracefully
✓ Error logged to database
✓ User-friendly message returned
✓ No stack trace exposed
✓ Escalation option offered
```

---

### Test Class 4: Session Management (2 tests)

#### Test 4.1: `test_conversation_history_retrieval`

**Purpose**: Verify conversation history is stored and retrievable

**Setup**:
- Agent with session_id
- Mock LLM to create 3-turn conversation:
  1. User greeting
  2. Agent response
  3. User order question
  4. Agent tool call
  5. Agent response

**Verification**:
1. All messages logged to ConversationLog
2. get_conversation_history() returns all logs
3. Logs include:
   - message_type (USER, ASSISTANT, TOOL, SYSTEM)
   - content (message text)
   - created_at (timestamp)
   - meta_data (tool results, errors)
4. Logs ordered by created_at
5. All logs have same session_id

**Expected**:
```
✓ 5+ ConversationLog entries created
✓ Message types correct
✓ Content preserved
✓ Timestamps sequential
✓ Session ID consistent
✓ History retrievable via get_conversation_history()
```

#### Test 4.2: `test_multiple_sessions_isolated`

**Purpose**: Verify conversations in different sessions don't interfere

**Setup**:
- Create 2 agents with different session_ids
- Each agent executes a conversation:
  - Agent 1: Order 77893 return request
  - Agent 2: Order 45110 return request

**Verification**:
1. Both agents process independently
2. ConversationLog entries separate by session_id
3. get_conversation_history() for Agent 1 shows only Agent 1's logs
4. get_conversation_history() for Agent 2 shows only Agent 2's logs
5. No cross-contamination
6. Database queries filter by session_id correctly

**Expected**:
```
✓ Session 1 conversation isolated
✓ Session 2 conversation isolated
✓ History queries return correct data
✓ No message leakage between sessions
```

---

## Mocking Strategy

### What to Mock

1. **ChatOllama (LLM)**
   - Mock `.invoke()` to return predefined responses
   - Use `MagicMock` to capture tool calls
   - Return tool results without calling actual LLM
   - Provides deterministic test flow

2. **KnowledgeBase (RAG)**
   - Mock `.health_check()` to return True
   - Mock `.query()` if used in tests (optional)
   - Avoid actual ChromaDB operations

### What NOT to Mock

1. **Tool Implementations** - Use real tools (tested in Phase 4.3)
2. **Database** - Use seeded_db fixture (in-memory SQLite)
3. **Tools' Database Access** - Real get_db_session() calls
4. **Tool Orchestration** - Real agent execution flow

### Mock Implementation

```python
@pytest.fixture
def mock_ollama_chat(mocker):
    """Mock ChatOllama to return predetermined responses"""
    responses = []  # Queue of responses

    def invoke_side_effect(messages):
        response = responses.pop(0)
        return {"messages": [..., {"content": response}]}

    mock_chat = mocker.patch(
        "src.agents.return_agent.ChatOllama",
        return_value=mocker.MagicMock()
    )
    mock_chat.return_value.invoke = invoke_side_effect
    return mock_chat
```

---

## Test Data & Fixtures

### Reuse from conftest.py

- `seeded_db` - Database with 7 customers, 6+ orders
- `test_session_id` - UUID for conversation tracking
- Order fixtures: 77893, 45110, 10552 (with various statuses)
- Customer fixtures: john.doe (regular), fraud.user, high.returns

### New Fixtures Needed

1. `agent_with_session` - ReturnAgent with mocked LLM and session_id
2. `mock_ollama_chat` - Mocked ChatOllama responses
3. `mock_knowledge_base` - Mocked KnowledgeBase

---

## Implementation Checklist

- [ ] Create `tests/test_agent.py` file
- [ ] Implement TestAgentInitialization (3 tests)
- [ ] Implement TestConversationFlow (5 tests)
- [ ] Implement TestErrorHandling (3 tests)
- [ ] Implement TestSessionManagement (2 tests)
- [ ] Create mocking utilities and fixtures
- [ ] Run tests with pytest
- [ ] Verify all tests pass
- [ ] Check coverage (aim for >90% on agent code)
- [ ] Update documentation
- [ ] Create Phase 4.4 implementation summary

---

## Expected Test Results

**Target**: 13 passing tests

```
TestAgentInitialization:
  ✓ test_agent_initialization_with_session_id
  ✓ test_agent_initializes_without_session_id
  ✓ test_agent_rag_health_check

TestConversationFlow:
  ✓ test_agent_greeting_and_initial_message
  ✓ test_agent_order_lookup_flow
  ✓ test_agent_eligibility_check_flow
  ✓ test_agent_rma_creation_flow
  ✓ test_agent_rejection_flow

TestErrorHandling:
  ✓ test_agent_escalates_damaged_items
  ✓ test_agent_escalates_fraud_flag
  ✓ test_agent_handles_tool_error_gracefully

TestSessionManagement:
  ✓ test_conversation_history_retrieval
  ✓ test_multiple_sessions_isolated

Total: 13 passing
```

---

## Success Criteria

✅ **All 13 tests pass**
✅ **>90% coverage on agent orchestration layer**
✅ **Clear test output explaining each integration point**
✅ **Proper mocking of external dependencies (LLM, RAG)**
✅ **Real tool execution and database operations tested**
✅ **Error scenarios handled gracefully**
✅ **Session isolation verified**
✅ **Documentation complete**

---

## Next Phase Preview

### Phase 4.5: End-to-End Scenario Tests

After Phase 4.4 completes, Phase 4.5 will test complete user workflows:
- Scenario 1: Standard return (Order 77893 approved)
- Scenario 2: Expired window (Order 45110 rejected)
- Scenario 3: Multiple orders (customer lookup by email)
- Scenario 4: Damaged item (Order 10552 escalated)
- Scenario 5: Refund status check (existing RMA)

Each scenario will exercise full multi-turn conversation with mocked LLM.

---

## Timeline & Effort

**Estimated Implementation Time**: ~2 hours
- Setup & mocking utilities: 20 min
- TestAgentInitialization: 15 min
- TestConversationFlow: 45 min
- TestErrorHandling: 30 min
- TestSessionManagement: 20 min
- Testing & refinement: 15 min

**Total**: ~2.5 hours to complete Phase 4.4
