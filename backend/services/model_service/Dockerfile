FROM python:3.9-slim

WORKDIR /app

# Copy the Model Service requirements and install them
COPY services/model_service/requirements.txt ./model_requirements.txt
RUN pip install --no-cache-dir -r ./model_requirements.txt

# Copy the Model Service code
COPY services/model_service/ /app/

# Copy the shared folder so that it’s included in the container
COPY shared/ /app/shared/

# Set PYTHONPATH so that the shared folder is found
ENV PYTHONPATH=/app

# Run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
