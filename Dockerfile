# Professional DEM Reconstruction & Coregistration App - Docker Image
# Based on Ubuntu with NASA Ames Stereo Pipeline (ASP) pre-installed

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV ASP_VERSION=3.6.0-alpha-2025-08-05

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    git \
    mercurial \
    subversion \
    python3 \
    python3-pip \
    python3-dev \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Download and install NASA Ames Stereo Pipeline (ASP)
WORKDIR /opt
RUN wget https://github.com/NeoGeographyToolkit/StereoPipeline/releases/download/2025-08-05-daily-build/StereoPipeline-${ASP_VERSION}-x86_64-Linux.tar.bz2 \
    && tar -xjf StereoPipeline-${ASP_VERSION}-x86_64-Linux.tar.bz2 \
    && rm StereoPipeline-${ASP_VERSION}-x86_64-Linux.tar.bz2 \
    && mv StereoPipeline-${ASP_VERSION}-x86_64-Linux asp

# Add ASP to PATH
ENV PATH="/opt/asp/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy application files
COPY professional_dem_app.py .
COPY README.md .
COPY DEPLOYMENT_GUIDE.md .

# Create directories for data processing
RUN mkdir -p /app/data /app/output /app/temp

# Set OpenTopography API key (will be overridden by environment variable)
ENV OPENTOPOGRAPHY_API_KEY=523da07408e277366b4b10399fc41d99

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "professional_dem_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
