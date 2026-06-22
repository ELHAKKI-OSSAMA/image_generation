FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3.9 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the shared module and make it accessible
COPY shared/ /app/shared/
ENV PYTHONPATH=/app

# Copy service directories
COPY services/ /app/services/
COPY gateway/ /app/gateway/

# Each service will override this with their specific command
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]