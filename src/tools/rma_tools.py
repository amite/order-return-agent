"""RMA (Return Merchandise Authorization) creation tool"""

import json
import random
import time
from datetime import datetime
from typing import List, cast

from langchain.tools import BaseTool
from loguru import logger
from pydantic import BaseModel

from src.db.connection import get_db_session
from src.db.schema import Order, RMA
from src.models.enums import OrderStatus, RMAStatus
from src.models.schemas import CreateRMAInput, CreateRMAOutput


class CreateRMATool(BaseTool):
    """
    Tool to create a Return Merchandise Authorization (RMA).

    Creates an RMA record in the database and updates order status.
    """

    name: str = "CreateRMA"
    description: str = """
    Create a Return Merchandise Authorization (RMA) for an approved return.

    This tool should be called AFTER CheckEligibility returns APPROVED.
    It creates an RMA record and updates the order status to Return_Initiated.

    Input:
    - order_id: Order number (required)
    - customer_id: Customer ID (required)
    - item_ids: List of item IDs being returned (required)
    - return_reason: Reason for return (required)
    - reason_code: Eligibility reason code from CheckEligibility (required)

    Returns:
    - rma_number: Unique RMA number (e.g., RMA-1234567890-ABCD)
    - rma_id: Database ID of the RMA record
    - success: Boolean indicating success
    """

    args_schema: type[BaseModel] = CreateRMAInput

    def _generate_rma_number(self) -> str:
        """Generate a unique RMA number"""
        timestamp = int(time.time())
        random_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
        return f"RMA-{timestamp}-{random_suffix}"

    def _run(
        self,
        order_id: str,
        customer_id: int,
        item_ids: List[int],
        return_reason: str,
        reason_code: str,
    ) -> str:
        """Execute RMA creation"""
        try:
            with get_db_session() as session:
                # 1. Verify order exists
                order = session.query(Order).filter(Order.order_number == order_id).first()

                if not order:
                    return CreateRMAOutput(
                        success=False,
                        error=f"Order {order_id} not found",
                        message="Unable to create RMA: Order not found.",
                    ).model_dump_json()

                # 2. Generate unique RMA number
                rma_number = self._generate_rma_number()

                # 3. Calculate refund amount (sum of item prices)
                items_to_return = [item for item in order.items if item.id in item_ids]
                refund_amount = sum(item.price * item.quantity for item in items_to_return)

                # 4. Create RMA record
                rma = RMA(
                    rma_number=rma_number,
                    order_id=order.id,
                    customer_id=customer_id,
                    return_reason=return_reason,
                    reason_code=reason_code,
                    status=RMAStatus.INITIATED,
                    items_returned=json.dumps(item_ids),
                    refund_amount=refund_amount,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

                session.add(rma)

                # 5. Update order status
                # Type checker sees Column, but runtime is Python value
                setattr(order, 'status', OrderStatus.RETURN_INITIATED)

                session.commit()
                session.refresh(rma)

                logger.info(f"Created RMA {rma_number} for order {order_id}")

                return CreateRMAOutput(
                    success=True,
                    rma_number=rma_number,
                    rma_id=cast(int, rma.id),
                    message=f"RMA {rma_number} created successfully. Refund amount: ${refund_amount:.2f}",
                ).model_dump_json()

        except Exception as e:
            logger.error(f"Error creating RMA: {e}")
            return CreateRMAOutput(
                success=False,
                error=str(e),
                message="An error occurred while creating the RMA. Please try again.",
            ).model_dump_json()

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented, falls back to sync)"""
        return self._run(*args, **kwargs)
