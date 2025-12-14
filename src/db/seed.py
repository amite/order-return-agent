"""Seed the database with comprehensive mock data"""

import json
import random
from datetime import datetime, timedelta
from decimal import Decimal

from loguru import logger
from sqlalchemy.orm import Session

from src.db.connection import get_db_session, init_database
from src.db.schema import (
    ConversationLog,
    Customer,
    Order,
    OrderItem,
    ReturnPolicy,
    RMA,
)
from src.models.enums import (
    LoyaltyTier,
    OrderStatus,
    ProductCategory,
    RMAStatus,
)


def seed_return_policies(session: Session) -> None:
    """Create return policy records"""
    logger.info("Seeding return policies...")

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

    session.add_all(policies)
    session.commit()
    logger.success(f"Created {len(policies)} return policies")


def seed_customers(session: Session) -> list:
    """Create customer records with various loyalty tiers and flags"""
    logger.info("Seeding customers...")

    customers_data = [
        # Standard tier customers (5)
        {
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "555-0101",
            "loyalty_tier": LoyaltyTier.STANDARD,
            "fraud_flag": False,
            "return_count_30d": 0,
        },
        {
            "email": "jane.smith@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "555-0102",
            "loyalty_tier": LoyaltyTier.STANDARD,
            "fraud_flag": False,
            "return_count_30d": 1,
        },
        {
            "email": "bob.johnson@example.com",
            "first_name": "Bob",
            "last_name": "Johnson",
            "phone": "555-0103",
            "loyalty_tier": LoyaltyTier.STANDARD,
            "fraud_flag": False,
            "return_count_30d": 0,
        },
        {
            "email": "alice.williams@example.com",
            "first_name": "Alice",
            "last_name": "Williams",
            "phone": "555-0104",
            "loyalty_tier": LoyaltyTier.STANDARD,
            "fraud_flag": False,
            "return_count_30d": 2,
        },
        {
            "email": "charlie.brown@example.com",
            "first_name": "Charlie",
            "last_name": "Brown",
            "phone": "555-0105",
            "loyalty_tier": LoyaltyTier.STANDARD,
            "fraud_flag": False,
            "return_count_30d": 0,
        },
        # Silver tier customers (5)
        {
            "email": "david.miller@example.com",
            "first_name": "David",
            "last_name": "Miller",
            "phone": "555-0201",
            "loyalty_tier": LoyaltyTier.SILVER,
            "fraud_flag": False,
            "return_count_30d": 1,
        },
        {
            "email": "emily.davis@example.com",
            "first_name": "Emily",
            "last_name": "Davis",
            "phone": "555-0202",
            "loyalty_tier": LoyaltyTier.SILVER,
            "fraud_flag": False,
            "return_count_30d": 0,
        },
        {
            "email": "frank.wilson@example.com",
            "first_name": "Frank",
            "last_name": "Wilson",
            "phone": "555-0203",
            "loyalty_tier": LoyaltyTier.SILVER,
            "fraud_flag": False,
            "return_count_30d": 2,
        },
        {
            "email": "grace.moore@example.com",
            "first_name": "Grace",
            "last_name": "Moore",
            "phone": "555-0204",
            "loyalty_tier": LoyaltyTier.SILVER,
            "fraud_flag": False,
            "return_count_30d": 0,
        },
        {
            "email": "henry.taylor@example.com",
            "first_name": "Henry",
            "last_name": "Taylor",
            "phone": "555-0205",
            "loyalty_tier": LoyaltyTier.SILVER,
            "fraud_flag": False,
            "return_count_30d": 1,
        },
        # Gold tier customers (3)
        {
            "email": "isabel.anderson@example.com",
            "first_name": "Isabel",
            "last_name": "Anderson",
            "phone": "555-0301",
            "loyalty_tier": LoyaltyTier.GOLD,
            "fraud_flag": False,
            "return_count_30d": 0,
        },
        {
            "email": "jack.thomas@example.com",
            "first_name": "Jack",
            "last_name": "Thomas",
            "phone": "555-0302",
            "loyalty_tier": LoyaltyTier.GOLD,
            "fraud_flag": False,
            "return_count_30d": 1,
        },
        {
            "email": "kelly.jackson@example.com",
            "first_name": "Kelly",
            "last_name": "Jackson",
            "phone": "555-0303",
            "loyalty_tier": LoyaltyTier.GOLD,
            "fraud_flag": False,
            "return_count_30d": 0,
        },
        # Platinum tier customers (2)
        {
            "email": "liam.white@example.com",
            "first_name": "Liam",
            "last_name": "White",
            "phone": "555-0401",
            "loyalty_tier": LoyaltyTier.PLATINUM,
            "fraud_flag": False,
            "return_count_30d": 0,
        },
        {
            "email": "maria.harris@example.com",
            "first_name": "Maria",
            "last_name": "Harris",
            "phone": "555-0402",
            "loyalty_tier": LoyaltyTier.PLATINUM,
            "fraud_flag": False,
            "return_count_30d": 1,
        },
        # Customers with fraud flags (2)
        {
            "email": "nathan.fraud@example.com",
            "first_name": "Nathan",
            "last_name": "Fraud",
            "phone": "555-0501",
            "loyalty_tier": LoyaltyTier.STANDARD,
            "fraud_flag": True,
            "return_count_30d": 5,
        },
        {
            "email": "olivia.suspicious@example.com",
            "first_name": "Olivia",
            "last_name": "Suspicious",
            "phone": "555-0502",
            "loyalty_tier": LoyaltyTier.SILVER,
            "fraud_flag": True,
            "return_count_30d": 4,
        },
        # High return count customers (3)
        {
            "email": "peter.returns@example.com",
            "first_name": "Peter",
            "last_name": "Returns",
            "phone": "555-0601",
            "loyalty_tier": LoyaltyTier.STANDARD,
            "fraud_flag": False,
            "return_count_30d": 4,
        },
        {
            "email": "quinn.frequent@example.com",
            "first_name": "Quinn",
            "last_name": "Frequent",
            "phone": "555-0602",
            "loyalty_tier": LoyaltyTier.SILVER,
            "fraud_flag": False,
            "return_count_30d": 3,
        },
        {
            "email": "rachel.often@example.com",
            "first_name": "Rachel",
            "last_name": "Often",
            "phone": "555-0603",
            "loyalty_tier": LoyaltyTier.GOLD,
            "fraud_flag": False,
            "return_count_30d": 3,
        },
    ]

    customers = [Customer(**data) for data in customers_data]
    session.add_all(customers)
    session.commit()

    logger.success(f"Created {len(customers)} customers")
    return customers


