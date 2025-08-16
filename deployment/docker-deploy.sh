#!/bin/bash

# Build the Docker image
docker build -t vn-stock-advisory .

# Stop and remove any existing container
docker stop vn-stock-advisory || true
docker rm vn-stock-advisory || true

# Run the Docker container
docker run -d \
  --name vn-stock-advisory \
  --env-file .env \
  -p 8000:8000 \
  vn-stock-advisory

# Print the logs of the running container
docker logs -f vn-stock-advisory