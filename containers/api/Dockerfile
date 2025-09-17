# Use the official Python base image
FROM python:3.10-slim

RUN apt update -y && apt upgrade -y && \
    apt-get install -y python3-pip && \
    apt-get install -y gcc
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY src/requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir uvicorn
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the working directory
COPY src/ .

# Expose the port that FastAPI will run on
EXPOSE 8080

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]