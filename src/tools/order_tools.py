"""Order lookup tools"""

from typing import Optional

from langchain.tools import BaseTool
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import joinedload

from src.db.connection import get_db_session
from src.db.schema import Customer, Order, OrderItem
from src.models.schemas import GetOrderDetailsInput, GetOrderDetailsOutput, OrderSchema


class GetOrderDetailsTool(BaseTool):
    """
    Tool to retrieve order details by order number or customer email.

    This is the foundational tool that must be called first in the return flow.
    """

    name: str = "GetOrderDetails"
    description: str = """
    Look up order information by order number or customer email.

    Use this tool to:
    - Find an order by its order number (e.g., "77893")
    - Find orders by customer email (may return multiple orders)
    - Retrieve order date, items, customer info, and status

    Input:
    - order_id (optional): The order number to look up
    - email (optional): Customer email to search by

    Note: Provide either order_id OR email, not both.

    Returns order details including items, dates, and customer information.
    """

    args_schema: type[BaseModel] = GetOrderDetailsInput

    def _run(
        self,
        order_id: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """Execute the tool"""
        try:
            # Validate input
            if not order_id and not email:
                return GetOrderDetailsOutput(
                    success=False,
                    error="Must provide either order_id or email",
                    message="Please provide an order number or email address to look up the order.",
                ).model_dump_json()

            with get_db_session() as session:
                if order_id:
                    # Lookup by order number
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
                        return GetOrderDetailsOutput(
                            success=False,
                            error=f"Order {order_id} not found",
                            message=f"I couldn't find an order with number {order_id}. Please check the order number and try again.",
                        ).model_dump_json()

                    # Convert to schema
                    order_schema = OrderSchema.model_validate(order)

                    return GetOrderDetailsOutput(
                        success=True,
                        order=order_schema,
                        message=f"Found order {order_id} placed on {order.order_date.strftime('%B %d, %Y')}.",
                    ).model_dump_json()

                elif email:
                    # Lookup by email
                    orders = (
                        session.query(Order)
                        .join(Customer)
                        .options(
                            joinedload(Order.items),
                            joinedload(Order.customer),
                        )
                        .filter(Customer.email == email)
                        .order_by(Order.order_date.desc())
                        .limit(10)  # Limit to 10 most recent
                        .all()
                    )

                    if not orders:
                        return GetOrderDetailsOutput(
                            success=False,
                            error=f"No orders found for {email}",
                            message=f"I couldn't find any orders associated with {email}. Please check the email address.",
                        ).model_dump_json()

                    # Convert to schemas
                    order_schemas = [OrderSchema.model_validate(order) for order in orders]

                    if len(orders) == 1:
                        # Single order found
                        return GetOrderDetailsOutput(
                            success=True,
                            order=order_schemas[0],
                            message=f"Found 1 order for {email}.",
                        ).model_dump_json()
                    else:
                        # Multiple orders found
                        return GetOrderDetailsOutput(
                            success=True,
                            orders=order_schemas,
                            message=f"Found {len(orders)} orders for {email}. Please specify which order you'd like to return items from.",
                        ).model_dump_json()

        except Exception as e:
            logger.error(f"Error in GetOrderDetails: {e}")
            return GetOrderDetailsOutput(
                success=False,
                error=str(e),
                message="An error occurred while looking up the order. Please try again.",
            ).model_dump_json()

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented, falls back to sync)"""
        return self._run(*args, **kwargs)
