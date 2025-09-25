FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml ./
RUN uv pip install --system fastmcp httpx uvicorn beautifulsoup4

# Copy application code
COPY main.py ./

# Expose port 8005
EXPOSE 8005

# Set environment variables
ENV PYTHONPATH=/app

# Run the server
CMD ["python", "main.py"]