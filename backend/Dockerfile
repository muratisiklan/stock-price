# Base image
FROM python:3.10-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /usr/src/

# Copy requirements first for better caching
COPY ./requirements.txt ./

# Install build dependencies, install Python packages, and clean up
RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc python3-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc python3-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . .

# Default command to run the application
CMD ["python", "-m", "app.main"]
