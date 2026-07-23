# -------------------------------------
# Stage 1: Builder
# -------------------------------------
FROM python:3.12-slim AS builder

# Set env vars to prevent writing pyc files and enable uv bytecode compilation
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

WORKDIR /app

# Copy dependency files first to maximize Docker layer caching
COPY pyproject.toml uv.lock ./

# Sync dependencies into a local virtual environment (.venv)
RUN uv sync --frozen --no-dev


# -------------------------------------
# Stage 2: Runtime
# -------------------------------------
FROM python:3.12-slim

# Add the virtual environment to PATH so python/streamlit commands work automatically
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Install only essential runtime dependencies (e.g. libpq5 for DB drivers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy ONLY the optimized virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the rest of the application code
COPY . .

# Default port if not provided by Railway
ENV PORT=8501
EXPOSE $PORT

# Run using shell to correctly evaluate the $PORT variable provided by Railway
CMD sh -c "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
