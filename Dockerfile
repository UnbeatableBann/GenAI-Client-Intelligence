FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install required system dependencies (for building some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for blazingly fast dependency management
RUN pip install uv

# Set the working directory
WORKDIR /app

# Copy the project configuration and the generated lockfile first
COPY pyproject.toml uv.lock ./

# Install the dependencies precisely according to uv.lock (without dev dependencies)
RUN uv sync --frozen --no-dev

# Copy the rest of the application files
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Run the Streamlit application using uv
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.address=0.0.0.0"]
