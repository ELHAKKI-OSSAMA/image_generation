FROM python:3.9-slim

WORKDIR /app

# Copy the Image Service requirements and install them
COPY services/image_service/requirements.txt ./image_requirements.txt
RUN pip install --no-cache-dir -r ./image_requirements.txt

# Copy the Image Service code
COPY services/image_service/ /app/

# Copy the shared folder so the service can import it
COPY shared/ /app/shared/

# Ensure the shared module is on the PYTHONPATH
ENV PYTHONPATH=/app

# Run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
