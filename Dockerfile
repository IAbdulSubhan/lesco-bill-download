# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for headless Chrome (required for Selenium)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libx11-dev \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    libvulkan1 \  # This is the missing dependency for Google Chrome
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (for headless mode)
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -fy

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for Flask to run
EXPOSE 5000

# Run Flask app when container starts
CMD ["python", "app.py"]
