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
