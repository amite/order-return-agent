# Phase 4: Testing & Validation - Implementation Plan

## Overview

This plan implements comprehensive testing for the order-return-agent project. Based on exploration, the project currently has **only RAG tests** (26 tests in test_rag.py). We need to add tests for:

- **6 Tools** (order, eligibility, RMA, logistics, email, escalation)
- **Database layer** (connection, schema, seed data)
- **Agent orchestration** (conversation flow, session management)
- **End-to-end workflows** (PRD test scenarios)

**Target Coverage**: >80% (per implementation-plan.md)

---

## Current State

### ✅ What Exists
- [tests/test_rag.py](tests/test_rag.py) - 26 comprehensive RAG tests
- [tests/test_basic.py](tests/test_basic.py) - 2 basic structure tests
- Test infrastructure: pytest, pytest-cov, pytest-asyncio, pytest-mock

### ❌ What's Missing
- No tool tests (6 tools untested)
- No database tests
- No agent integration tests
- No end-to-end scenario tests
- No conftest.py for shared fixtures
- No pytest configuration file

---

## Implementation Strategy

### Phase 4.1: Test Infrastructure Setup
**File**: [tests/conftest.py](tests/conftest.py) (NEW)

**Purpose**: Shared test fixtures and configuration

**Fixtures to Create**:
1. `test_db` - In-memory SQLite database for testing
2. `db_session` - Database session with automatic rollback
3. `seeded_db` - Database with test data loaded
4. `mock_ollama` - Mock Ollama LLM responses
5. `mock_rag` - Mock KnowledgeBase for agent tests
6. `test_session_id` - UUID for conversation tracking

**Key Features**:
- Isolated test database (not production db)
- Automatic cleanup after each test
- Reusable seed data fixtures
- Mock external dependencies (Ollama)

---

### Phase 4.2: Database Tests
**File**: [tests/test_database.py](tests/test_database.py) (NEW)

**Test Coverage**:

#### Connection Tests
- `test_database_initialization()` - Creates database file
- `test_get_db_session()` - Session context manager works
- `test_session_commit()` - Changes persist
- `test_session_rollback()` - Errors trigger rollback
- `test_reset_database()` - Drops and recreates schema

#### Schema Tests
- `test_customer_model_creation()` - Create customer record
- `test_order_relationships()` - Order → Customer, Order → OrderItems
- `test_rma_foreign_keys()` - RMA → Order, RMA → Customer
- `test_conversation_log_session_query()` - Query by session_id
- `test_return_policy_query()` - Query by category/tier

#### Seed Data Tests
- `test_seed_return_policies()` - 5 policies created
- `test_seed_customers()` - All loyalty tiers present
- `test_seed_orders()` - PRD test orders exist (77893, 45110, 10552)
- `test_seed_data_integrity()` - No orphaned records

**Critical Files Tested**:
- [src/db/connection.py](src/db/connection.py)
- [src/db/schema.py](src/db/schema.py)
- [src/db/seed.py](src/db/seed.py)

---

### Phase 4.3: Tool Unit Tests
**File**: [tests/test_tools.py](tests/test_tools.py) (NEW)

**Test Coverage** (6 tools × ~6 tests each = ~36 tests):

#### 1. GetOrderDetailsTool Tests
- `test_get_order_by_order_id()` - Returns single order
- `test_get_order_by_email()` - Returns order list
- `test_order_not_found()` - Returns error message
- `test_email_not_found()` - Returns empty list
- `test_missing_both_params()` - Validation error
- `test_joinedload_efficiency()` - Items/customer loaded

#### 2. CheckEligibilityTool Tests
- `test_eligibility_approved()` - Standard return window
- `test_eligibility_time_expired()` - Beyond 30 days
- `test_eligibility_item_excluded()` - Final sale item
- `test_eligibility_fraud_flag()` - RISK_MANUAL for fraud
- `test_eligibility_high_return_count()` - 3+ returns in 30 days
- `test_eligibility_damaged_keyword()` - DAMAGED_MANUAL detection
- `test_vip_extended_policy()` - Gold/Platinum 120-day window
- `test_category_specific_policy()` - Electronics 90-day window

#### 3. CreateRMATool Tests
- `test_create_rma_success()` - RMA created, order updated
- `test_rma_number_format()` - Matches RMA-{timestamp}-{suffix}
- `test_refund_calculation()` - Sum of item prices
- `test_order_status_update()` - Order → RETURN_INITIATED
- `test_items_json_serialization()` - item_ids stored correctly
- `test_order_not_found()` - Error handling

