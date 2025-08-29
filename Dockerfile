# Use Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for pdfminer
RUN apt-get update && apt-get install -y build-essential libpoppler-cpp-dev pkg-config python3-dev

# Copy project files
COPY server/ ./server/
COPY frontend/ ./frontend/
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
