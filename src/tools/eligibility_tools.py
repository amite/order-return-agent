"""Return eligibility checking tool - CRITICAL COMPONENT"""

from datetime import datetime
from typing import List

from langchain.tools import BaseTool
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import joinedload

from src.db.connection import get_db_session
from src.db.schema import Customer, Order, OrderItem, ReturnPolicy
from src.models.enums import EligibilityReasonCode, ProductCategory
from src.models.schemas import CheckEligibilityInput, CheckEligibilityOutput


class CheckEligibilityTool(BaseTool):
    """
    CRITICAL TOOL: Check if items are eligible for return using hard-coded business logic.

    This tool implements strict policy enforcement WITHOUT LLM interpretation.
    All eligibility decisions are made using deterministic business rules.
    """

    name: str = "CheckEligibility"
    description: str = """
    Check if items are eligible for return based on company return policies.

    This tool applies hard-coded business logic to determine return eligibility.
    It checks:
    - Time since order (return window)
    - Item returnability flags (final sale, etc.)
    - Customer fraud flags
    - Product category policies
    - Return count thresholds

    Input:
    - order_id: Order number (required)
    - item_ids: List of item IDs to return (required)
    - return_reason: Reason for return (required)

    Returns:
    - eligible: Boolean indicating if return is approved
    - reason_code: Code indicating approval or specific rejection reason
    - policy_applied: Name of the policy that was applied
    - message: Human-readable explanation

    Reason codes:
    - APPROVED: Return approved
    - TIME_EXP: Return window expired
    - ITEM_EXCL: Item not returnable (final sale, etc.)
    - DATA_ERR: Missing or invalid data
    - RISK_MANUAL: Fraud flag or high return count - needs manual review
    - DAMAGED_MANUAL: Damaged/defective items require inspection
    """

    args_schema: type[BaseModel] = CheckEligibilityInput

    def _run(
        self,
        order_id: str,
        item_ids: List[int],
        return_reason: str,
    ) -> str:
        """
        Execute eligibility check using ONLY hard-coded business logic.

        NO LLM INTERPRETATION - All decisions are deterministic.
        """
        try:
            with get_db_session() as session:
                # 1. Fetch order with items and customer
                order = (
                    session.query(Order)
                    .options(
                        joinedload(Order.items),
                        joinedload(Order.customer),
                    )
                    .filter(Order.order_number == order_id)
                    .first()
                )

                if not order:
                    return CheckEligibilityOutput(
                        eligible=False,
                        reason_code=EligibilityReasonCode.DATA_ERR,
                        policy_applied="N/A",
                        message=f"Order {order_id} not found.",
                    ).model_dump_json()

                # 2. Calculate days since order
                now = datetime.now()
                days_since_order = (now - order.order_date).days

                # 3. Fetch items to return
                items_to_return = [item for item in order.items if item.id in item_ids]

                if not items_to_return:
                    return CheckEligibilityOutput(
                        eligible=False,
                        reason_code=EligibilityReasonCode.DATA_ERR,
                        policy_applied="N/A",
                        message="No valid items found to return.",
                        days_since_order=days_since_order,
                    ).model_dump_json()

                # 4. Check for damaged/defective items (requires manual review)
                damaged_keywords = ["damaged", "defective", "broken", "shattered", "torn"]
                if any(keyword in return_reason.lower() for keyword in damaged_keywords):
                    return CheckEligibilityOutput(
                        eligible=False,
                        reason_code=EligibilityReasonCode.DAMAGED_MANUAL,
                        policy_applied="Damage Inspection Policy",
                        message="Damaged or defective items require inspection by a specialist. Escalating to human agent.",
                        days_since_order=days_since_order,
                        requires_manual_review=True,
                    ).model_dump_json()

                # 5. Check customer fraud flags and return count
                customer = order.customer
                if customer.fraud_flag:
                    return CheckEligibilityOutput(
                        eligible=False,
                        reason_code=EligibilityReasonCode.RISK_MANUAL,
                        policy_applied="Fraud Prevention Policy",
                        message="Account flagged for review. Please connect with a specialist.",
                        days_since_order=days_since_order,
                        requires_manual_review=True,
                    ).model_dump_json()

                # Check high return count (3+ returns in 30 days)
                if customer.return_count_30d >= 3:
                    return CheckEligibilityOutput(
                        eligible=False,
                        reason_code=EligibilityReasonCode.RISK_MANUAL,
                        policy_applied="Return Frequency Policy",
                        message="Your account has multiple recent returns. A specialist will review your request.",
                        days_since_order=days_since_order,
                        requires_manual_review=True,
                    ).model_dump_json()

                # 6. Check if items are returnable (final sale check)
                non_returnable_items = [
                    item for item in items_to_return if not item.is_returnable or item.is_final_sale
                ]
                if non_returnable_items:
                    item_names = ", ".join([item.product_name for item in non_returnable_items])
                    return CheckEligibilityOutput(
                        eligible=False,
                        reason_code=EligibilityReasonCode.ITEM_EXCL,
                        policy_applied="Final Sale Policy",
                        message=f"The following items are final sale and cannot be returned: {item_names}",
                        days_since_order=days_since_order,
                    ).model_dump_json()

                # 7. Determine applicable return policy based on items
                # Get all unique categories
                categories = set([item.product_category for item in items_to_return if item.product_category])

                # Fetch policies
                policies = session.query(ReturnPolicy).filter(ReturnPolicy.is_active == True).all()

                # Determine which policy applies
                applicable_policy = None
                max_window = 0

                # Check VIP extended policy for Gold/Platinum customers
                if customer.loyalty_tier in ["Gold", "Platinum"]:
                    vip_policy = next(
                        (p for p in policies if p.category == "VIP Extended"), None
                    )
                    if vip_policy:
                        applicable_policy = vip_policy
                        max_window = vip_policy.return_window_days

                # If no VIP policy or not VIP customer, check category policies
                if not applicable_policy:
                    for item in items_to_return:
                        category = item.product_category
                        if category:
                            # Find policy for this category
                            category_policy = next(
                                (p for p in policies if p.category == category), None
                            )
                            if category_policy:
                                if category_policy.return_window_days > max_window:
                                    max_window = category_policy.return_window_days
                                    applicable_policy = category_policy

                # Fallback to general policy
                if not applicable_policy:
                    general_policy = next(
                        (p for p in policies if p.category == "General"), None
                    )
                    if general_policy:
                        applicable_policy = general_policy
                        max_window = general_policy.return_window_days

                if not applicable_policy:
                    return CheckEligibilityOutput(
                        eligible=False,
                        reason_code=EligibilityReasonCode.DATA_ERR,
                        policy_applied="N/A",
                        message="Unable to determine applicable return policy.",
                        days_since_order=days_since_order,
                    ).model_dump_json()

                # 8. Check if within return window
                if days_since_order > max_window:
                    return CheckEligibilityOutput(
                        eligible=False,
                        reason_code=EligibilityReasonCode.TIME_EXP,
                        policy_applied=applicable_policy.policy_name,
                        message=f"Order is {days_since_order} days old. Return window is {max_window} days.",
                        days_since_order=days_since_order,
                    ).model_dump_json()

                # 9. ALL CHECKS PASSED - APPROVE RETURN
                return CheckEligibilityOutput(
                    eligible=True,
                    reason_code=EligibilityReasonCode.APPROVED,
                    policy_applied=applicable_policy.policy_name,
                    message=f"Return approved under {applicable_policy.policy_name} ({max_window}-day window).",
                    days_since_order=days_since_order,
                    requires_manual_review=False,
                ).model_dump_json()

        except Exception as e:
            logger.error(f"Error in CheckEligibility: {e}")
            return CheckEligibilityOutput(
                eligible=False,
                reason_code=EligibilityReasonCode.DATA_ERR,
                policy_applied="N/A",
                message=f"An error occurred while checking eligibility: {str(e)}",
            ).model_dump_json()

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented, falls back to sync)"""
        return self._run(*args, **kwargs)