#### 4. GenerateReturnLabelTool Tests
- `test_generate_label_success()` - Label URL and tracking created
- `test_tracking_number_format()` - Matches {CARRIER}-{digits}
- `test_label_url_format()` - Valid URL
- `test_rma_status_update()` - RMA → LABEL_SENT
- `test_rma_not_found()` - Error handling

#### 5. SendEmailTool Tests
- `test_send_email_return_approved()` - Template renders
- `test_send_email_return_rejected()` - Template renders
- `test_send_email_label_ready()` - Template renders
- `test_message_id_generation()` - Unique MSG-{timestamp}
- `test_email_preview()` - First 200 chars returned
- `test_invalid_template()` - Error for unknown template
- `test_conversation_log_entry()` - Logged when session_id present

#### 6. EscalateToHumanTool Tests
- `test_escalate_generates_ticket()` - TICKET-{timestamp} format
- `test_escalate_summary_generation()` - Summary includes conversation
- `test_escalate_no_conversation()` - Works without logs
- `test_escalate_marks_rma()` - RMA status updated
- `test_escalate_priority_levels()` - LOW, MEDIUM, HIGH, URGENT
- `test_escalate_recommended_actions()` - Based on reason

**Critical Files Tested**:
- [src/tools/order_tools.py](src/tools/order_tools.py)
- [src/tools/eligibility_tools.py](src/tools/eligibility_tools.py)
- [src/tools/rma_tools.py](src/tools/rma_tools.py)
- [src/tools/logistics_tools.py](src/tools/logistics_tools.py)
- [src/tools/email_tools.py](src/tools/email_tools.py)
- [src/tools/escalation_tools.py](src/tools/escalation_tools.py)

---

### Phase 4.4: Agent Integration Tests
**File**: [tests/test_agent.py](tests/test_agent.py) (NEW)

**Test Coverage**:

#### Initialization Tests
- `test_agent_initialization()` - Agent created with session_id
- `test_agent_tools_loaded()` - All 6 tools registered
- `test_agent_rag_health_check()` - KnowledgeBase initialized
- `test_agent_ollama_connection()` - LLM available

#### Conversation Flow Tests
- `test_agent_greeting()` - First message asks for order ID
- `test_agent_order_lookup()` - Calls GetOrderDetailsTool
- `test_agent_eligibility_check()` - Calls CheckEligibilityTool
- `test_agent_rma_creation()` - Approved flow creates RMA
- `test_agent_label_generation()` - Label generated after RMA

#### Session Management Tests
- `test_conversation_logging()` - User/assistant messages logged
- `test_conversation_history_retrieval()` - get_conversation_history()
- `test_multiple_sessions_isolated()` - Different session_ids separate

#### Error Handling Tests
- `test_agent_tool_error_recovery()` - Graceful error messages
- `test_agent_invalid_input()` - Validation errors handled
- `test_agent_database_error()` - Database failures logged

#### Escalation Tests
- `test_agent_escalation()` - escalate() creates ticket
- `test_escalation_summary()` - Summary includes conversation
- `test_escalation_logs_to_db()` - ConversationLog entry created

**Critical Files Tested**:
- [src/agents/return_agent.py](src/agents/return_agent.py)

---

### Phase 4.5: End-to-End Scenario Tests
**File**: [tests/test_scenarios.py](tests/test_scenarios.py) (NEW)

**Test Coverage** (PRD examples from implementation-plan.md):

#### Scenario 1: Standard Return (Order 77893)
- Customer provides order 77893
- Item within return window
- Eligibility check passes
- RMA created successfully
- Label generated
- Email sent

#### Scenario 2: Expired Window (Order 45110)
- Customer provides order 45110
- Item beyond 30-day window
- Eligibility check fails (TIME_EXP)
- RAG provides policy explanation
- Rejection email sent

#### Scenario 3: Missing Order Details
- Customer provides email instead of order ID
- Multiple orders returned
- Agent asks which order
- Continues with selected order

#### Scenario 4: Damaged Item (Order 10552)
- Customer reports "damaged" in reason
- Eligibility check returns DAMAGED_MANUAL
- Case escalated to human
- Escalation ticket created

#### Scenario 5: Refund Status Check
- Customer asks about existing RMA
- Agent retrieves RMA status
- Provides tracking information

