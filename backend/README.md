# WealthOS Backend

Backend services for the WealthOS financial analysis and investment platform.

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