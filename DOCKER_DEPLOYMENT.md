# Docker Deployment Guide

## 🐳 Full Functionality Docker Deployment

This Docker setup provides **complete ASP functionality** with all NASA Ames Stereo Pipeline tools pre-installed.

## 🚀 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (usually included with Docker)
- At least 4GB RAM available
- 10GB free disk space

### 1. Clone Repository
```bash
git clone https://github.com/nvashutoshkumar/professional-dem-app.git
cd professional-dem-app
```

### 2. Build and Run
```bash
# Build and start the application
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 3. Access Application
Open your browser to: **http://localhost:8501**

## 🔧 Manual Docker Commands

### Build Image
```bash
docker build -t professional-dem-app .
```

### Run Container
```bash
docker run -p 8501:8501 \
  -e OPENTOPOGRAPHY_API_KEY=your_api_key_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  professional-dem-app
```

## 📁 Directory Structure

```
professional-dem-app/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-container setup
├── professional_dem_app.py # Main application
├── requirements.txt        # Python dependencies
├── data/                   # Input ASTER files (mounted)
├── output/                 # Generated DEMs (mounted)
└── temp/                   # Processing workspace (mounted)
```

## 🛠️ What's Included in Docker Image

### System Components
- **Ubuntu 22.04** base image
- **NASA ASP 3.6.0-alpha** pre-installed
- **GDAL/OGR** geospatial libraries
- **Python 3.10** with all dependencies

### ASP Tools Available
- `aster2asp` - ASTER to ASP conversion
- `stereo` - Stereo processing
- `point2dem` - Point cloud to DEM conversion
- `pc_align` - Point cloud alignment
- `geodiff` - DEM comparison and validation

### Python Libraries
- Streamlit web framework
- Rasterio for raster processing
- GeoPandas for geospatial operations
- SlideRule for ICESat-2 data
- All visualization libraries (Plotly, Folium)

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENTOPOGRAPHY_API_KEY` | OpenTopography API key | Required |
| `STREAMLIT_SERVER_PORT` | Application port | 8501 |
| `STREAMLIT_SERVER_ADDRESS` | Bind address | 0.0.0.0 |

## 💾 Data Persistence

### Volume Mounts
- `./data:/app/data` - Input ASTER L1A files
- `./output:/app/output` - Generated DEM outputs
- `./temp:/app/temp` - Processing workspace

### Usage
1. Place ASTER L1A zip files in `./data/` directory
2. Upload through web interface or process directly
3. Find outputs in `./output/` directory

## 🔍 Monitoring & Logs

### View Logs
```bash
# Real-time logs
docker-compose logs -f

# Container logs
docker logs professional-dem-app_dem-app_1
```

### Health Check
```bash
# Check container health
docker-compose ps

# Manual health check
curl http://localhost:8501/_stcore/health
```

## 🚀 Production Deployment

### Cloud Deployment Options

#### 1. AWS ECS/Fargate
```bash
# Build for AWS
docker build -t your-account.dkr.ecr.region.amazonaws.com/dem-app .
docker push your-account.dkr.ecr.region.amazonaws.com/dem-app
```

#### 2. Google Cloud Run
```bash
# Build for GCP
docker build -t gcr.io/your-project/dem-app .
docker push gcr.io/your-project/dem-app
gcloud run deploy --image gcr.io/your-project/dem-app --port 8501
```

#### 3. Azure Container Instances
```bash
# Build for Azure
docker build -t your-registry.azurecr.io/dem-app .
docker push your-registry.azurecr.io/dem-app
```

### Resource Requirements

#### Minimum
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB

#### Recommended
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ (for large datasets)

## 🛠️ Customization

### Custom API Key
```bash
# Set your OpenTopography API key
export OPENTOPOGRAPHY_API_KEY="your_api_key_here"
docker-compose up
```

### Custom Port
```yaml
# In docker-compose.yml
ports:
  - "8080:8501"  # Use port 8080 instead
```

### Development Mode
```bash
# Mount source code for development
docker run -p 8501:8501 \
  -v $(pwd):/app \
  professional-dem-app
```

## 🐛 Troubleshooting

### Common Issues

#### Build Fails
```bash
# Clean build
docker system prune -a
docker-compose build --no-cache
```

#### ASP Tools Not Found
```bash
# Check ASP installation in container
docker exec -it container_name which aster2asp
docker exec -it container_name ls /opt/asp/bin/
```

#### Memory Issues
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory > 8GB+
```

#### Permission Issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./data ./output ./temp
```

## 📊 Performance Tips

1. **Use SSD storage** for Docker volumes
2. **Allocate sufficient RAM** (8GB+ recommended)
3. **Use multi-stage builds** for smaller images
4. **Enable BuildKit** for faster builds:
   ```bash
   export DOCKER_BUILDKIT=1
   ```

## 🔒 Security Considerations

1. **Don't expose API keys** in Dockerfile
2. **Use environment variables** for secrets
3. **Run as non-root user** in production
4. **Keep base image updated** regularly
5. **Scan for vulnerabilities**:
   ```bash
   docker scan professional-dem-app
   ```

---

**🎉 With Docker, you get full ASP functionality with professional DEM processing capabilities!**
