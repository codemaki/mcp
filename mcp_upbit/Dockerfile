# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY mcp_upbit/ ./mcp_upbit/

# Install dependencies using uv
RUN uv sync

# Expose port (default 10000, configurable via environment)
EXPOSE ${PORT:-10000}

# Set default environment variables
ENV HOST=0.0.0.0
ENV PORT=10000

# Run the FastMCP server with StreamableHTTP
CMD ["uv", "run", "python", "-m", "mcp_upbit.fastmcp_server"]