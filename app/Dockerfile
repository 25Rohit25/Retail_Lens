FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for PostgreSQL and OpenCV
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend source code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Command to run FastAPI using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