**Test Approach**:
- Use real database with seed data
- Mock Ollama LLM responses for predictable flow
- Validate multi-turn conversations
- Check database state after workflow

---

## Testing Patterns

### Fixture Usage (from test_rag.py patterns)

```python
@pytest.fixture
def test_db():
    """Create in-memory test database"""
    # Create temp db, init schema, yield session, cleanup

@pytest.fixture
def seeded_db(test_db):
    """Database with seed data loaded"""
    # Run seed functions, yield session

@pytest.fixture
def mock_ollama(mocker):
    """Mock Ollama LLM responses"""
    # Mock ChatOllama.invoke() for deterministic tests
```

### Test Organization

- **Class-based grouping**: Group related tests by component
- **Descriptive names**: `test_{component}_{scenario}_{expected}`
- **Arrange-Act-Assert**: Clear test structure
- **Edge cases**: Test boundaries, empty inputs, errors

### Mocking Strategy

**Mock Ollama for**:
- Agent conversation tests (deterministic LLM responses)
- Tool tests that don't need LLM (GetOrderDetails, CreateRMA, etc.)

**Use real components for**:
- Database operations (test database)
- RAG retrieval (ChromaDB with test collection)
- Tool business logic (eligibility rules)

---

## Success Criteria

### Test Metrics
- [ ] >80% code coverage overall
- [ ] 100% coverage for critical business logic (CheckEligibility)
- [ ] All 6 tools have comprehensive unit tests
- [ ] Agent conversation flow tested
- [ ] All 5 PRD scenarios pass

### Test Organization
- [ ] conftest.py with shared fixtures
- [ ] Clear test file organization
- [ ] Fast test execution (<30 seconds for unit tests)
- [ ] Isolated tests (no dependencies between tests)

### Documentation
- [ ] Each test has clear docstring
- [ ] Test output is readable
- [ ] Failures provide actionable error messages

---

## Implementation Order

1. **conftest.py** - Shared fixtures first (foundation for all tests)
2. **test_database.py** - Database layer tests (tools depend on this)
3. **test_tools.py** - Tool unit tests (agent depends on these)
4. **test_agent.py** - Agent integration tests (end-to-end depends on this)
5. **test_scenarios.py** - End-to-end PRD scenarios (final validation)

---

## Files to Create

### New Test Files
1. [tests/conftest.py](tests/conftest.py)
2. [tests/test_database.py](tests/test_database.py)
3. [tests/test_tools.py](tests/test_tools.py)
4. [tests/test_agent.py](tests/test_agent.py)
5. [tests/test_scenarios.py](tests/test_scenarios.py)

### Optional Configuration
- [pytest.ini](pytest.ini) or [pyproject.toml](pyproject.toml) updates for pytest config
- [.coveragerc](.coveragerc) for coverage configuration

---

## Estimated Effort

- **conftest.py**: 20 minutes (6 fixtures)
- **test_database.py**: 30 minutes (~15 tests)
- **test_tools.py**: 60 minutes (~36 tests for 6 tools)
- **test_agent.py**: 40 minutes (~12 tests)
- **test_scenarios.py**: 30 minutes (5 PRD scenarios)

**Total**: ~3 hours

---

## Risk Mitigation

### Risk 1: Test Database Conflicts
- **Solution**: Use in-memory SQLite or temp file per test
- **Verification**: Tests can run in parallel without conflicts

### Risk 2: Ollama Dependency
- **Solution**: Mock all Ollama calls in unit tests
- **Verification**: Tests run without Ollama running

### Risk 3: Slow Test Execution
- **Solution**: Mock external services, use small test datasets
- **Verification**: Unit tests complete in <30 seconds

### Risk 4: Flaky Tests
- **Solution**: Deterministic mocks, clean fixtures, no time-dependent logic
- **Verification**: Tests pass consistently

---

## Post-Implementation Validation

After all tests are written:

1. **Run full test suite**:
   ```bash
   uv run pytest -v
   ```

2. **Check coverage**:
   ```bash
   uv run pytest --cov=src --cov-report=term-missing
   ```

3. **Validate PRD scenarios**:
   ```bash
   uv run pytest tests/test_scenarios.py -v
   ```

4. **Run specific test files**:
   ```bash
   uv run pytest tests/test_tools.py -v
   uv run pytest tests/test_agent.py -v
   ```

5. **Coverage target**:
   - Aim for >80% overall
   - Critical paths (CheckEligibility, CreateRMA) should be 100%
