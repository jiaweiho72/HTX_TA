FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    sox \
    libsox-fmt-all \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the necessary port
EXPOSE 8001

# Command to run the app
CMD ["uvicorn", "asr_api:app", "--host", "0.0.0.0", "--port", "8001"]
