"""Pydantic schemas for data validation and API models"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.enums import (
    AccountStatus,
    EligibilityReasonCode,
    EscalationPriority,
    LoyaltyTier,
    MessageType,
    OrderStatus,
    PolicyCategory,
    ProductCategory,
    RMAStatus,
    ReturnReason,
)


# Customer Schemas
class CustomerSchema(BaseModel):
    """Customer data model"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    loyalty_tier: LoyaltyTier
    account_status: AccountStatus
    fraud_flag: bool = False
    return_count_30d: int = 0


# Order Item Schemas
class OrderItemSchema(BaseModel):
    """Order item data model"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_name: str
    product_category: Optional[ProductCategory] = None
    sku: Optional[str] = None
    quantity: int
    price: Decimal
    is_final_sale: bool = False
    is_returnable: bool = True


# Order Schemas
class OrderSchema(BaseModel):
    """Order data model"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int
    order_date: datetime
    total_amount: Decimal
    status: OrderStatus
    shipping_address: Optional[str] = None
    items: List[OrderItemSchema] = []
    customer: Optional[CustomerSchema] = None


# Return Policy Schemas
class ReturnPolicySchema(BaseModel):
    """Return policy data model"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_name: str
    category: Optional[PolicyCategory] = None
    return_window_days: int
    requires_original_packaging: bool = False
    restocking_fee_percent: Decimal = Decimal("0")
    conditions: Optional[str] = None
    is_active: bool = True


# RMA Schemas
class RMASchema(BaseModel):
    """RMA (Return Merchandise Authorization) data model"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    rma_number: str
    order_id: int
    customer_id: int
    return_reason: str
    reason_code: Optional[str] = None
    status: RMAStatus
    items_returned: Optional[str] = None  # JSON string
    refund_amount: Optional[Decimal] = None
    label_url: Optional[str] = None
    tracking_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    escalated: bool = False
    escalation_reason: Optional[str] = None


# Tool Input/Output Schemas

# Tool 1: GetOrderDetails
class GetOrderDetailsInput(BaseModel):
    """Input for GetOrderDetails tool"""

    order_id: Optional[str] = Field(None, description="Order number to look up")
    email: Optional[EmailStr] = Field(None, description="Customer email to search by")


class GetOrderDetailsOutput(BaseModel):
    """Output from GetOrderDetails tool"""

    success: bool
    order: Optional[OrderSchema] = None
    orders: Optional[List[OrderSchema]] = (
        None  # Multiple orders found (when searching by email)
    )
    error: Optional[str] = None
    message: str


# Tool 2: CheckEligibility
class CheckEligibilityInput(BaseModel):
    """Input for CheckEligibility tool"""

    order_id: str = Field(..., description="Order number")
    item_ids: List[int] = Field(..., description="List of item IDs to return")
    return_reason: str = Field(..., description="Reason for return")


class CheckEligibilityOutput(BaseModel):
    """Output from CheckEligibility tool"""

    eligible: bool
    reason_code: EligibilityReasonCode
    policy_applied: str
    message: str
    days_since_order: Optional[int] = None
    requires_manual_review: bool = False


# Tool 3: CreateRMA
class CreateRMAInput(BaseModel):
    """Input for CreateRMA tool"""

    order_id: str = Field(..., description="Order number")
    customer_id: int = Field(..., description="Customer ID")
    item_ids: List[int] = Field(..., description="List of item IDs to return")
    return_reason: str = Field(..., description="Reason for return")
    reason_code: str = Field(..., description="Eligibility reason code")


class CreateRMAOutput(BaseModel):
    """Output from CreateRMA tool"""

    success: bool
    rma_number: Optional[str] = None
    rma_id: Optional[int] = None
    error: Optional[str] = None
    message: str


# Tool 4: GenerateReturnLabel
class GenerateReturnLabelInput(BaseModel):
    """Input for GenerateReturnLabel tool"""

    order_id: str = Field(..., description="Order number")
    rma_number: str = Field(..., description="RMA number")


class GenerateReturnLabelOutput(BaseModel):
    """Output from GenerateReturnLabel tool"""

    success: bool
    label_url: Optional[str] = None
    tracking_number: Optional[str] = None
    error: Optional[str] = None
    message: str


# Tool 5: SendEmail
class SendEmailInput(BaseModel):
    """Input for SendEmail tool"""

    customer_email: EmailStr = Field(..., description="Customer email address")
    template_name: str = Field(..., description="Email template name")
    context: dict = Field(..., description="Template context variables")


class SendEmailOutput(BaseModel):
    """Output from SendEmail tool"""

    success: bool
    message_id: Optional[str] = None
    preview: Optional[str] = None  # First 200 chars
    error: Optional[str] = None
    message: str


# Tool 6: EscalateToHuman
class EscalateToHumanInput(BaseModel):
    """Input for EscalateToHuman tool"""

    session_id: str = Field(..., description="Conversation session ID")
    reason: str = Field(..., description="Reason for escalation")
    priority: EscalationPriority = Field(
        default=EscalationPriority.MEDIUM, description="Priority level"
    )


class EscalateToHumanOutput(BaseModel):
    """Output from EscalateToHuman tool"""

    success: bool
    ticket_id: Optional[str] = None
    summary: Optional[str] = None  # RAG-generated handoff summary
    error: Optional[str] = None
    message: str


# Conversation Log Schema
class ConversationLogSchema(BaseModel):
    """Conversation log data model"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    customer_id: Optional[int] = None
    message_type: MessageType
    content: str
    meta_data: Optional[str] = None
    created_at: datetime
