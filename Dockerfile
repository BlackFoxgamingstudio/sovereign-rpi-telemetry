# Multi-stage lightweight container for sovereign-rpi-telemetry
FROM python:3.11-slim as runtime

WORKDIR /app

# Install system utilities if needed for sysfs / ps
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY n8n/ ./n8n/

# Install in editable mode
RUN pip install --no-cache-dir -e .

EXPOSE 8770

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8770/healthz || exit 1

ENV PYTHONUNBUFFERED=1
ENV SBB_RPI_PORT=8770

ENTRYPOINT ["python3", "n8n/webhook_adapter.py"]
