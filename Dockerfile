# Use the official CUDA image from the Docker Hub
FROM nvidia/cuda:11.6.1-base-ubuntu20.04

# Set the working directory in the container
WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements-linux.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements-linux.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "main_page.py"]
