# WealthOS: Setup Guide

This guide will help you set up the WealthOS development environment.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Docker and Docker Compose
- Git

## Backend Setup

1. Clone the Repository

```bash
git clone <https://github.com/yourusername/WealthOS.git>
cd WealthOS
```

2. Set Up Python Environment with uv

```bash
# Install uv
curl -sSf <https://astral.sh/uv/install.sh> | bash
# Create a virtual environment
uv venv .venv
# Activate the environment
source .venv/bin/activate # On Unix/macOS
# or
.venv\Scripts\activate # On Windows
# Install dependencies
cd backend
uv pip install -r requirements.txt
```

3. Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/WealthOS
# API Keys
AKSHARE_TOKEN=your_akshare_token
OPENAI_API_KEY=your_openai_api_key
# Security
SECRET_KEY=your_secret_key
```

4. Initialize the Database

```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres
# Run migrations
python -m scripts.init_db
```

5. Run the Backend Server

```bash
# Development mode
uvicorn app.main:app --reload
# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 4400
```

## Frontend Setup

1. Set Up Node.js Environment with pnpm

```bash
# Install pnpm
npm install -g pnpm
# Install dependencies
cd frontend
pnpm install
```

2. Set Up Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
# API
NEXT_PUBLIC_API_URL=<http://localhost:4400>
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
# Other services
NEXT_PUBLIC_POSTHOG_KEY=your_posthog_key
```

3. Run the Frontend Development Server

```bash
pnpm dev
```

The frontend will be available at `http://localhost:4300`.

## Docker Setup (Optional)

You can also run the entire application using Docker Compose:

```bash
# Build and start all services
docker-compose up -d
# View logs
docker-compose logs -f
```

## Development Workflow

### Code Formatting

```bash
# Backend
cd backend
black .
isort .
# Frontend
cd frontend
pnpm lint
pnpm format
```

### Running Tests

```bash
# Backend
cd backend
pytest
# Frontend
cd frontend
pnpm test
```
