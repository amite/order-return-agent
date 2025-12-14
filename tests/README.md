# Test Suite Documentation

## Overview

The test suite for the order-return-agent project includes comprehensive tests for database operations, RAG functionality, and will eventually include tool tests, agent tests, and end-to-end scenario tests.

**Current Status**: 60 tests passing (31 database + 27 RAG + 2 basic)

---

## Quick Start

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Run Specific Test File
```bash
uv run pytest tests/test_database.py -v
uv run pytest tests/test_rag.py -v
```

### Run with Coverage
```bash
uv run pytest tests/test_database.py --cov=src/db --cov-report=term-missing
```

### Run Single Test
```bash
uv run pytest tests/test_database.py::TestSeededDatabase::test_seeded_db_has_prd_orders -v
```

---

## Test Files

### conftest.py (521 lines)
**Shared test fixtures and utilities**

#### Database Fixtures
- `test_db` - In-memory SQLite database for isolated testing
- `db_session` - SQLAlchemy session with automatic cleanup
- `seeded_db` - Pre-populated test database with customers, orders, items, policies, RMAs

#### Mock Fixtures
- `mock_ollama` - Mock Ollama LLM for deterministic tests
- `mock_rag` - Mock KnowledgeBase for agent tests

#### Session & ID Fixtures
- `test_session_id` - UUID for conversation tracking

#### Test Data Fixtures
- `sample_order_dict` - Sample order data
- `sample_item_dict` - Sample order item data
- `sample_rma_dict` - Sample RMA data
- `sample_conversation_log_dict` - Sample conversation log data

#### Utility Fixtures
- `temp_db_path` - Temporary database file path

---

### test_database.py (613 lines, 31 tests)
**Database layer tests**

#### Test Classes

**TestDatabaseConnection** (4 tests)
- Session creation and context manager functionality
- Commit and rollback behavior

**TestDatabaseSchema** (12 tests)
- All 6 tables created correctly
- Model creation and CRUD operations
- Relationships (Order↔Customer, Order↔Items, RMA↔Order, RMA↔Customer)
- Cascade deletes
- Unique constraints

**TestSeededDatabase** (14 tests)
- Seeded data verification
- PRD test case order validation (77893, 45110, 10552)
- Customer tier validation
- Data integrity checks
- Orphaned record detection

**TestDatabaseMigration** (1 test)
- Database reset functionality
- SQLAlchemy metadata validation

---

### test_rag.py (27 tests)
**RAG/Knowledge Base tests** (requires Ollama running)

Tests for:
- Knowledge base initialization
- Document loading and metadata
- Document chunking
- Vector store ingestion
- Semantic search and retrieval
- Policy context retrieval
- Communication templates
- Exception handling guidance
- Health checks

---

### test_basic.py (2 tests)
**Basic project structure tests**

- Project directory structure validation
- Placeholder test

---

## Seeded Test Data

### Test Database Contents

**Customers** (7 total)
```
john.doe@example.com         - Standard, no flags
jane.smith@example.com       - Standard, 1 return
bob.johnson@example.com      - Standard, no flags
gold.vip@example.com         - Gold tier
platinum.vip@example.com     - Platinum tier
fraud.user@example.com       - Fraud flag, 5 returns
high.returns@example.com     - Standard, 3 returns in 30 days
```

**Orders** (6 total)
```
Order 77893  - 5 days old, eligible, hiking boots ($129.99)
Order 45110  - 185 days old, expired window, jacket ($89.99)
Order 10552  - 10 days old, electronics, tablet ($499.99)
Order 12345  - 20 days old, final sale item, vinyl ($149.99)
Order 54321  - 50 days old, Gold VIP, smart watch ($299.99)
Order 99999  - 15 days old, multiple items, shirts + jeans
```

**Return Policies** (5 total)
```
General        - 30 days
Electronics    - 90 days
Clothing       - 30 days
Final Sale     - 0 days (non-returnable)
VIP Extended   - 120 days
```

---

## Using Fixtures in Tests

### Example 1: Test with Database Session
```python
def test_something(db_session):
    """Test with a database session"""
    customer = Customer(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        loyalty_tier=LoyaltyTier.STANDARD,
    )
    db_session.add(customer)
    db_session.commit()

    result = db_session.query(Customer).filter_by(email="test@example.com").first()
    assert result is not None
```

### Example 2: Test with Seeded Data
```python
def test_with_seed_data(seeded_db):
    """Test using pre-populated database"""
    order = seeded_db.query(Order).filter_by(order_number="77893").first()
    assert order is not None
    assert order.customer.email == "john.doe@example.com"
```

