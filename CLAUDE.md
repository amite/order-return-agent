# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an "order-return-agent" Python project that uses `uv` as the package manager. The project is currently a minimal boilerplate with a structured directory layout designed for data science/ML workflows.

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies (first time setup)
uv sync

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>
```

### Running the Application
```bash
# Run the main entry point
uv run python -m src.main
```

### Testing
```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_basic.py

# Run a specific test
uv run pytest tests/test_basic.py::test_placeholder

# Run with coverage
uv run pytest --cov=src
```

### Code Quality
```bash
# Format code with black
uv run black src/ tests/

# Lint with ruff
uv run ruff check src/ tests/

# Fix linting issues
uv run ruff check --fix src/ tests/
```

## Architecture

### Directory Structure

The project follows a structured organization optimized for data science and research workflows:

- **`src/`** - Main application code and modules
  - `src/main.py` - Primary entry point with `main()` function
  - Import modules using `from src.module import ...`

- **`tests/`** - Test suite (pytest)
  - `tests/test_basic.py` validates project structure

- **Data and Analysis Directories**:
  - **`notebooks/`** - Jupyter notebooks for exploratory analysis
  - **`data/`** - Data files (not committed to git)
  - **`research/`** - Research notes and experiments
  - **`artifacts/`** - Generated outputs
    - `artifacts/wip/` - Work in progress artifacts
    - `artifacts/completed/` - Final artifacts
  - **`reports/`** - Generated reports and documentation
  - **`quality/`** - Quality assurance artifacts
  - **`scripts/`** - Utility scripts

### Key Patterns

- **Package Manager**: This project uses `uv`, not pip or poetry. Always use `uv` commands.
- **Module Structure**: The `src/` directory is a package. Use `python -m src.main` to run, not `python src/main.py`.
- **Testing**: Tests validate the directory structure exists (see `tests/test_basic.py:test_project_structure`).
- **Python Version**: Requires Python >=3.10.

### Development Dependencies

The project includes these dev tools in pyproject.toml:
- `pytest` + `pytest-cov` for testing
- `black` for code formatting
- `ruff` for linting
- `ipykernel` for Jupyter notebook support

# Rules

## Python Execution - CRITICAL

**IMPORTANT**: Always use `uv run` to execute Python commands. NEVER use plain `python` command.

**Why**: The project uses `uv` which manages the project's `.venv` virtual environment. Using bare `python` may invoke the system Python or wrong version, causing import errors and missing dependencies.

**Correct**:
```bash
uv run python -m src.main
uv run python -c "from src.agents.return_agent import ReturnAgent"
uv run pytest tests/
uv run python -m py_compile src/agents/return_agent.py
```

**WRONG** (do not do this):
```bash
python -m src.main                      # ❌ Wrong Python interpreter
python -c "from src..."                 # ❌ Missing project dependencies
pytest tests/                           # ❌ Tests may fail
```

## Documentation Lookups

*   **LangChain Questions**: For any question related to "langchain", "langgraph", "langsmith", or "LCEL", automatically invoke the `docs-langchain` MCP server to find the answer.
    - Example: Import paths, API usage, integration patterns
    - Use: `mcp__docs-langchain__SearchDocsByLangChain` tool
    - When: Before implementing any LangChain feature

*   **Library Documentation**: For any other library (numpy, pandas, fastapi, etc.), consider using `mcp__context7__resolve-library-id` and `mcp__context7__get-library-docs` to get up-to-date documentation.
    - Check official docs first before relying on memory
    - Especially useful for: version-specific features, API changes
    - When: Integrating new libraries or uncertain about API

## Ollama Commands

*   All Ollama commands must be executed from `/home/amite/code/docker/ollama-docker/` directory:
    ```bash
    cd /home/amite/code/docker/ollama-docker && docker compose exec ollama ollama list
    ```