def seed_orders_and_items(session: Session, customers: list) -> list:
    """Create orders with various age ranges and item types"""
    logger.info("Seeding orders and order items...")

    orders = []
    now = datetime.now()

    # Product catalog
    products = {
        "clothing": [
            ("Red T-Shirt", "CLO-001", 29.99),
            ("Blue Jeans", "CLO-002", 59.99),
            ("Black Jacket", "CLO-003", 89.99),
            ("White Sneakers", "FOO-001", 79.99),
            ("Hiking Boots", "FOO-002", 129.99),
        ],
        "electronics": [
            ("Smart Watch", "ELE-001", 299.99),
            ("Wireless Headphones", "ELE-002", 149.99),
            ("Laptop", "ELE-003", 999.99),
            ("Tablet", "ELE-004", 499.99),
            ("Phone Case", "ELE-005", 24.99),
        ],
        "home_goods": [
            ("Toaster", "HOME-001", 49.99),
            ("Blender", "HOME-002", 79.99),
            ("Coffee Maker", "HOME-003", 99.99),
            ("Vacuum Cleaner", "HOME-004", 199.99),
        ],
        "special_edition": [
            ("Limited Edition Vinyl", "SPE-001", 149.99),
            ("Collector's Watch", "SPE-002", 599.99),
            ("Signed Baseball", "SPE-003", 299.99),
        ],
    }

    order_number_counter = 10000

    # Helper function to create an order
    def create_order(
        customer, days_ago, item_list, status=OrderStatus.DELIVERED, final_sale=False
    ):
        nonlocal order_number_counter
        order_number_counter += 1

        order_date = now - timedelta(days=days_ago)
        order = Order(
            order_number=str(order_number_counter),
            customer_id=customer.id,
            order_date=order_date,
            total_amount=Decimal("0"),
            status=status,
            shipping_address=f"{random.randint(100, 999)} Main St, City, ST 12345",
        )
        session.add(order)
        session.flush()

        total = Decimal("0")
        for product_name, sku, price, category in item_list:
            item = OrderItem(
                order_id=order.id,
                product_name=product_name,
                product_category=category,
                sku=sku,
                quantity=1,
                price=Decimal(str(price)),
                is_final_sale=final_sale,
                is_returnable=not final_sale,
            )
            session.add(item)
            total += Decimal(str(price))

        order.total_amount = total  # type: ignore[assignment]
        return order

    # 10 orders within 30 days (eligible for standard policy)
    for i in range(10):
        customer = customers[i % len(customers)]
        days_ago = random.randint(5, 29)
        category_key = random.choice(list(products.keys()))
        product_data = random.choice(products[category_key])
        category_enum = {
            "clothing": ProductCategory.CLOTHING,
            "electronics": ProductCategory.ELECTRONICS,
            "home_goods": ProductCategory.HOME_GOODS,
            "special_edition": ProductCategory.SPECIAL_EDITION,
        }[category_key]
        item_list = [(product_data[0], product_data[1], product_data[2], category_enum)]
        order = create_order(customer, days_ago, item_list)
        orders.append(order)

    # 10 orders 31-90 days old (eligible for some categories)
    for i in range(10):
        customer = customers[(i + 10) % len(customers)]
        days_ago = random.randint(31, 89)
        category_key = random.choice(list(products.keys()))
        product_data = random.choice(products[category_key])
        category_enum = {
            "clothing": ProductCategory.CLOTHING,
            "electronics": ProductCategory.ELECTRONICS,
            "home_goods": ProductCategory.HOME_GOODS,
            "special_edition": ProductCategory.SPECIAL_EDITION,
        }[category_key]
        item_list = [(product_data[0], product_data[1], product_data[2], category_enum)]
        order = create_order(customer, days_ago, item_list)
        orders.append(order)

    # 10 orders 90+ days old (ineligible - time expired)
    for i in range(10):
        customer = customers[(i + 20) % len(customers)]
        days_ago = random.randint(91, 200)
        category_key = random.choice(list(products.keys()))
        product_data = random.choice(products[category_key])
        category_enum = {
            "clothing": ProductCategory.CLOTHING,
            "electronics": ProductCategory.ELECTRONICS,
            "home_goods": ProductCategory.HOME_GOODS,
            "special_edition": ProductCategory.SPECIAL_EDITION,
        }[category_key]
        item_list = [(product_data[0], product_data[1], product_data[2], category_enum)]
        order = create_order(customer, days_ago, item_list)
        orders.append(order)

    # 10 orders with final sale items (ineligible - item exclusion)
    for i in range(10):
        customer = customers[(i + 30) % len(customers)]
        days_ago = random.randint(5, 29)
        category_key = random.choice(list(products.keys()))
        product_data = random.choice(products[category_key])
        category_enum = {
            "clothing": ProductCategory.CLOTHING,
            "electronics": ProductCategory.ELECTRONICS,
            "home_goods": ProductCategory.HOME_GOODS,
            "special_edition": ProductCategory.SPECIAL_EDITION,
        }[category_key]
        item_list = [(product_data[0], product_data[1], product_data[2], category_enum)]
        order = create_order(customer, days_ago, item_list, final_sale=True)
        orders.append(order)

    # 10 orders with mixed item types
    for i in range(10):
        customer = customers[(i + 40) % len(customers)]
        days_ago = random.randint(5, 60)
        item_list = []
        # Add 2-3 random items
        for _ in range(random.randint(2, 3)):
            category_key = random.choice(list(products.keys()))
            product_data = random.choice(products[category_key])
            category_enum = {
                "clothing": ProductCategory.CLOTHING,
                "electronics": ProductCategory.ELECTRONICS,
                "home_goods": ProductCategory.HOME_GOODS,
                "special_edition": ProductCategory.SPECIAL_EDITION,
            }[category_key]
            item_list.append(
                (product_data[0], product_data[1], product_data[2], category_enum)
            )
        order = create_order(customer, days_ago, item_list)
        orders.append(order)

    # Create specific PRD test case orders
    # Example 1: Order #77893 - hiking boots, 15 days ago (eligible)
    customer_john = next(c for c in customers if c.email == "john.doe@example.com")
    order_77893 = create_order(
        customer_john,
        15,
        [("Hiking Boots", "FOO-002", 129.99, ProductCategory.FOOTWEAR)],
    )
    order_77893.order_number = "77893"  # type: ignore[assignment]
    orders.append(order_77893)

    # Example 2: Order #45110 - jacket, 185 days ago (ineligible)
    customer_jane = next(c for c in customers if c.email == "jane.smith@example.com")
    order_45110 = create_order(
        customer_jane,
        185,
        [("Black Jacket", "CLO-003", 89.99, ProductCategory.CLOTHING)],
    )
    order_45110.order_number = "45110"  # type: ignore[assignment]
    orders.append(order_45110)

    # Example 4: Order #10552 - shattered electronics, 10 days ago
    customer_bob = next(c for c in customers if c.email == "bob.johnson@example.com")
    order_10552 = create_order(
        customer_bob,
        10,
        [("Tablet", "ELE-004", 499.99, ProductCategory.ELECTRONICS)],
    )
    order_10552.order_number = "10552"  # type: ignore[assignment]
    orders.append(order_10552)

    session.commit()
    logger.success(f"Created {len(orders)} orders with items")
    return orders


