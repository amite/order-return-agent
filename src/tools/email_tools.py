"""Email sending and template tools"""

import time
from typing import Dict, Any, ClassVar

from jinja2 import Template
from langchain.tools import BaseTool
from loguru import logger
from pydantic import BaseModel

from src.db.connection import get_db_session
from src.db.schema import ConversationLog
from src.models.enums import MessageType
from src.models.schemas import SendEmailInput, SendEmailOutput


class SendEmailTool(BaseTool):
    """
    Tool to send emails to customers using templates.

    Simulates email sending by logging to console and database.
    """

    name: str = "SendEmail"
    description: str = """
    Send an email to the customer using a template.

    Templates available:
    - return_approved: Confirmation that return is approved with RMA details
    - return_rejected: Notification that return cannot be processed
    - label_ready: Shipping label is ready for download

    Input:
    - customer_email: Customer email address (required)
    - template_name: Name of the email template to use (required)
    - context: Dictionary of template variables (required)

    Returns:
    - message_id: Unique identifier for the sent message
    - preview: First 200 characters of the email
    - success: Boolean indicating success
    """

    args_schema: type[BaseModel] = SendEmailInput

    # Email templates
    TEMPLATES: ClassVar[Dict[str, str]] = {
        "return_approved": """
Dear {{ customer_name }},

Your return request has been approved!

Order Number: {{ order_number }}
RMA Number: {{ rma_number }}
Items: {{ items }}
Refund Amount: ${{ refund_amount }}

Your prepaid shipping label is ready. You can download it here:
{{ label_url }}

Tracking Number: {{ tracking_number }}

Please pack your items securely and drop off the package at any {{ carrier }} location.
Once we receive your return, we'll process your refund within 3-5 business days.

Thank you for your business!

Best regards,
Customer Service Team
""",
        "return_rejected": """
Dear {{ customer_name }},

Thank you for contacting us about your return request for Order #{{ order_number }}.

Unfortunately, we're unable to process this return because:
{{ reason }}

{{ additional_info }}

If you have any questions or would like to discuss alternatives, please don't hesitate to contact us.

Best regards,
Customer Service Team
""",
        "label_ready": """
Dear {{ customer_name }},

Your return shipping label is ready!

Order Number: {{ order_number }}
RMA Number: {{ rma_number }}
Tracking Number: {{ tracking_number }}

Download your label here: {{ label_url }}

Please print the label and attach it to your package. Drop it off at any {{ carrier }} location.

Thank you!

Best regards,
Customer Service Team
""",
    }

    def _generate_message_id(self) -> str:
        """Generate a unique message ID"""
        return f"MSG-{int(time.time())}-{hash(time.time()) % 10000}"

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        if template_name not in self.TEMPLATES:
            raise ValueError(f"Template '{template_name}' not found")

        template = Template(self.TEMPLATES[template_name])
        return template.render(**context)

    def _run(
        self,
        customer_email: str,
        template_name: str,
        context: dict,
    ) -> str:
        """Execute email sending"""
        try:
            # 1. Render template
            email_body = self._render_template(template_name, context)

            # 2. Generate message ID
            message_id = self._generate_message_id()

            # 3. Simulate sending (log to console)
            logger.info(f"Sending email to {customer_email} using template '{template_name}'")
            logger.debug(f"Email content:\n{email_body}")

            # 4. Log to database (optional, if session_id provided)
            if 'session_id' in context:
                try:
                    with get_db_session() as session:
                        log_entry = ConversationLog(
                            session_id=context['session_id'],
                            customer_id=context.get('customer_id'),
                            message_type=MessageType.SYSTEM,
                            content=f"Email sent: {template_name}",
                            meta_data=f'{{"template": "{template_name}", "message_id": "{message_id}"}}',
                        )
                        session.add(log_entry)
                        session.commit()
                except Exception as log_error:
                    logger.warning(f"Failed to log email to database: {log_error}")

            # 5. Return success with preview
            preview = email_body[:200].strip() + "..." if len(email_body) > 200 else email_body.strip()

            return SendEmailOutput(
                success=True,
                message_id=message_id,
                preview=preview,
                message=f"Email sent successfully to {customer_email}",
            ).model_dump_json()

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return SendEmailOutput(
                success=False,
                error=str(e),
                message="An error occurred while sending the email. Please try again.",
            ).model_dump_json()

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented, falls back to sync)"""
        return self._run(*args, **kwargs)
