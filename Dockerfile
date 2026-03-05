FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install katana (Go-based web crawler from ProjectDiscovery)
# Download the latest release for Linux amd64
RUN curl -sSL https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_linux_amd64.zip -o /tmp/katana.zip \
    && unzip /tmp/katana.zip -d /tmp/ \
    && mv /tmp/katana /usr/local/bin/katana \
    && chmod +x /usr/local/bin/katana \
    && rm /tmp/katana.zip

# Verify katana is installed
RUN katana -version

WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# CRITICAL: Set environment for proper binding
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose the port (Render will set PORT env var)
EXPOSE 8000

CMD ["python", "server.py"]
