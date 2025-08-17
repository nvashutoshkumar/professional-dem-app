# Streamlit Cloud Deployment Guide

## Files Required for Deployment

1. **`professional_dem_app.py`** - Main Streamlit application
2. **`requirements.txt`** - Python dependencies
3. **`packages.txt`** - System packages (wget, GDAL)
4. **`chandra_basin_coregistration_clean.py`** - Coregistration backend (if using)

## Streamlit Cloud Setup

### 1. Repository Structure
```
your-repo/
├── professional_dem_app.py    # Main app
├── requirements.txt           # Python deps
├── packages.txt              # System deps
├── chandra_basin_coregistration_clean.py  # Optional backend
└── README.md                 # Documentation
```

### 2. Environment Variables
Set in Streamlit Cloud settings:
- `OPENTOPOGRAPHY_API_KEY` = `523da07408e277366b4b10399fc41d99`

### 3. App Configuration
- **Main file**: `professional_dem_app.py`
- **Python version**: 3.9+
- **Resources**: 
  - Memory: 2GB+ (for DEM processing)
  - CPU: 2+ cores recommended

## Key Features for Cloud Deployment

### ✅ Session-Based Processing
- Uses `tempfile` and session-specific directories
- No hardcoded local paths
- Automatic cleanup

### ✅ Dynamic ASP Installation
- Downloads ASP binaries on first use
- Extracts to `/tmp/asp/`
- Adds to PATH automatically

### ✅ Error Handling
- Graceful fallbacks for missing tools
- Clear error messages for users
- Timeout protection

### ✅ File Management
- Handles uploaded files properly
- Temporary working directories
- Download links for results

## Limitations & Considerations

### Resource Limits
- **Processing Time**: Large ASTER files may timeout
- **Memory**: DEM processing is memory-intensive
- **Storage**: Limited to session temporary files

### Alternative Deployment Options
1. **Heroku**: More resources, custom buildpacks
2. **AWS/GCP**: Full control, unlimited resources  
3. **Local Docker**: For development/testing

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run professional_dem_app.py
```

## Monitoring & Debugging

- Check Streamlit Cloud logs for ASP installation
- Monitor memory usage during processing
- Test with small ASTER files first
