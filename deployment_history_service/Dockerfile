# Use the official Python image from the Docker Hub
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8001

# Run the application
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]