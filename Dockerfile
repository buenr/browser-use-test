# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size
# Using --default-timeout to prevent timeouts during pip install
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8080 available to the world outside this container (if needed)
# EXPOSE 8080
# The current scripts don't seem to run a web server, so EXPOSE might not be necessary.
# If ProductHunt.py or fetch_headlines.py were to run a web service, this would be important.

# Define environment variables if needed (e.g., for API keys)
# ENV NAME placeholder_value
# For sensitive data like API keys, it's better to inject them at runtime via OpenShift secrets.

# Run ProductHunt.py when the container launches
# If fetch_headlines.py should be run, this CMD can be changed.
CMD ["python", "ProductHunt.py"]
