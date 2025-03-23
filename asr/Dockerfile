FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ../requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY asr_api.py .

# Expose the port
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "asr_api:app", "--host", "0.0.0.0", "--port", "8001"]
