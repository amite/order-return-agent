"""Base tool class for all order return tools"""

from typing import ClassVar, Type

from langchain.tools import BaseTool
from pydantic import BaseModel


class OrderReturnBaseTool(BaseTool):
    """
    Base class for all Order Return Agent tools.

    Provides common functionality and structure for tools.
    """

    # Will be overridden by subclasses
    args_schema: ClassVar[Type[BaseModel]]

    def _format_error(self, error: Exception) -> str:
        """Format error message for user-friendly display"""
        return f"Error: {str(error)}"

    def _handle_exception(self, error: Exception) -> dict:
        """
        Handle exceptions consistently across all tools.

        Args:
            error: The exception that occurred

        Returns:
            Dictionary with error information
        """
        error_message = self._format_error(error)
        return {
            "success": False,
            "error": error_message,
            "message": "An error occurred while processing your request."
        }
