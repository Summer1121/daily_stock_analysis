<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AGENTS.md - AI Coding Assistant Guide

This file provides guidelines for AI coding assistants working in this repository.

## Project Overview

This is an A-share/H-share stock analysis system with AI-powered decision dashboards. The backend is Python-based (Python 3.10+), with a Vue.js frontend web UI.

## Build/Lint/Test Commands

### Python Backend

```bash
# Install dependencies
pip install -r requirements.txt
pip install black flake8 isort bandit

# Code formatting
black .                              # Format all Python files
isort .                              # Sort imports

# Static analysis
flake8 .                             # Full linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics  # Critical errors only
bandit -r . -x ./test_*.py           # Security scan

# Syntax check (without running)
python -m py_compile <file.py>

# Run tests
pytest                                # Run all tests
pytest tests/                         # Run all tests in tests directory
pytest -v                            # Verbose output
pytest -k "test_name"                # Run specific test by name
pytest --collect-only                # List tests without running
pytest -m "not slow"                 # Skip slow tests
pytest -m integration                # Run only integration tests
```

### Running a Single Test

```bash
# Run a specific test file
pytest tests/e2e/test_pages.py

# Run a specific test function
pytest tests/e2e/test_pages.py::test_homepage_loads

# Run tests matching a pattern
pytest -k "homepage"
```

### Vue.js Frontend

```bash
cd web/frontend

# Install dependencies
npm install

# Development
npm run dev

# Build
npm run build

# Preview
npm run preview
```

### Docker

```bash
# Build Docker image
docker build -t stock-analysis:test .

# Run container
docker run --rm stock-analysis:test python -c "print('OK')"
```

## Code Style Guidelines

### General Principles

- Follow PEP 8 for Python code
- Use Python 3.10+ features (dataclasses, pattern matching where appropriate)
- Keep functions small and focused (< 100 lines preferred)
- Add docstrings to all public functions and classes

### Formatting

- **Line length**: 120 characters (configured in pyproject.toml)
- **Indentation**: 4 spaces (no tabs)
- **Black** is the source of truth for formatting
- **isort** for import sorting (profile: black)

### Imports

Order (as enforced by isort):
1. Standard library
2. Third-party packages
3. Local application imports

```python
# Example
import os
from pathlib import Path
from typing import List, Optional

import requests
from dotenv import load_dotenv

from config import Config
from storage import DatabaseManager
```

### Naming Conventions

- **Variables/functions**: snake_case (`stock_list`, `get_config()`)
- **Classes**: PascalCase (`Config`, `DatabaseManager`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private members**: prefix with underscore (`_internal_method`)

### Types

- Use type hints for all function signatures
- Use `Optional[X]` instead of `X | None` for compatibility
- Use dataclasses for structured data

```python
from typing import List, Optional, Dict
from dataclasses import dataclass, field

@dataclass
class StockInfo:
    code: str
    name: str
    price: float = 0.0
    tags: List[str] = field(default_factory=list)

def get_stock(code: str) -> Optional[StockInfo]:
    ...
```

### Error Handling

- Use custom exceptions for domain-specific errors
- Catch specific exceptions, not bare `Exception`
- Log errors before re-raising
- Use defensive programming with early returns

```python
try:
    result = fetch_data(code)
except ConnectionError as e:
    logger.error(f"Failed to connect: {e}")
    raise NetworkError(f"Cannot fetch {code}") from e
except ValueError as e:
    logger.warning(f"Invalid data for {code}: {e}")
    return None
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of what the function does.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is invalid.
    """
```

### File Headers

Include encoding declaration and module docstring:

```python
# -*- coding: utf-8 -*-
"""
Module name - Brief description of module purpose.

Extended description if needed.
"""
```

### Git Commit Messages

Follow Conventional Commits:

```
feat: add new feature
fix: bug fix
docs: documentation update
style: formatting (no code change)
refactor: code refactoring
perf: performance improvement
test: test-related changes
chore: build/tooling changes
```

### Testing

- Write tests for new features
- E2E tests use Playwright (in `tests/e2e/`)
- Mark slow tests with `@pytest.mark.slow`
- Mark integration tests with `@pytest.mark.integration`

### Security

- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive config
- Run Bandit before committing: `bandit -r . -x ./test_*.py`
- Validate all inputs from external sources

### Dependencies

- Pin major versions in requirements.txt
- Check for vulnerabilities: `pip install safety && safety check`

## Directory Structure

```
daily_stock_analysis/
├── main.py                 # Entry point
├── config.py               # Configuration
├── analyzer.py             # AI analyzer (Gemini)
├── market_analyzer.py     # Market analysis
├── search_service.py      # News search
├── notification.py         # Notifications
├── storage.py             # Data storage
├── scheduler.py           # Scheduled tasks
├── webui.py               # WebUI entry
├── data_provider/         # Data source adapters
│   ├── akshare_fetcher.py
│   ├── tushare_fetcher.py
│   ├── baostock_fetcher.py
│   └── yfinance_fetcher.py
├── web/                   # WebUI backend
│   ├── server.py
│   ├── router.py
│   ├── handlers.py
│   └── api/               # API endpoints
├── trading/               # Trading logic
│   ├── brokers/           # Broker implementations
│   ├── strategy.py
│   └── backtester.py
├── analysis/              # Analysis orchestration
│   └── agents/            # AI agents
├── tests/                 # Test suite
│   └── e2e/               # End-to-end tests
└── web/frontend/          # Vue.js frontend
```

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs on PRs:
- Python syntax check
- Module import tests
- Critical error detection (flake8 --select=E9,F63,F7,F82)
- Docker build test

## Additional Resources

- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- [README.md](./README.md) - Project documentation
- [docs/](./docs/) - Detailed documentation
- [openspec/](./openspec/) - Specification documents
