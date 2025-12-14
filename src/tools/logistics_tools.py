"""Logistics and shipping label tools"""

import random

from langchain.tools import BaseTool
from loguru import logger
from pydantic import BaseModel

from src.db.connection import get_db_session
from src.db.schema import RMA
from src.models.enums import RMAStatus
from src.models.schemas import GenerateReturnLabelInput, GenerateReturnLabelOutput


class GenerateReturnLabelTool(BaseTool):
    """
    Tool to generate a prepaid return shipping label.

    Simulates integration with a logistics API to create a shipping label.
    """

    name: str = "GenerateReturnLabel"
    description: str = """
    Generate a prepaid return shipping label for an RMA.

    This tool should be called AFTER CreateRMA.
    It generates a tracking number and label URL, then updates the RMA record.

    Input:
    - order_id: Order number (required)
    - rma_number: RMA number (required)

    Returns:
    - label_url: URL to download the shipping label PDF
    - tracking_number: Tracking number for the return shipment
    - success: Boolean indicating success
    """

    args_schema: type[BaseModel] = GenerateReturnLabelInput

    def _generate_tracking_number(self) -> str:
        """Generate a mock tracking number"""
        carrier_prefix = random.choice(['USPS', 'UPS', 'FEDEX'])
        tracking_digits = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        return f"{carrier_prefix}-{tracking_digits}"

    def _generate_label_url(self, rma_number: str) -> str:
        """Generate a mock label URL"""
        return f"https://returns.example.com/labels/{rma_number}.pdf"

    def _run(
        self,
        order_id: str,
        rma_number: str,
    ) -> str:
        """Execute label generation"""
        try:
            with get_db_session() as session:
                # 1. Find the RMA
                rma = session.query(RMA).filter(RMA.rma_number == rma_number).first()

                if not rma:
                    return GenerateReturnLabelOutput(
                        success=False,
                        error=f"RMA {rma_number} not found",
                        message="Unable to generate label: RMA not found.",
                    ).model_dump_json()

                # 2. Generate tracking number and label URL
                tracking_number = self._generate_tracking_number()
                label_url = self._generate_label_url(rma_number)

                # 3. Update RMA with label info
                rma.tracking_number = tracking_number
                rma.label_url = label_url
                rma.status = RMAStatus.LABEL_SENT

                session.commit()

                logger.info(f"Generated label for RMA {rma_number}: {tracking_number}")

                return GenerateReturnLabelOutput(
                    success=True,
                    label_url=label_url,
                    tracking_number=tracking_number,
                    message=f"Shipping label generated successfully. Tracking: {tracking_number}",
                ).model_dump_json()

        except Exception as e:
            logger.error(f"Error generating label: {e}")
            return GenerateReturnLabelOutput(
                success=False,
                error=str(e),
                message="An error occurred while generating the shipping label. Please try again.",
            ).model_dump_json()

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented, falls back to sync)"""
        return self._run(*args, **kwargs)
