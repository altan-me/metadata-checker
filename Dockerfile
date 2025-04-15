# Dockerfile

# ---- Base Stage ----
# Use a specific Python version. Using slim variants reduces image size.
FROM python:3.13-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed by some python packages
# (Optional, but can prevent issues with packages that compile C extensions)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy just the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install python dependencies
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt


# ---- Final Stage ----
# Use the same slim base image for the final stage
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Create a non-root user and group
# Running as non-root is a security best practice
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

# Copy installed dependencies from the base stage
COPY --from=base /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy the application code
COPY app.py .

# Ensure the app directory is owned by the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application using Gunicorn
# Binds to all interfaces on the specified port
# 'app:app' means: look for the 'app' variable (Flask instance) inside the 'app.py' module
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
