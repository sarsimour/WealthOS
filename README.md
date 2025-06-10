# WealthOS

WealthOS is an all-in-one platform for financial analysis and investment across multiple asset classes, with a focus on the Chinese market. The platform unifies data handling, analysis, portfolio optimization, and reporting in a cohesive ecosystem enhanced by AI capabilities.

## Project Structure

This repository contains both the frontend and backend components of WealthOS:

- `frontend/`: Next.js application with TypeScript and Tailwind CSS
- `backend/`: FastAPI application with Python

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL
- Redis
- Docker (optional)

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment using `uv`:

```bash
curl -sSf https://astral.sh/uv/install.sh | bash
uv venv .venv
source .venv/bin/activate  # On Unix/macOS
```

3. Install dependencies:

```bash
uv pip install -e ".[dev]"
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:4400`.

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
pnpm install
```

3. Set up environment variables:

```bash
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

4. Run the development server:

```bash
pnpm dev
```

The application will be available at `http://localhost:4300`.

## Docker Setup (Optional)

You can also run the entire application using Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Development Roadmap

See [development_roadmap.md](development_roadmap.md) for the project timeline and milestones.

## Documentation

- [Project Overview](project_overview.md)
- [Architecture](architecture.md)
- [Core Components](core_components.md)
- [Core Principles](core_principles.md)
- [Tech Stack](tech_stack.md)
- [Setup Guide](setup_guide.md) # Portfolio auto-update test
