# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY resolver_service.py .

# Expose port 8000
EXPOSE 8000

# Run the app using uvicorn server
CMD ["uvicorn", "resolver_service:app", "--host", "0.0.0.0", "--port", "8000"]
