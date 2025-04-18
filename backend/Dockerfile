FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -sSf https://astral.sh/uv/install.sh | bash

# Copy requirements first to leverage Docker cache
COPY pyproject.toml .

# Install dependencies
RUN uv pip install -e .

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 4400

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4400"] 