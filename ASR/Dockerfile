FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 3001
EXPOSE 3001

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]