# Phase 4.5: End-to-End Scenario Tests - Implementation Plan

## Overview

Phase 4.5 implements comprehensive end-to-end scenario tests based on the 5 PRD examples. These tests validate complete user workflows from initial request through final resolution, testing multi-turn conversations with the ReturnAgent.

**Current Status**: Phase 4.4 complete with 13/13 agent integration tests passing (100%)

**Phase 4.5 Goal**: Implement 5 end-to-end scenario tests matching PRD examples

---

## What Makes Phase 4.5 Different from Phase 4.4

### Phase 4.4 (Agent Integration Tests) ✅ COMPLETE
- **Focus**: Individual agent capabilities and tool orchestration
- **Scope**: Single-turn or 2-turn conversations
- **Pattern**: Test one workflow at a time (order lookup, eligibility check, RMA creation)
- **Example**: `test_agent_order_lookup_flow()` - tests just the order lookup step

### Phase 4.5 (End-to-End Scenario Tests) ⏳ TO IMPLEMENT
- **Focus**: Complete user journeys from start to finish
- **Scope**: Multi-turn conversations (3-6 exchanges)
- **Pattern**: Test realistic customer interactions with complete context
- **Example**: `test_scenario_standard_eligible_return()` - full conversation from greeting → order lookup → eligibility → RMA → label → email

**Key Difference**: Phase 4.5 tests mirror the exact PRD scenarios, validating that the agent can handle realistic customer conversations end-to-end.

---

## 5 PRD Scenarios to Implement

