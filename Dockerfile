# Use the specific version the script was developed with
FROM python:3.13-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create a non-root user
RUN groupadd -r ddns && useradd -r -g ddns ddns

# Install system dependencies for miniupnpc
#   (C extension needs build tools, but a multi-stage build is possible)
FROM base AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first — utilises Docker layer caching
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install uv && \
    uv sync --frozen --no-dev

# --- Final stage ---
FROM base

WORKDIR /app

# Copy only the built venv from builder (results in a smaller final image)
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY ddns/ ./ddns/

# Switch to non-root user
USER ddns

# Use the venv's Python
ENV PATH="/app/.venv/bin:$PATH"

# Run the script with -u to signify unbuffered output (logs dont show in certain container managers otherwise)
CMD ["python", "-u", "ddns/main.py"]

# Check for the file /tmp/ddns_healthy which is put there every successful run
HEALTHCHECK --interval=60s --timeout=5s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/tmp/ddns_healthy') else 1)"
