"""Rich console utilities for Order Return Agent CLI"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

# Styling constants
USER_STYLE = "cyan"
AGENT_STYLE = "green"
ERROR_STYLE = "red bold"
SUCCESS_STYLE = "green"
INFO_STYLE = "blue"
WARNING_STYLE = "yellow"


def print_welcome(console: Console) -> None:
    """Display welcome screen with Rich Panel

    Creates an attractive welcome banner with the agent introduction,
    instructions for getting started, and available commands.
    """
    content = """
🤖 **ORDER RETURN AGENT** - Customer Service Assistant

Welcome! I'm here to help you process your order return.

**To get started, please provide:**
• Your order number, OR
• Your email address

**Commands:**
• `/exit`  - End the conversation
• `/help`  - Show this message again
• `/reset` - Start a new conversation
    """
    panel = Panel(
        Markdown(content),
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)


def get_user_input(console: Console) -> str:
    """Get styled user input with Rich Prompt

    Displays a stylized prompt for user input with emoji and cyan color.

    Args:
        console: Rich Console instance

    Returns:
        Stripped user input string
    """
    return Prompt.ask("[cyan]👤 You[/cyan]").strip()


def print_agent_response(console: Console, response: str) -> None:
    """Display agent response in styled panel with markdown

    Renders the agent's response in a green-bordered panel with markdown
    formatting support for enhanced readability.

    Args:
        console: Rich Console instance
        response: Agent response text
    """
    md = Markdown(response)
    panel = Panel(
        md,
        title="🤖 Agent",
        title_align="left",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()  # Add spacing after agent response


def print_error(console: Console, message: str, hint: str = None) -> None:
    """Display error in red panel with optional hint

    Shows error messages in a prominent red-bordered panel with
    an optional helpful hint for troubleshooting.

    Args:
        console: Rich Console instance
        message: Error message to display
        hint: Optional troubleshooting hint
    """
    content = f"❌ {message}"
    if hint:
        content += f"\n\n💡 Hint: {hint}"
    panel = Panel(
        content,
        border_style="red bold",
        padding=(1, 2)
    )
    console.print(panel)


def print_status(console: Console, message: str, status: str = "info") -> None:
    """Print status message with appropriate styling

    Displays a status message with color-coded styling and emoji icons
    based on the status type (success, info, warning, error).

    Args:
        console: Rich Console instance
        message: Status message to display
        status: Status type - 'success', 'info', 'warning', or 'error'
    """
    icons = {
        "success": "✓",
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌"
    }
    colors = {
        "success": "green",
        "info": "blue",
        "warning": "yellow",
        "error": "red"
    }
    icon = icons.get(status, "ℹ️")
    color = colors.get(status, "blue")
    console.print(f"[{color}]{icon} {message}[/{color}]")


def show_spinner(console: Console, message: str = "Processing..."):
    """Context manager for showing spinner during long operations

    Returns a context manager that displays an animated spinner
    while code within the context is executing.

    Args:
        console: Rich Console instance
        message: Message to display while processing

    Returns:
        Console status context manager
    """
    return console.status(f"[cyan]{message}[/cyan]", spinner="dots")
