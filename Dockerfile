# Use official lightweight Python image
FROM python:3.12.7-slim

# Install system dependencies needed by WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpangocairo-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev \
    libcairo2 shared-mime-info fonts-liberation2 curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory inside container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Expose the port your app runs on
EXPOSE 8000

# Command to run your app using Gunicorn
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:create_app()"]
CMD ["python", "app.py"]
