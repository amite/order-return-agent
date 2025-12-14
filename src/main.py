"""Main entry point for the Order Return Agent"""

import uuid
from pathlib import Path

from loguru import logger

from src.agents.return_agent import ReturnAgent
from src.db.connection import init_database, check_database_exists
from src.db.seed import seed_database
from src.config.settings import settings


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
    print("\n" + "=" * 70)
    print("  ORDER RETURN AGENT - Customer Service Assistant".center(70))
    print("=" * 70)
    print()
    print("Welcome! I'm here to help you process your order return.")
    print()
    print("To get started, please provide:")
    print("  • Your order number, OR")
    print("  • Your email address")
    print()
    print("Commands:")
    print("  /exit  - End the conversation")
    print("  /help  - Show this message again")
    print("  /reset - Start a new conversation")
    print()
    print("-" * 70)
    print()


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
        print("Error: Failed to initialize database")
        return

    # Display welcome message
    _print_welcome()

    # Initialize agent
    session_id = str(uuid.uuid4())
    logger.info(f"Creating new agent session: {session_id}")

    try:
        agent = ReturnAgent(session_id=session_id)
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        print(f"Error: Failed to start agent: {e}")
        print("Please ensure Ollama is running locally on http://localhost:11434")
        return

    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() == "/exit":
                print(
                    "\nThank you for using our service. Your session has been saved. Goodbye!"
                )
                logger.info(f"Session {session_id} ended by user")
                break

            if user_input.lower() == "/help":
                _print_welcome()
                continue

            if user_input.lower() == "/reset":
                session_id = str(uuid.uuid4())
                agent = ReturnAgent(session_id=session_id)
                print("\nConversation reset. Let's start over!")
                _print_welcome()
                continue

            # Process user input through agent
            logger.debug(f"User input: {user_input}")
            response = agent.run(user_input)

            # Display agent response
            print(f"\nAgent: {response}")

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Your conversation has been saved.")
            logger.info(f"Session {session_id} interrupted by user")
            break

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            print(f"\nError: {e}")
            print("Attempting to continue...")


if __name__ == "__main__":
    main()
