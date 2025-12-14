"""Database schema models using SQLAlchemy ORM"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Customer(Base):
    """Customer model with loyalty tier and fraud tracking"""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    loyalty_tier = Column(
        String(20), default="Standard"
    )  # Standard, Silver, Gold, Platinum
    account_status = Column(String(20), default="Active")  # Active, Suspended, Closed
    created_at = Column(DateTime, default=func.now())
    fraud_flag = Column(Boolean, default=False)
    return_count_30d = Column(
        Integer, default=0
    )  # Number of returns in last 30 days

    # Relationships
    orders = relationship("Order", back_populates="customer")
    rmas = relationship("RMA", back_populates="customer")
    conversation_logs = relationship("ConversationLog", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, email='{self.email}', tier='{self.loyalty_tier}')>"


class Order(Base):
    """Order model with items and status tracking"""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        String(30), default="Delivered"
    )  # Pending, Shipped, Delivered, Return_Initiated, Returned
    shipping_address = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    rmas = relationship("RMA", back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    """Individual items within an order"""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_category = Column(
        String(50)
    )  # Clothing, Electronics, Home Goods, Special Edition
    sku = Column(String(50))
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)
    is_final_sale = Column(Boolean, default=False)
    is_returnable = Column(Boolean, default=True)

    # Relationships
    order = relationship("Order", back_populates="items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product='{self.product_name}', category='{self.product_category}')>"


class ReturnPolicy(Base):
    """Return policy rules by product category"""

    __tablename__ = "return_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_name = Column(String(100), nullable=False)
    category = Column(
        String(50)
    )  # General, Electronics, Clothing, Final Sale, VIP Extended
    return_window_days = Column(Integer, nullable=False)
    requires_original_packaging = Column(Boolean, default=False)
    restocking_fee_percent = Column(Numeric(5, 2), default=0)
    conditions = Column(Text)  # JSON or text description of additional conditions
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<ReturnPolicy(id={self.id}, name='{self.policy_name}', days={self.return_window_days})>"


class RMA(Base):
    """Return Merchandise Authorization tracking"""

    __tablename__ = "rmas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rma_number = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    return_reason = Column(Text, nullable=False)
    reason_code = Column(
        String(30)
    )  # WRONG_SIZE, DEFECTIVE, UNWANTED, DAMAGED, CHANGED_MIND, etc.
    status = Column(
        String(30), default="Initiated"
    )  # Initiated, Label_Sent, In_Transit, Received, Processed, Refunded
    items_returned = Column(Text)  # JSON list of item IDs
    refund_amount = Column(Numeric(10, 2))
    label_url = Column(String(500))
    tracking_number = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text)

    # Relationships
    order = relationship("Order", back_populates="rmas")
    customer = relationship("Customer", back_populates="rmas")

    def __repr__(self):
        return f"<RMA(id={self.id}, number='{self.rma_number}', status='{self.status}')>"


class ConversationLog(Base):
    """Log of all agent-customer conversations"""

    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    message_type = Column(String(20))  # user, assistant, tool, system
    content = Column(Text, nullable=False)
    meta_data = Column(Text)  # JSON for tool results, session state, etc.
    created_at = Column(DateTime, default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="conversation_logs")

    def __repr__(self):
        return f"<ConversationLog(id={self.id}, session='{self.session_id}', type='{self.message_type}')>"
