# backend/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install system dependencies for python-magic
RUN apt-get update && apt-get install -y \
    curl \
    libmagic1 \
    iptables \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    --default-timeout=600 \
    --retries=10 \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Copy backend code
COPY . .

# Copy the firewall script into the container
COPY scripts/setup-firewall.sh /usr/local/bin/setup-firewall.sh
RUN chmod +x /usr/local/bin/setup-firewall.sh

# Expose backend port
EXPOSE 8000

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

RUN chown -R appuser:appgroup /app

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

USER appuser

# Run the backend server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
