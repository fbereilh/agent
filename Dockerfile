# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY agent/ ./agent/
COPY search/ ./search/
COPY main.py ./

# Copy environment template (users should mount their own .env)
COPY .env.example ./

# Expose port
EXPOSE 5001

# Run the application
CMD ["uv", "run", "python", "main.py"]
