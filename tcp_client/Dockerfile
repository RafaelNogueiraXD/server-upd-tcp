# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY tcp_client.py /app/

# Install any needed packages specified in requirements
RUN pip install --no-cache-dir typing-extensions

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define default environment variables
ENV HOST=localhost
ENV PORT=5000
ENV REQUESTS=10000

# Run the script when the container launches
ENTRYPOINT ["python", "tcp_client.py", \
            "--requests", "1000", \
            "--save-results"]