"""Enum definitions for status codes and reason codes"""

from enum import Enum


class LoyaltyTier(str, Enum):
    """Customer loyalty tier levels"""

    STANDARD = "Standard"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"


class AccountStatus(str, Enum):
    """Customer account status"""

    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    CLOSED = "Closed"


class OrderStatus(str, Enum):
    """Order processing status"""

    PENDING = "Pending"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    RETURN_INITIATED = "Return_Initiated"
    RETURNED = "Returned"


class ProductCategory(str, Enum):
    """Product category types"""

    CLOTHING = "Clothing"
    ELECTRONICS = "Electronics"
    HOME_GOODS = "Home Goods"
    SPECIAL_EDITION = "Special Edition"
    FOOTWEAR = "Footwear"
    ACCESSORIES = "Accessories"


class PolicyCategory(str, Enum):
    """Return policy categories"""

    GENERAL = "General"
    ELECTRONICS = "Electronics"
    CLOTHING = "Clothing"
    FINAL_SALE = "Final Sale"
    VIP_EXTENDED = "VIP Extended"


class EligibilityReasonCode(str, Enum):
    """
    Reason codes for return eligibility decisions.
    These codes are used by CheckEligibility tool.
    """

    # Approved
    APPROVED = "APPROVED"

    # Ineligible - Time
    TIME_EXP = "TIME_EXP"  # Return window expired

    # Ineligible - Item
    ITEM_EXCL = "ITEM_EXCL"  # Item not returnable (final sale, etc.)

    # Ineligible - Data
    DATA_ERR = "DATA_ERR"  # Missing or invalid data

    # Manual Review Required
    RISK_MANUAL = "RISK_MANUAL"  # Fraud flag or high return count
    DAMAGED_MANUAL = "DAMAGED_MANUAL"  # Damaged/defective items require inspection
    COMPLEX_MANUAL = "COMPLEX_MANUAL"  # Complex situation needs human judgment


class ReturnReason(str, Enum):
    """Customer return reasons"""

    WRONG_SIZE = "Wrong Size"
    WRONG_COLOR = "Wrong Color"
    DEFECTIVE = "Defective"
    DAMAGED = "Damaged"
    NOT_AS_DESCRIBED = "Not as Described"
    UNWANTED = "Unwanted"
    CHANGED_MIND = "Changed Mind"
    FOUND_BETTER_PRICE = "Found Better Price"
    DUPLICATE_ORDER = "Duplicate Order"
    OTHER = "Other"


class RMAStatus(str, Enum):
    """RMA (Return Merchandise Authorization) processing status"""

    INITIATED = "Initiated"
    LABEL_SENT = "Label_Sent"
    IN_TRANSIT = "In_Transit"
    RECEIVED = "Received"
    INSPECTED = "Inspected"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PROCESSED = "Processed"
    REFUNDED = "Refunded"


class EscalationPriority(str, Enum):
    """Priority level for human escalation"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class MessageType(str, Enum):
    """Conversation log message types"""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"
