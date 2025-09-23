FROM python:3.11-slim

# Install uv and curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY .python-version .
COPY uv.lock .
COPY src/ ./src/

# Install dependencies with uv
RUN uv sync --frozen

# Create non-root user and change ownership
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port for HTTP server
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["uv", "run", "python", "src/finance_server.py"]