# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .
COPY setup.py .

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install the package (this is needed to treat src as a module)
RUN pip install -e .

# Copy only the src folder into the container
COPY src/ ./src/

# Specify the command to run on container start
CMD ["python", "src/main.py"]