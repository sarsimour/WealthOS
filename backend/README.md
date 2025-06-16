# Backend Setup

This directory contains the FastAPI backend for the WealthOS application.

## Environment

- **Python Version**: 3.12 (as specified in rules)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Virtual Environment**: A virtual environment managed by `uv` is expected to be active within this directory (e.g., `.venv`).

## Getting Started

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```
2.  **Activate the virtual environment**:
    *   If using `uv`'s default `.venv`:
        ```fish
        source .venv/bin/activate.fish
        ```
        (Adjust path and shell command if your setup differs)
3.  **Install dependencies**:
    ```bash
    uv pip install -r requirements.txt  # Or uv sync if using uv.lock
    ```
4.  **Run the application** (Details TBD - e.g., using uvicorn)

## Dependencies

Key dependencies are managed using `uv` and should be listed in `requirements.txt` (or `pyproject.toml` if using that structure with `uv`).

## Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL
- Redis

### Installation

1. Create a virtual environment using `uv`:

```bash
curl -sSf https://astral.sh/uv/install.sh | bash
uv venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:

```bash
uv pip install -e ".[dev]"
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:4400`.

## Development

### Code Formatting

```bash
black .
isort .
```

### Linting

```bash
ruff check .
mypy .
```

### Testing

```bash
pytest
```

## Project Structure

- `app/`: Main application package
  - `api/`: API endpoints
  - `core/`: Core functionality and base classes
  - `data/`: Data acquisition and storage
  - `factors/`: Factor implementations
  - `portfolio/`: Portfolio construction and analysis
  - `ml/`: Machine learning models
  - `market_monitor/`: Market monitoring
  - `reporting/`: Reporting and visualization
  - `utils/`: Utility functions 