### Example 3: Test with Mock Ollama
```python
def test_with_mock_ollama(mock_ollama):
    """Test with mocked Ollama LLM"""
    # Ollama LLM is mocked and won't require actual connection
    # Tests run deterministically
```

### Example 4: Test with Session ID
```python
def test_conversation(seeded_db, test_session_id):
    """Test conversation logging"""
    log = ConversationLog(
        session_id=test_session_id,
        customer_id=1,
        message_type="user",
        content="Hello",
    )
    seeded_db.add(log)
    seeded_db.commit()

    result = seeded_db.query(ConversationLog).filter_by(session_id=test_session_id).first()
    assert result is not None
```

---

## Test Organization Patterns

### Class-Based Grouping
Tests are organized into classes by component:
```python
class TestDatabaseConnection:
    def test_get_session_returns_session(self):
        ...

class TestDatabaseSchema:
    def test_customer_model_creation(self):
        ...
```

### Naming Convention
```
test_{component}_{scenario}_{expected}

Examples:
- test_customer_model_creation()
- test_order_customer_relationship()
- test_seeded_db_order_77893_eligible()
```

### Fixture Scope
- **function**: Fresh database per test (default)
- **class**: Shared across class methods (advanced)
- **module**: Shared across file (rare)

---

## Coverage Goals

### Phase 4 Targets
- Database layer: 94% (currently achieved)
- Tools: 80% (to be implemented in Phase 4.3)
- Agent: 75% (to be implemented in Phase 4.4)
- End-to-end: 100% of scenarios (Phase 4.5)

### Overall Target
**>80% code coverage**

### Current Coverage
```
src/db/schema.py:    94%
src/db/connection.py: 47% (functions tested through fixtures)
src/db/seed.py:       0% (tested through fixtures)
```

---

## Running Tests in CI/CD

### GitHub Actions Example
```yaml
- name: Run tests
  run: uv run pytest tests/ --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### Pre-commit Hook
```bash
#!/bin/bash
uv run pytest tests/ -q
if [ $? -ne 0 ]; then
    echo "Tests failed!"
    exit 1
fi
```

---

## Common Issues & Solutions

### Issue: "Ollama connection error" in test_rag.py
**Solution**: Start Ollama before running RAG tests
```bash
cd /home/amite/code/docker/ollama-docker
docker compose up -d ollama
```

### Issue: "Database locked" error
**Solution**: Tests should be isolated. Check that fixtures are cleaning up properly.

### Issue: Tests are slow
**Solution**:
- Run only database tests: `uv run pytest tests/test_database.py`
- Skip RAG tests: `uv run pytest tests/ -k "not rag"`

### Issue: Fixture not found error
**Solution**: Ensure conftest.py is in the tests/ directory

---

## Next Steps

### Phase 4.3: Tool Tests (~36 tests)
- [x] Test infrastructure (conftest.py) ✓
- [x] Database tests (test_database.py) ✓
- [ ] Tool unit tests (test_tools.py)
  - GetOrderDetailsTool
  - CheckEligibilityTool
  - CreateRMATool
  - GenerateReturnLabelTool
  - SendEmailTool
  - EscalateToHumanTool

### Phase 4.4: Agent Tests (~12 tests)
- [ ] Agent initialization
- [ ] Conversation flow
- [ ] Session management
- [ ] Error handling
- [ ] Escalation workflow

### Phase 4.5: Scenario Tests (5 tests)
- [ ] Standard Return (Order 77893)
- [ ] Expired Window (Order 45110)
- [ ] Missing Order Details
- [ ] Damaged Item (Order 10552)
- [ ] Refund Status Check

---

## Test Maintenance

### Running Tests Locally
```bash
# Quick check (database only)
uv run pytest tests/test_database.py -q

# Full test suite
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### Adding New Tests
1. Create test function in appropriate file
2. Use descriptive names: `test_{component}_{scenario}_{expected}`
3. Add docstring explaining what is tested
4. Use existing fixtures from conftest.py
5. Keep tests isolated (no dependencies)

### Fixture Best Practices
- Use `seeded_db` fixture for database access
- Use `mock_ollama` for LLM tests (no Ollama required)
- Use `test_session_id` for conversation tracking
- Always clean up resources (fixtures handle this automatically)

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/faq/testing.html)
- [Project Implementation Plan](../plans/implementation-plan.md)
- [Phase 4 Testing Plan](../plans/phase-4-testing-plan.md)
