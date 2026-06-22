# Use an official Python slim image
FROM python:3.9-slim

WORKDIR /app

# Copy the gateway requirements and install them
COPY gateway/requirements.txt ./gateway_requirements.txt
RUN pip install --no-cache-dir -r ./gateway_requirements.txt

# Copy the gateway application code
COPY gateway/ /app/

# Copy the shared folder (located at backend/shared)
COPY shared/ /app/shared/

# Set PYTHONPATH so that "shared" is discoverable by Python
ENV PYTHONPATH=/app

# Run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
