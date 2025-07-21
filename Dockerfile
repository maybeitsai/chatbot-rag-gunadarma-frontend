# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Create virtual environment
RUN uv venv --python 3.12

# Copy uv configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN . .venv/bin/activate && uv sync --no-cache

# Copy application code
COPY . .

# Expose port 8080
EXPOSE 8080

# Create a non-root user for security
RUN useradd -m -u 1000 chainlit && chown -R chainlit:chainlit /app
USER chainlit

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080 || exit 1

# Run the Chainlit application with debugging enabled
CMD ["uv", "run", "chainlit", "run", "app.py", "-w", "--port", "8080", "--host", "0.0.0.0"]