Based on [prd.md](../../../prd.md#L218-L289), these are the 5 real-world scenarios:

### Scenario 1: Standard Eligible Return (Happy Path)
**PRD Reference**: Example 1 - Order #77893
- **User Query**: "I need to return the hiking boots I bought a few weeks ago, order #77893. They're just too small and I need to send them back for a refund."
- **Expected Flow**:
  1. GetOrderDetails(77893) → order found (15 days old)
  2. CheckEligibility → APPROVED (within 30-day window)
  3. CreateRMA → RMA number generated
  4. GenerateReturnLabel → label URL created
  5. SendEmail → confirmation sent
- **Validation**: All 5 tools called, RMA created, order status = RETURN_INITIATED

### Scenario 2: Ineligible Return - Expired Window
**PRD Reference**: Example 2 - Order #45110
- **User Query**: "I bought a jacket last summer and it's too big. I want to return it. The order number is #45110."
- **Expected Flow**:
  1. GetOrderDetails(45110) → order found (185 days old)
  2. CheckEligibility → TIME_EXP (outside 90-day window)
  3. Agent explains policy, rejection email sent
  4. NO RMA created
- **Validation**: Eligibility fails, no RMA, rejection handled gracefully

### Scenario 3: Missing Order Details - Email Lookup
**PRD Reference**: Example 3 - Multiple orders via email
- **User Query**: "I lost my receipt but I need to send back the toaster I bought. I think I used my email john.doe@example.com."
- **Expected Flow**:
  1. GetOrderDetails(email="john.doe@example.com") → multiple orders returned
  2. Agent asks user to clarify which order
  3. User selects order
  4. CheckEligibility → proceed with selected order
  5. RMA created if eligible
- **Validation**: Email lookup works, agent handles multiple orders, user clarification flow

### Scenario 4: Damaged Item - Escalation Required
**PRD Reference**: Example 4 - Order #10552
- **User Query**: "The package arrived totally ripped open and the electronics inside are shattered. Order #10552."
- **Expected Flow**:
  1. GetOrderDetails(10552) → order found
  2. CheckEligibility(reason="damaged") → DAMAGED_MANUAL
  3. EscalateToHuman → ticket created
  4. Agent explains escalation, provides ticket ID
- **Validation**: Damaged keyword detected, escalation triggered, no automatic RMA

### Scenario 5: Refund Status Check
**PRD Reference**: Example 5 - RMA status lookup
- **User Query**: "I sent my return back last week using RMA RMA-123456-ABCD. Has my refund been processed yet?"
- **Expected Flow**:
  1. Agent queries existing RMA status
  2. Returns tracking information and refund timeline
  3. Provides customer with status update
- **Validation**: RMA lookup works, status information returned

---

## Implementation Approach

### Test File Structure

**File**: `tests/test_scenarios.py` (~400-500 lines)

**Test Organization**:
```python
class TestEndToEndScenarios:
    """End-to-end PRD scenario tests"""

    def test_scenario_1_standard_eligible_return(self, seeded_db, test_session_id):
        """PRD Example 1: Standard return (Order 77893)"""

    def test_scenario_2_expired_window_rejection(self, seeded_db, test_session_id):
        """PRD Example 2: Expired window (Order 45110)"""

    def test_scenario_3_email_lookup_multiple_orders(self, seeded_db, test_session_id):
        """PRD Example 3: Email lookup with multiple orders"""

    def test_scenario_4_damaged_item_escalation(self, seeded_db, test_session_id):
        """PRD Example 4: Damaged item requiring escalation (Order 10552)"""

    def test_scenario_5_refund_status_check(self, seeded_db, test_session_id):
        """PRD Example 5: Check status of existing RMA"""
```

### Testing Strategy

Following Phase 4.4 proven patterns:

1. **Use Real Agent**: No mocking LLM, use actual ReturnAgent with Ollama
2. **Real Database**: Use `seeded_db` fixture with test data
3. **Multi-Turn Conversations**: Simulate realistic back-and-forth exchanges
4. **Database Validation**: Verify state changes after each scenario
5. **Graceful Handling**: Skip if required test data missing

### Test Pattern (from Phase 4.4)

```python
def test_scenario_1_standard_eligible_return(self, seeded_db, test_session_id):
    """PRD Example 1: Standard return flow"""
    # Arrange
    agent = ReturnAgent(session_id=test_session_id)

    # Act - Simulate user conversation
    response1 = agent.run(
        "I need to return the hiking boots I bought a few weeks ago, "
        "order #77893. They're just too small."
    )

    # Assert - Verify conversation response
    assert response1 is not None
    assert "77893" in str(response1).lower() or "rma" in str(response1).lower()

    # Verify database state
    with get_db_session() as session:
        order = session.query(Order).filter(Order.order_number == "77893").first()
        assert order is not None
        assert "return_initiated" in str(order.status).lower()

        rma = session.query(RMA).filter(RMA.order_id == order.id).first()
        assert rma is not None
        assert rma.rma_number is not None

    # Verify conversation history
    history = agent.get_conversation_history()
    assert len(history) >= 2  # User message + agent response
    user_messages = [msg for msg in history if msg["type"] == "user"]
    assert len(user_messages) >= 1
```

---

## Critical Files

### Files to Create
- **[tests/test_scenarios.py](../../../tests/test_scenarios.py)** - NEW (400-500 lines)
  - 5 test methods for PRD scenarios
  - Multi-turn conversation simulation
  - Database validation after each scenario

### Files to Reference
- **[tests/test_agent.py](../../../tests/test_agent.py)** - Phase 4.4 patterns
- **[tests/conftest.py](../../../tests/conftest.py)** - Shared fixtures (seeded_db, test_session_id)
- **[prd.md](../../../prd.md)** - PRD scenario definitions
- **[src/agents/return_agent.py](../../../src/agents/return_agent.py)** - Agent implementation
- **[src/db/schema.py](../../../src/db/schema.py)** - Database models

### Database Dependencies
- **Order 77893**: Recent order (15-20 days old) - for Scenario 1 ✅ EXISTS
- **Order 45110**: Old order (>90 days) - for Scenario 2 ✅ EXISTS
- **john.doe@example.com**: Customer with multiple orders - for Scenario 3 ✅ EXISTS
- **Order 10552**: Order for damaged item test - for Scenario 4 ✅ EXISTS
- **Existing RMA**: Pre-created RMA for status check - for Scenario 5 ✅ EXISTS (RMA4567, RMA4568, RMA4569)

---

## Test Implementation Details

### Scenario 1: Standard Eligible Return
**Test Name**: `test_scenario_1_standard_eligible_return`

**Steps**:
1. Create ReturnAgent with test session
2. Send user message with order 77893 and return reason
3. Agent should:
   - Call GetOrderDetailsTool(77893)
   - Call CheckEligibilityTool → APPROVED
   - Call CreateRMATool → RMA number
   - Call GenerateReturnLabelTool → label URL
   - Call SendEmailTool → confirmation
4. Verify database:
   - Order status = RETURN_INITIATED
   - RMA record created with valid RMA number
   - RMA status = LABEL_SENT
5. Verify conversation history logged

**Assertions**:
- Response includes RMA number or confirmation
- All 5 tools executed (check via database or logs)
- Database state matches expected

### Scenario 2: Expired Window Rejection
**Test Name**: `test_scenario_2_expired_window_rejection`

**Steps**:
1. Create ReturnAgent
2. Send message: "Order #45110, want to return jacket from last summer"
3. Agent should:
   - Call GetOrderDetailsTool(45110)
   - Call CheckEligibilityTool → TIME_EXP
   - Explain policy (may use RAG)
   - Send rejection email
4. Verify database:
   - Order status unchanged (not RETURN_INITIATED)
   - NO RMA created
   - Conversation logged with rejection

**Assertions**:
- Response explains time expiration
- No RMA in database for this order
- Order status unchanged

### Scenario 3: Email Lookup - Multiple Orders
**Test Name**: `test_scenario_3_email_lookup_multiple_orders`

**Steps**:
1. Create ReturnAgent
2. Send message: "Lost receipt, email john.doe@example.com, want to return toaster"
3. Agent should:
   - Call GetOrderDetailsTool(email="john.doe@example.com")
   - Return multiple orders
   - Ask user to clarify
4. Simulate user response selecting specific order
5. Agent continues with eligibility check
6. Verify correct order processed

**Assertions**:
- Email lookup returns multiple orders
- Agent requests clarification
- Correct order selected after user input

### Scenario 4: Damaged Item Escalation
**Test Name**: `test_scenario_4_damaged_item_escalation`

**Steps**:
1. Create ReturnAgent
2. Send message: "Package arrived ripped, electronics shattered, order #10552"
3. Agent should:
   - Call GetOrderDetailsTool(10552)
   - Call CheckEligibilityTool(reason="damaged") → DAMAGED_MANUAL
   - Call EscalateToHumanTool
   - Provide ticket number
4. Verify database:
   - NO automatic RMA created
   - Escalation ticket generated
   - Conversation logged

**Assertions**:
- "damaged" keyword detected
- Escalation triggered
- Ticket ID returned
- No RMA auto-created

### Scenario 5: Refund Status Check
**Test Name**: `test_scenario_5_refund_status_check`

**Steps**:
1. Pre-create RMA in database (setup)
2. Create ReturnAgent
3. Send message: "Check status of RMA RMA-123456-ABCD"
4. Agent should:
   - Query RMA by RMA number
   - Return status information
   - Provide tracking details if available
5. Verify response includes status

**Assertions**:
- RMA found by number
- Status information returned
- Response includes tracking or refund timeline

---

## Fixtures Required

### Existing Fixtures (from conftest.py)
- ✅ `seeded_db` - Database with test orders
- ✅ `test_session_id` - UUID for session tracking

### Potential New Fixtures
- `pre_created_rma` - RMA for Scenario 5 status check (may need to add to conftest.py)

---

## Success Criteria

### Test Metrics
- ✅ 5 end-to-end scenario tests implemented
- ✅ All 5 tests passing (100%)
- ✅ Each scenario matches PRD example
- ✅ Multi-turn conversations validated
- ✅ Database state verified after each scenario

### Code Quality
- ✅ Clear test names matching PRD examples
- ✅ Comprehensive assertions for each flow
- ✅ Proper use of fixtures from conftest.py
- ✅ Follows Phase 4.4 patterns (real agent, real DB)
- ✅ Graceful handling of missing test data

### Integration
- ✅ Tests run with `uv run pytest tests/test_scenarios.py -v`
- ✅ Full test suite remains 100% passing (119 + 5 = 124 tests)
- ✅ Test execution time acceptable (~40-50 seconds for all 5 scenarios)

---

## Implementation Steps

1. **Create test file**: `tests/test_scenarios.py`
2. **Import dependencies**: ReturnAgent, database models, fixtures
3. **Implement Scenario 1**: Standard eligible return (Order 77893)
4. **Implement Scenario 2**: Expired window rejection (Order 45110)
5. **Implement Scenario 3**: Email lookup with multiple orders
6. **Implement Scenario 4**: Damaged item escalation (Order 10552)
7. **Implement Scenario 5**: RMA status check
8. **Run tests**: Verify all 5 passing
9. **Verify full suite**: Ensure 124/124 tests passing
10. **Create implementation summary**: Document Phase 4.5 completion

---

## Expected Test Output

```bash
$ uv run pytest tests/test_scenarios.py -v

tests/test_scenarios.py::TestEndToEndScenarios::test_scenario_1_standard_eligible_return PASSED
tests/test_scenarios.py::TestEndToEndScenarios::test_scenario_2_expired_window_rejection PASSED
tests/test_scenarios.py::TestEndToEndScenarios::test_scenario_3_email_lookup_multiple_orders PASSED
tests/test_scenarios.py::TestEndToEndScenarios::test_scenario_4_damaged_item_escalation PASSED
tests/test_scenarios.py::TestEndToEndScenarios::test_scenario_5_refund_status_check PASSED

======================== 5 passed in 45.23s ========================
```

---

## Risk Mitigation

### Risk 1: Test Data Availability
- **Issue**: Required orders (77893, 45110, 10552) may not exist in seeded_db
- **Mitigation**: Use graceful pytest.skip() if data missing (Phase 4.4 pattern)
- **Verification**: ✅ All required orders verified to exist in seed.py

### Risk 2: Multi-Turn Conversation Complexity
- **Issue**: Simulating realistic multi-turn exchanges with real LLM may be unpredictable
- **Mitigation**: Focus on end state validation (database changes) rather than exact conversation content
- **Verification**: Assert on database state, not exact agent responses

### Risk 3: LLM Non-Determinism
- **Issue**: Real Ollama LLM may produce slightly different responses
- **Mitigation**: Use flexible assertions (check for keywords, not exact strings)
- **Example**: `assert "rma" in response.lower()` instead of `assert response == "Your RMA is..."`

### Risk 4: Test Execution Time
- **Issue**: 5 scenarios with real LLM may take 60+ seconds
- **Mitigation**: Acceptable for end-to-end tests (Phase 4.4 took 13 seconds for 13 tests)
- **Target**: <60 seconds for all 5 scenarios

---

## Next Phase Preview

After Phase 4.5 completes:

### Phase 5: Deployment Preparation
- API endpoint implementation
- CLI interface for agent interaction
- Performance optimization
- Production database configuration
- Monitoring and logging setup

---

## Estimated Effort

**Total Implementation Time**: ~90 minutes

- Setup test file structure: 10 min
- Scenario 1 (standard return): 15 min
- Scenario 2 (expired window): 15 min
- Scenario 3 (email lookup): 20 min
- Scenario 4 (damaged escalation): 15 min
- Scenario 5 (status check): 10 min
- Testing and refinement: 15 min

---

## Key Decisions

### Decision 1: Real LLM vs Mock LLM
**Decision**: Use real Ollama LLM (consistent with Phase 4.4)

**Rationale**:
- Phase 4.4 established this pattern successfully
- End-to-end tests should validate real agent behavior
- Mocking LLM for multi-turn conversations is complex
- Trade-off: slower tests (~60s) but higher confidence

### Decision 2: Conversation Simulation
**Decision**: Use simple agent.run() calls, not complex multi-turn simulation

**Rationale**:
- agent.run() handles full conversation context automatically
- Focus on database validation, not exact conversation flow
- Simpler test code, easier to maintain

### Decision 3: Test Data Strategy
**Decision**: Use existing seeded_db, add graceful skips if data missing

**Rationale**:
- Consistent with Phase 4.4 pattern
- No new fixtures needed (reuse conftest.py)
- Tests adaptable to different database states

---

## Notes

- Phase 4.4 achieved 100% passing (13/13 tests) using real LLM pattern
- Full test suite currently at 119/119 passing
- Target: 124/124 passing after Phase 4.5 (119 + 5 scenarios)
- This is the final testing phase before deployment preparation
- All 5 PRD test orders and pre-created RMAs verified to exist in seed data
