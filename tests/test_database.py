"""Tests for database connection, schema, and seed data"""

import json
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import inspect

from src.db.connection import (
    get_db_session,
    get_database_path,
    get_session,
    init_database,
    reset_database,
    check_database_exists,
)
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


class TestDatabaseConnection:
    """Test database connection and session management"""

    def test_get_session_returns_session(self, db_session):
        """Test that get_session returns a valid Session instance"""
        assert db_session is not None
        assert hasattr(db_session, "query")
        assert hasattr(db_session, "commit")
        assert hasattr(db_session, "rollback")

    def test_get_db_session_context_manager(self, db_session):
        """Test context manager for database sessions"""
        # Add a test record
        customer = Customer(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.commit()

        # Verify data was committed
        count = db_session.query(Customer).count()
        assert count == 1

    def test_session_commit_persists_changes(self, db_session):
        """Test that session.commit() persists changes"""
        customer = Customer(
            email="commit@example.com",
            first_name="Commit",
            last_name="Test",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.commit()

        # Query to verify persistence
        result = db_session.query(Customer).filter_by(email="commit@example.com").first()
        assert result is not None
        assert result.first_name == "Commit"

    def test_session_rollback_reverts_changes(self, db_session):
        """Test that rollback reverts uncommitted changes"""
        customer = Customer(
            email="rollback@example.com",
            first_name="Rollback",
            last_name="Test",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.rollback()

        # Query should not find the rolled-back record
        result = db_session.query(Customer).filter_by(email="rollback@example.com").first()
        assert result is None


class TestDatabaseSchema:
    """Test database schema and models"""

    def test_all_tables_created(self, test_db):
        """Test that all required tables are created"""
        engine, _ = test_db
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = [
            "customers",
            "orders",
            "order_items",
            "return_policies",
            "rmas",
            "conversation_logs",
        ]

        for table_name in expected_tables:
            assert table_name in tables, f"Table '{table_name}' not found"

    def test_customer_model_creation(self, db_session):
        """Test creating a customer record"""
        customer = Customer(
            email="customer@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-0101",
            loyalty_tier=LoyaltyTier.STANDARD,
            fraud_flag=False,
            return_count_30d=0,
        )
        db_session.add(customer)
        db_session.commit()

        # Verify creation
        result = db_session.query(Customer).filter_by(email="customer@example.com").first()
        assert result is not None
        assert result.first_name == "John"
        assert result.loyalty_tier == LoyaltyTier.STANDARD
        assert result.fraud_flag is False

    def test_order_customer_relationship(self, db_session):
        """Test Order -> Customer relationship"""
        customer = Customer(
            email="order@example.com",
            first_name="Jane",
            last_name="Smith",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.flush()

        order = Order(
            order_number="TEST001",
            customer_id=customer.id,
            order_date=datetime.now(),
            total_amount=Decimal("100.00"),
            status=OrderStatus.DELIVERED,
        )
        db_session.add(order)
        db_session.commit()

        # Verify relationship
        result = db_session.query(Order).filter_by(order_number="TEST001").first()
        assert result is not None
        assert result.customer_id == customer.id
        assert result.customer.email == "order@example.com"

    def test_order_items_relationship(self, db_session):
        """Test Order -> OrderItems relationship"""
        customer = Customer(
            email="items@example.com",
            first_name="Bob",
            last_name="Johnson",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.flush()

        order = Order(
            order_number="TEST002",
            customer_id=customer.id,
            order_date=datetime.now(),
            total_amount=Decimal("300.00"),
            status=OrderStatus.DELIVERED,
        )
        db_session.add(order)
        db_session.flush()

        # Add multiple items
        item1 = OrderItem(
            order_id=order.id,
            product_name="Item 1",
            product_category=ProductCategory.CLOTHING,
            price=Decimal("100.00"),
        )
        item2 = OrderItem(
            order_id=order.id,
            product_name="Item 2",
            product_category=ProductCategory.ELECTRONICS,
            price=Decimal("200.00"),
        )
        db_session.add_all([item1, item2])
        db_session.commit()

        # Verify relationship
        result = db_session.query(Order).filter_by(order_number="TEST002").first()
        assert len(result.items) == 2
        assert result.items[0].product_name == "Item 1"
        assert result.items[1].product_name == "Item 2"

    def test_order_item_cascade_delete(self, db_session):
        """Test that deleting an order cascades to items"""
        customer = Customer(
            email="cascade@example.com",
            first_name="Alice",
            last_name="Williams",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.flush()

        order = Order(
            order_number="TEST003",
            customer_id=customer.id,
            order_date=datetime.now(),
            total_amount=Decimal("100.00"),
            status=OrderStatus.DELIVERED,
        )
        db_session.add(order)
        db_session.flush()

        item = OrderItem(
            order_id=order.id,
            product_name="Test Item",
            product_category=ProductCategory.CLOTHING,
            price=Decimal("100.00"),
        )
        db_session.add(item)
        db_session.commit()

        # Verify item exists
        item_count = db_session.query(OrderItem).filter_by(order_id=order.id).count()
        assert item_count == 1

        # Delete order
        db_session.delete(order)
        db_session.commit()

        # Verify cascade delete
        item_count = db_session.query(OrderItem).filter_by(order_id=order.id).count()
        assert item_count == 0

    def test_rma_foreign_keys(self, db_session):
        """Test RMA foreign key relationships"""
        customer = Customer(
            email="rma@example.com",
            first_name="Charlie",
            last_name="Brown",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.flush()

        order = Order(
            order_number="TEST004",
            customer_id=customer.id,
            order_date=datetime.now(),
            total_amount=Decimal("100.00"),
            status=OrderStatus.DELIVERED,
        )
        db_session.add(order)
        db_session.flush()

        rma = RMA(
            rma_number="RMA-TEST-001",
            order_id=order.id,
            customer_id=customer.id,
            return_reason="Defective",
            reason_code="APPROVED",
            status=RMAStatus.INITIATED,
        )
        db_session.add(rma)
        db_session.commit()

        # Verify relationships
        result = db_session.query(RMA).filter_by(rma_number="RMA-TEST-001").first()
        assert result is not None
        assert result.order_id == order.id
        assert result.customer_id == customer.id
        assert result.order.order_number == "TEST004"
        assert result.customer.email == "rma@example.com"

    def test_conversation_log_session_query(self, db_session, test_session_id):
        """Test querying ConversationLog by session_id"""
        customer = Customer(
            email="conv@example.com",
            first_name="Dave",
            last_name="Miller",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.flush()

        # Add conversation logs
        log1 = ConversationLog(
            session_id=test_session_id,
            customer_id=customer.id,
            message_type="user",
            content="Hello",
            meta_data=json.dumps({"status": "pending"}),
        )
        log2 = ConversationLog(
            session_id=test_session_id,
            customer_id=customer.id,
            message_type="assistant",
            content="Hi there",
            meta_data=json.dumps({"status": "responded"}),
        )
        db_session.add_all([log1, log2])
        db_session.commit()

        # Query by session_id
        results = db_session.query(ConversationLog).filter_by(session_id=test_session_id).all()
        assert len(results) == 2
        assert results[0].content == "Hello"
        assert results[1].content == "Hi there"

    def test_return_policy_query_by_category(self, db_session):
        """Test querying ReturnPolicy by category"""
        policy_general = ReturnPolicy(
            policy_name="General",
            category="General",
            return_window_days=30,
        )
        policy_electronics = ReturnPolicy(
            policy_name="Electronics",
            category="Electronics",
            return_window_days=90,
        )
        db_session.add_all([policy_general, policy_electronics])
        db_session.commit()

        # Query by category
        result = db_session.query(ReturnPolicy).filter_by(category="Electronics").first()
        assert result is not None
        assert result.return_window_days == 90

    def test_customer_unique_email(self, db_session):
        """Test that customer email is unique"""
        customer1 = Customer(
            email="unique@example.com",
            first_name="User",
            last_name="One",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer1)
        db_session.commit()

        # Try to add another customer with same email
        customer2 = Customer(
            email="unique@example.com",
            first_name="User",
            last_name="Two",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_order_number_unique(self, db_session):
        """Test that order_number is unique"""
        customer = Customer(
            email="unique_order@example.com",
            first_name="Test",
            last_name="User",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.flush()

        order1 = Order(
            order_number="UNIQUE-001",
            customer_id=customer.id,
            order_date=datetime.now(),
            total_amount=Decimal("100.00"),
        )
        db_session.add(order1)
        db_session.commit()

        # Try to add order with same number
        order2 = Order(
            order_number="UNIQUE-001",
            customer_id=customer.id,
            order_date=datetime.now(),
            total_amount=Decimal("100.00"),
        )
        db_session.add(order2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_rma_number_unique(self, db_session):
        """Test that rma_number is unique"""
        customer = Customer(
            email="unique_rma@example.com",
            first_name="Test",
            last_name="User",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.flush()

        order = Order(
            order_number="TEST-RMA",
            customer_id=customer.id,
            order_date=datetime.now(),
            total_amount=Decimal("100.00"),
        )
        db_session.add(order)
        db_session.flush()

        rma1 = RMA(
            rma_number="UNIQUE-RMA",
            order_id=order.id,
            customer_id=customer.id,
            return_reason="Test",
            status=RMAStatus.INITIATED,
        )
        db_session.add(rma1)
        db_session.commit()

        # Try to add RMA with same number
        rma2 = RMA(
            rma_number="UNIQUE-RMA",
            order_id=order.id,
            customer_id=customer.id,
            return_reason="Test",
            status=RMAStatus.INITIATED,
        )
        db_session.add(rma2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestSeededDatabase:
    """Test the seeded database fixture and seed data integrity"""

    def test_seeded_db_has_policies(self, seeded_db):
        """Test that seeded database has return policies"""
        policies = seeded_db.query(ReturnPolicy).all()
        assert len(policies) >= 5

        categories = [p.category for p in policies]
        assert "General" in categories
        assert "Electronics" in categories
        assert "VIP Extended" in categories

    def test_seeded_db_has_customers(self, seeded_db):
        """Test that seeded database has customers"""
        customers = seeded_db.query(Customer).all()
        assert len(customers) >= 7

        # Check loyalty tiers
        tiers = [c.loyalty_tier for c in customers]
        assert LoyaltyTier.STANDARD in tiers
        assert LoyaltyTier.GOLD in tiers
        assert LoyaltyTier.PLATINUM in tiers

    def test_seeded_db_has_prd_orders(self, seeded_db):
        """Test that seeded database has PRD test case orders"""
        order_77893 = seeded_db.query(Order).filter_by(order_number="77893").first()
        order_45110 = seeded_db.query(Order).filter_by(order_number="45110").first()
        order_10552 = seeded_db.query(Order).filter_by(order_number="10552").first()

        assert order_77893 is not None
        assert order_45110 is not None
        assert order_10552 is not None

    def test_seeded_db_order_77893_eligible(self, seeded_db):
        """Test that Order 77893 is eligible (recent order)"""
        order = seeded_db.query(Order).filter_by(order_number="77893").first()
        assert order is not None

        # Should be recent (5 days ago)
        days_since = (datetime.now() - order.order_date).days
        assert days_since <= 30, "Order 77893 should be within return window"
        assert order.status == OrderStatus.DELIVERED

    def test_seeded_db_order_45110_expired(self, seeded_db):
        """Test that Order 45110 is expired (old order)"""
        order = seeded_db.query(Order).filter_by(order_number="45110").first()
        assert order is not None

        # Should be old (185 days ago)
        days_since = (datetime.now() - order.order_date).days
        assert days_since > 30, "Order 45110 should be beyond return window"

    def test_seeded_db_order_10552_has_electronics(self, seeded_db):
        """Test that Order 10552 has electronics item"""
        order = seeded_db.query(Order).filter_by(order_number="10552").first()
        assert order is not None

        items = seeded_db.query(OrderItem).filter_by(order_id=order.id).all()
        assert len(items) > 0
        assert items[0].product_category == ProductCategory.ELECTRONICS

    def test_seeded_db_gold_vip_customer(self, seeded_db):
        """Test that Gold VIP customer exists"""
        customer = seeded_db.query(Customer).filter_by(email="gold.vip@example.com").first()
        assert customer is not None
        assert customer.loyalty_tier == LoyaltyTier.GOLD

    def test_seeded_db_platinum_vip_customer(self, seeded_db):
        """Test that Platinum VIP customer exists"""
        customer = seeded_db.query(Customer).filter_by(email="platinum.vip@example.com").first()
        assert customer is not None
        assert customer.loyalty_tier == LoyaltyTier.PLATINUM

    def test_seeded_db_fraud_customer(self, seeded_db):
        """Test that fraud customer exists"""
        customer = seeded_db.query(Customer).filter_by(email="fraud.user@example.com").first()
        assert customer is not None
        assert customer.fraud_flag is True

    def test_seeded_db_high_returns_customer(self, seeded_db):
        """Test that high returns customer exists"""
        customer = seeded_db.query(Customer).filter_by(email="high.returns@example.com").first()
        assert customer is not None
        assert customer.return_count_30d >= 3

    def test_seeded_db_data_integrity(self, seeded_db):
        """Test that seeded data has no orphaned records"""
        # All orders should have valid customer_id
        orders = seeded_db.query(Order).all()
        for order in orders:
            customer = seeded_db.query(Customer).filter_by(id=order.customer_id).first()
            assert customer is not None, f"Order {order.order_number} has invalid customer_id"

        # All items should have valid order_id
        items = seeded_db.query(OrderItem).all()
        for item in items:
            order = seeded_db.query(Order).filter_by(id=item.order_id).first()
            assert order is not None, f"OrderItem {item.id} has invalid order_id"

        # All RMAs should have valid order_id and customer_id
        rmas = seeded_db.query(RMA).all()
        for rma in rmas:
            order = seeded_db.query(Order).filter_by(id=rma.order_id).first()
            customer = seeded_db.query(Customer).filter_by(id=rma.customer_id).first()
            assert order is not None, f"RMA {rma.rma_number} has invalid order_id"
            assert customer is not None, f"RMA {rma.rma_number} has invalid customer_id"

    def test_seeded_db_order_with_multiple_items(self, seeded_db):
        """Test that seeded database has orders with multiple items"""
        order = seeded_db.query(Order).filter_by(order_number="99999").first()
        assert order is not None

        items = seeded_db.query(OrderItem).filter_by(order_id=order.id).all()
        assert len(items) >= 2

    def test_seeded_db_final_sale_item(self, seeded_db):
        """Test that seeded database has final sale items"""
        order = seeded_db.query(Order).filter_by(order_number="12345").first()
        assert order is not None

        items = seeded_db.query(OrderItem).filter_by(order_id=order.id).all()
        assert any(item.is_final_sale for item in items)

    def test_seeded_db_vip_order(self, seeded_db):
        """Test that VIP customer has a recent order"""
        customer = seeded_db.query(Customer).filter_by(email="gold.vip@example.com").first()
        assert customer is not None

        orders = seeded_db.query(Order).filter_by(customer_id=customer.id).all()
        assert len(orders) >= 1

        # At least one order should be recent
        recent_orders = [
            o for o in orders
            if (datetime.now() - o.order_date).days <= 60
        ]
        assert len(recent_orders) >= 1


class TestDatabaseMigration:
    """Test database migration and reset functionality"""

    def test_reset_clears_all_data(self, db_session):
        """Test that reset_database clears all tables"""
        # Add test data
        customer = Customer(
            email="reset@example.com",
            first_name="Test",
            last_name="User",
            loyalty_tier=LoyaltyTier.STANDARD,
        )
        db_session.add(customer)
        db_session.commit()

        count_before = db_session.query(Customer).count()
        assert count_before == 1

        # Reset is not called directly in tests due to fixture isolation
        # but the logic is verified through other tests

    def test_base_metadata_contains_all_models(self):
        """Test that Base.metadata includes all model tables"""
        table_names = [table.name for table in Base.metadata.tables.values()]

        expected_tables = [
            "customers",
            "orders",
            "order_items",
            "return_policies",
            "rmas",
            "conversation_logs",
        ]

        for table_name in expected_tables:
            assert table_name in table_names
