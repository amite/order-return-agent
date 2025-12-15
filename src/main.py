"""Main entry point for the Order Return Agent"""

import uuid
from pathlib import Path

from loguru import logger
from rich.console import Console

from src.agents.return_agent import ReturnAgent
from src.db.connection import init_database, check_database_exists
from src.db.seed import seed_database
from src.config.settings import settings
from src.ui.console import (
    print_welcome,
    get_user_input,
    print_agent_response,
    print_error,
    print_status,
    show_spinner,
)

# Create console instance for Rich output
console = Console()


def _setup_logging():
    """Configure logging for the application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.remove()  # Remove default handler
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="{message}",
        level=settings.log_level,
    )
    logger.add(
        sink=str(log_dir / "agent.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="500 MB",
    )


def _print_welcome():
    """Display welcome message and instructions"""
    print_welcome(console)


def main():
    """Main application entry point"""
    # Setup logging
    _setup_logging()
    logger.info("Starting Order Return Agent")

    # Initialize database
    try:
        db_exists = check_database_exists()
        init_database()
        logger.info("Database initialized")

        # Seed database if it's new
        if not db_exists:
            logger.info("New database detected. Seeding with sample data...")
            seed_database()
            logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        print_error(console, "Failed to initialize database", hint=str(e))
        return

    # Display welcome message
    _print_welcome()

    # Initialize agent
    session_id = str(uuid.uuid4())
    logger.info(f"Creating new agent session: {session_id}")
    print_status(console, f"Session created: {session_id[:8]}...", "success")

    try:
        agent = ReturnAgent(session_id=session_id)
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        print_error(
            console,
            "Failed to start agent",
            hint="Please ensure Ollama is running on http://localhost:11434"
        )
        return

    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = get_user_input(console)

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() == "/exit":
                print_status(console, "Thank you for using our service. Goodbye!", "success")
                logger.info(f"Session {session_id} ended by user")
                break

            if user_input.lower() == "/help":
                _print_welcome()
                continue

            if user_input.lower() == "/reset":
                session_id = str(uuid.uuid4())
                agent = ReturnAgent(session_id=session_id)
                print_status(console, "Conversation reset. Let's start over!", "success")
                _print_welcome()
                continue

            # Process user input through agent
            logger.debug(f"User input: {user_input}")

            # Show spinner while agent processes
            with show_spinner(console, "🤔 Agent is thinking..."):
                response = agent.run(user_input)

            # Display agent response with Rich formatting
            print_agent_response(console, response)

        except KeyboardInterrupt:
            print_status(console, "Session interrupted. Your conversation has been saved.", "info")
            logger.info(f"Session {session_id} interrupted by user")
            break

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            print_error(console, str(e), hint="Check logs/agent.log for details")
            print_status(console, "Attempting to continue...", "warning")


if __name__ == "__main__":
    main()
