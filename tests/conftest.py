"""Shared pytest fixtures for all tests"""

import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.schema import (
    Base,
    ConversationLog,
    Customer,
    Order,
    OrderItem,
    ReturnPolicy,
    RMA,
)
from src.models.enums import LoyaltyTier, OrderStatus, ProductCategory, RMAStatus


# ========================
# Database Fixtures
# ========================


@pytest.fixture(scope="function")
def test_db():
    """
    Create an in-memory SQLite test database.

    Each test gets an isolated database to prevent conflicts.
    Database is automatically cleaned up after the test.
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session factory
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield engine, TestSessionLocal

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db):
    """
    Create a database session with automatic rollback after test.

    Provides a Session instance with automatic cleanup.
    Changes are committed within the test but rolled back after.
    """
    engine, TestSessionLocal = test_db
    session = TestSessionLocal()

    yield session

    # Rollback any uncommitted changes
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def seeded_db(db_session):
    """
    Create a test database with seed data loaded.

    Provides sample customers, orders, items, policies, and RMAs for testing.
    All data is isolated to this test.
    """
    # Seed return policies
    policies = [
        ReturnPolicy(
            policy_name="General Return Policy",
            category="General",
            return_window_days=30,
            requires_original_packaging=False,
            restocking_fee_percent=Decimal("0"),
            conditions="Standard 30-day return policy for most items",
            is_active=True,
        ),
        ReturnPolicy(
            policy_name="Electronics Return Policy",
            category="Electronics",
            return_window_days=90,
            requires_original_packaging=True,
            restocking_fee_percent=Decimal("15.0"),
            conditions="90-day return window with 15% restocking fee. Original packaging required.",
            is_active=True,
        ),
        ReturnPolicy(
            policy_name="Clothing Return Policy",
            category="Clothing",
            return_window_days=30,
            requires_original_packaging=False,
            restocking_fee_percent=Decimal("0"),
            conditions="30-day return policy for clothing. Tags must be attached.",
            is_active=True,
        ),
        ReturnPolicy(
            policy_name="Final Sale - No Returns",
            category="Final Sale",
            return_window_days=0,
            requires_original_packaging=False,
            restocking_fee_percent=Decimal("0"),
            conditions="Final sale items are non-returnable and non-refundable",
            is_active=True,
        ),
        ReturnPolicy(
            policy_name="VIP Extended Return Policy",
            category="VIP Extended",
            return_window_days=120,
            requires_original_packaging=False,
            restocking_fee_percent=Decimal("0"),
            conditions="Extended 120-day return window for Gold and Platinum tier customers",
            is_active=True,
        ),
    ]
    db_session.add_all(policies)
    db_session.flush()

    # Seed customers
    customers = [
        Customer(
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-0101",
            loyalty_tier=LoyaltyTier.STANDARD,
            fraud_flag=False,
            return_count_30d=0,
        ),
        Customer(
            email="jane.smith@example.com",
            first_name="Jane",
            last_name="Smith",
            phone="555-0102",
            loyalty_tier=LoyaltyTier.STANDARD,
            fraud_flag=False,
            return_count_30d=1,
        ),
        Customer(
            email="bob.johnson@example.com",
            first_name="Bob",
            last_name="Johnson",
            phone="555-0103",
            loyalty_tier=LoyaltyTier.STANDARD,
            fraud_flag=False,
            return_count_30d=0,
        ),
        Customer(
            email="gold.vip@example.com",
            first_name="Gold",
            last_name="VIP",
            phone="555-0104",
            loyalty_tier=LoyaltyTier.GOLD,
            fraud_flag=False,
            return_count_30d=0,
        ),
        Customer(
            email="platinum.vip@example.com",
            first_name="Platinum",
            last_name="VIP",
            phone="555-0105",
            loyalty_tier=LoyaltyTier.PLATINUM,
            fraud_flag=False,
            return_count_30d=0,
        ),
        Customer(
            email="fraud.user@example.com",
            first_name="Fraud",
            last_name="User",
            phone="555-0106",
            loyalty_tier=LoyaltyTier.STANDARD,
            fraud_flag=True,
            return_count_30d=5,
        ),
        Customer(
            email="high.returns@example.com",
            first_name="High",
            last_name="Returns",
            phone="555-0107",
            loyalty_tier=LoyaltyTier.STANDARD,
            fraud_flag=False,
            return_count_30d=3,
        ),
    ]
    db_session.add_all(customers)
    db_session.flush()

    # Seed orders and items
    now = datetime.now()

    # Order 1: Recent, eligible (5 days ago)
    order_1 = Order(
        order_number="77893",
        customer_id=customers[0].id,
        order_date=now - timedelta(days=5),
        total_amount=Decimal("129.99"),
        status=OrderStatus.DELIVERED,
        shipping_address="123 Main St, City, ST 12345",
    )
    db_session.add(order_1)
    db_session.flush()

    item_1 = OrderItem(
        order_id=order_1.id,
        product_name="Hiking Boots",
        product_category=ProductCategory.FOOTWEAR,
        sku="FOO-002",
        quantity=1,
        price=Decimal("129.99"),
        is_final_sale=False,
        is_returnable=True,
    )
    db_session.add(item_1)

    # Order 2: Expired window (185 days ago)
    order_2 = Order(
        order_number="45110",
        customer_id=customers[1].id,
        order_date=now - timedelta(days=185),
        total_amount=Decimal("89.99"),
        status=OrderStatus.DELIVERED,
        shipping_address="456 Oak Ave, Town, ST 67890",
    )
    db_session.add(order_2)
    db_session.flush()

    item_2 = OrderItem(
        order_id=order_2.id,
        product_name="Black Jacket",
        product_category=ProductCategory.CLOTHING,
        sku="CLO-003",
        quantity=1,
        price=Decimal("89.99"),
        is_final_sale=False,
        is_returnable=True,
    )
    db_session.add(item_2)

    # Order 3: Damaged item (10 days ago)
    order_3 = Order(
        order_number="10552",
        customer_id=customers[2].id,
        order_date=now - timedelta(days=10),
        total_amount=Decimal("499.99"),
        status=OrderStatus.DELIVERED,
        shipping_address="789 Pine Rd, Village, ST 13579",
    )
    db_session.add(order_3)
    db_session.flush()

    item_3 = OrderItem(
        order_id=order_3.id,
        product_name="Tablet",
        product_category=ProductCategory.ELECTRONICS,
        sku="ELE-004",
        quantity=1,
        price=Decimal("499.99"),
        is_final_sale=False,
        is_returnable=True,
    )
    db_session.add(item_3)

    # Order 4: Final sale item (20 days ago)
    order_4 = Order(
        order_number="12345",
        customer_id=customers[3].id,
        order_date=now - timedelta(days=20),
        total_amount=Decimal("149.99"),
        status=OrderStatus.DELIVERED,
        shipping_address="321 Elm St, Metro, ST 24680",
    )
    db_session.add(order_4)
    db_session.flush()

    item_4 = OrderItem(
        order_id=order_4.id,
        product_name="Limited Edition Vinyl",
        product_category=ProductCategory.SPECIAL_EDITION,
        sku="SPE-001",
        quantity=1,
        price=Decimal("149.99"),
        is_final_sale=True,
        is_returnable=False,
    )
    db_session.add(item_4)

    # Order 5: Gold VIP customer order (50 days ago - eligible for VIP policy)
    order_5 = Order(
        order_number="54321",
        customer_id=customers[3].id,
        order_date=now - timedelta(days=50),
        total_amount=Decimal("299.99"),
        status=OrderStatus.DELIVERED,
        shipping_address="321 Elm St, Metro, ST 24680",
    )
    db_session.add(order_5)
    db_session.flush()

    item_5 = OrderItem(
        order_id=order_5.id,
        product_name="Smart Watch",
        product_category=ProductCategory.ELECTRONICS,
        sku="ELE-001",
        quantity=1,
        price=Decimal("299.99"),
        is_final_sale=False,
        is_returnable=True,
    )
    db_session.add(item_5)

    # Order 6: Multiple items
    order_6 = Order(
        order_number="99999",
        customer_id=customers[0].id,
        order_date=now - timedelta(days=15),
        total_amount=Decimal("199.98"),
        status=OrderStatus.DELIVERED,
        shipping_address="123 Main St, City, ST 12345",
    )
    db_session.add(order_6)
    db_session.flush()

    item_6a = OrderItem(
        order_id=order_6.id,
        product_name="Red T-Shirt",
        product_category=ProductCategory.CLOTHING,
        sku="CLO-001",
        quantity=1,
        price=Decimal("29.99"),
        is_final_sale=False,
        is_returnable=True,
    )
    item_6b = OrderItem(
        order_id=order_6.id,
        product_name="Blue Jeans",
        product_category=ProductCategory.CLOTHING,
        sku="CLO-002",
        quantity=1,
        price=Decimal("59.99"),
        is_final_sale=False,
        is_returnable=True,
    )
    db_session.add_all([item_6a, item_6b])

    db_session.commit()

    yield db_session


# ========================
# Session and ID Fixtures
# ========================


@pytest.fixture
def test_session_id():
    """
    Create a unique session ID for conversation tracking.

    UUID format for session identification in tests.
    """
    return str(uuid.uuid4())


# ========================
# Mock Fixtures
# ========================


@pytest.fixture
def mock_ollama(mocker):
    """
    Mock Ollama LLM for deterministic testing.

    Mocks ChatOllama responses without requiring actual Ollama connection.
    Useful for agent and conversation tests.
    """
    mock_llm = Mock()
    mock_llm.invoke = Mock(
        return_value=Mock(content="Mock LLM response for testing")
    )
    return mocker.patch("src.agents.return_agent.ChatOllama", return_value=mock_llm)


@pytest.fixture
def mock_rag(mocker):
    """
    Mock KnowledgeBase/RAG for deterministic testing.

    Mocks RAG queries without requiring ChromaDB.
    Useful for agent tests that need RAG integration.
    """
    mock_kb = Mock()
    mock_kb.query = Mock(
        return_value=[
            Mock(
                page_content="Return policy allows returns within 30 days of purchase.",
                metadata={"source": "return_policy.md"},
            )
        ]
    )
    mock_kb.get_policy_context = Mock(
        return_value="Standard 30-day return policy applies."
    )
    mock_kb.get_communication_template = Mock(
        return_value="Dear customer, your return has been approved..."
    )
    mock_kb.get_exception_guidance = Mock(
        return_value="For damaged items, escalate to human review."
    )
    mock_kb.health_check = Mock(return_value=True)
    return mocker.patch("src.agents.return_agent.KnowledgeBase", return_value=mock_kb)


# ========================
# Utility Fixtures
# ========================


@pytest.fixture
def temp_db_path():
    """
    Create a temporary database file path for testing.

    Useful for tests that need a persistent (but temporary) database file.
    """
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_order_return.db"
    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()
    if Path(temp_dir).exists():
        Path(temp_dir).rmdir()


# ========================
# Fixtures for Common Test Data
# ========================


@pytest.fixture
def sample_order_dict():
    """Sample order data for testing GetOrderDetails responses."""
    return {
        "id": 1,
        "order_number": "77893",
        "customer_id": 1,
        "order_date": datetime.now() - timedelta(days=5),
        "total_amount": Decimal("129.99"),
        "status": OrderStatus.DELIVERED,
        "shipping_address": "123 Main St, City, ST 12345",
    }


@pytest.fixture
def sample_item_dict():
    """Sample order item data for testing."""
    return {
        "id": 1,
        "order_id": 1,
        "product_name": "Hiking Boots",
        "product_category": ProductCategory.FOOTWEAR,
        "sku": "FOO-002",
        "quantity": 1,
        "price": Decimal("129.99"),
        "is_final_sale": False,
        "is_returnable": True,
    }


@pytest.fixture
def sample_rma_dict():
    """Sample RMA data for testing."""
    return {
        "id": 1,
        "rma_number": "RMA-2025-01-01-ABC123",
        "order_id": 1,
        "customer_id": 1,
        "return_reason": "Item is damaged",
        "reason_code": "DAMAGED_MANUAL",
        "status": RMAStatus.INITIATED,
        "items_returned": json.dumps([1]),
        "refund_amount": Decimal("129.99"),
        "label_url": None,
        "tracking_number": None,
        "escalated": False,
        "escalation_reason": None,
    }


@pytest.fixture
def sample_conversation_log_dict(test_session_id):
    """Sample conversation log data for testing."""
    return {
        "session_id": test_session_id,
        "customer_id": 1,
        "message_type": "user",
        "content": "I need to return an item",
        "meta_data": json.dumps({"tool": None, "status": "pending"}),
    }