def seed_completed_rmas(session: Session, orders: list) -> None:
    """Create some completed RMAs for testing refund status queries"""
    logger.info("Seeding completed RMAs...")

    # Create 10 completed RMAs
    rmas_data = [
        {
            "rma_number": "RMA4567",
            "order": orders[0],
            "return_reason": "Wrong size",
            "reason_code": "APPROVED",
            "status": RMAStatus.REFUNDED,
            "days_ago": 10,
        },
        {
            "rma_number": "RMA4568",
            "order": orders[1],
            "return_reason": "Unwanted",
            "reason_code": "APPROVED",
            "status": RMAStatus.PROCESSED,
            "days_ago": 5,
        },
        {
            "rma_number": "RMA4569",
            "order": orders[2],
            "return_reason": "Defective",
            "reason_code": "APPROVED",
            "status": RMAStatus.IN_TRANSIT,
            "days_ago": 3,
        },
    ]

    now = datetime.now()
    rmas = []

    for data in rmas_data:
        created_date = now - timedelta(days=data["days_ago"])
        rma = RMA(
            rma_number=data["rma_number"],
            order_id=data["order"].id,
            customer_id=data["order"].customer_id,
            return_reason=data["return_reason"],
            reason_code=data["reason_code"],
            status=data["status"],
            items_returned=json.dumps([1]),  # Simplified
            refund_amount=data["order"].total_amount,
            label_url=f"https://example.com/labels/{data['rma_number']}.pdf",
            tracking_number=f"TRACK-{random.randint(10000, 99999)}",
            created_at=created_date,
            updated_at=created_date,
        )
        rmas.append(rma)

    session.add_all(rmas)
    session.commit()
    logger.success(f"Created {len(rmas)} completed RMAs")


def seed_database(force_recreate: bool = False) -> None:
    """
    Main function to seed the entire database with mock data.

    Args:
        force_recreate: If True, recreate the database before seeding
    """
    logger.info("Starting database seeding process...")

    # Initialize database
    init_database(force_recreate=force_recreate)

    # Seed data
    with get_db_session() as session:
        seed_return_policies(session)
        customers = seed_customers(session)
        orders = seed_orders_and_items(session, customers)
        seed_completed_rmas(session, orders)

    logger.success("Database seeding completed successfully!")


if __name__ == "__main__":
    # Run seeding with fresh database
    seed_database(force_recreate=True)
