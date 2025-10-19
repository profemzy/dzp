# Multi-stage build for DZP IAC Agent
FROM python:3.13-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gnupg \
    lsb-release \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update && apt-get install -y terraform \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only dependency files first (for better caching)
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies using pip
RUN pip install --no-cache-dir -e .

# Final stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install runtime dependencies and Terraform
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gnupg \
    lsb-release \
    wget \
    && wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update && apt-get install -y terraform \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Create directory for Terraform files
RUN mkdir -p /terraform

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Expose ports
# 8080 - Web interface
# 8000 - API server
EXPOSE 8080 8000

# Default command (can be overridden)
CMD ["dzp-web", "--host", "0.0.0.0", "--port", "8080"]
