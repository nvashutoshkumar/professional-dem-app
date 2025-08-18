#!/usr/bin/env python3
"""
Simple DEM App - Exact same logic as process_aster_dem.py but with corrected commands
Uses the proven commands that produce 5143.9m elevation
"""

import streamlit as st
import os
import sys
import glob
import zipfile
import subprocess
import numpy as np
import tempfile
import shutil
from pathlib import Path

# Try to import rasterio
try:
    import rasterio
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    st.warning("⚠️ Rasterio not available - some features may be limited")

def setup_environment():
    """Set up the ASP environment"""
    # In cloud, ASP should be in PATH from Docker
    return True

def extract_aster_data(zip_file, output_dir):
    """Extract ASTER L1A zip file - EXACT same as process_aster_dem.py"""
    st.info(f"📦 Extracting {os.path.basename(zip_file)}...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    # Find the extracted directory
    extracted_dirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    if extracted_dirs:
        return os.path.join(output_dir, extracted_dirs[0])
    else:
        return output_dir

def process_aster_to_asp(aster_dir, output_prefix):
    """Convert ASTER L1A to ASP format using aster2asp - EXACT same as process_aster_dem.py"""
    st.info(f"🔄 Converting ASTER data to ASP format...")
    
    # Create output directory
    output_dir = os.path.dirname(output_prefix)
    os.makedirs(output_dir, exist_ok=True)
    
    # Run aster2asp command
    cmd = f"aster2asp {aster_dir} -o {output_prefix}"
    st.code(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            st.success("✅ aster2asp completed successfully!")
            return True
        else:
            st.error(f"❌ aster2asp failed with error: {result.stderr}")
            return False
    except Exception as e:
        st.error(f"❌ Error running aster2asp: {e}")
        return False

def run_stereo_processing(left_image, right_image, left_camera, right_camera, output_prefix):
    """Run stereo processing - CORRECTED with ASTER parameters"""
    st.info("🛰️ Running stereo processing...")
    
    # CORRECTED: Use ASTER-specific parameters that we know work
    cmd = f"stereo -t aster --stereo-algorithm asp_bm --subpixel-mode 1 {left_image} {right_image} {left_camera} {right_camera} {output_prefix}"
    st.code(f"Running: {cmd}")
    
    try:
        # Set up environment for headless operation (cloud deployment)
        env = os.environ.copy()
        env['DISPLAY'] = ':99'
        env['QT_QPA_PLATFORM'] = 'offscreen'
        env['LIBGL_ALWAYS_INDIRECT'] = '1'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, timeout=3600)
        if result.returncode == 0:
            st.success("✅ Stereo processing completed successfully!")
            return True
        else:
            st.error(f"❌ Stereo processing failed with return code: {result.returncode}")
            st.error(f"**Error output:**\n```\n{result.stderr}\n```")
            if result.stdout:
                st.info(f"**Standard output:**\n```\n{result.stdout}\n```")
            
            # Add diagnostic information
            st.info("🔍 **Diagnostic Information:**")
            st.code(f"Command: {cmd}")
            st.code(f"Left image exists: {os.path.exists(left_image)}")
            st.code(f"Right image exists: {os.path.exists(right_image)}")
            st.code(f"Left camera exists: {os.path.exists(left_camera)}")
            st.code(f"Right camera exists: {os.path.exists(right_camera)}")
            st.code(f"Output directory exists: {os.path.exists(os.path.dirname(output_prefix))}")
            
            return False
    except subprocess.TimeoutExpired:
        st.error("❌ Stereo processing timed out (>1 hour)")
        return False
    except Exception as e:
        st.error(f"❌ Error running stereo: {e}")
        return False

def generate_dem(point_cloud, output_dem, resolution=30):
    """Generate DEM from point cloud - CORRECTED with UTM and errorimage"""
    st.info(f"🗻 Generating DEM with {resolution}m resolution...")
    
    # CORRECTED: Use UTM 43N and errorimage flag that we know work
    cmd = f"point2dem --tr {resolution} --t_srs 'EPSG:32643' --errorimage {point_cloud}"
    st.code(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            st.success("✅ DEM generation completed successfully!")
            return True
        else:
            st.error(f"❌ DEM generation failed with error: {result.stderr}")
            return False
    except Exception as e:
        st.error(f"❌ Error generating DEM: {e}")
        return False

def get_dem_stats(dem_file):
    """Get DEM statistics"""
    if not RASTERIO_AVAILABLE:
        return None
    
    try:
        with rasterio.open(dem_file) as src:
            data = src.read(1, masked=True)
            if data.mask.all():
                return None
            
            stats = {
                'min_elevation': float(data.min()),
                'max_elevation': float(data.max()),
                'mean_elevation': float(data.mean()),
                'file_size_mb': os.path.getsize(dem_file) / (1024 * 1024)
            }
            return stats
    except Exception as e:
        st.warning(f"Could not read DEM stats: {e}")
        return None

def main():
    """Main processing function - EXACT same structure as process_aster_dem.py"""
    
    st.title("🏔️ Simple ASTER DEM Processing")
    st.markdown("**Exact same logic as process_aster_dem.py with corrected commands**")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload ASTER L1A Zip File",
        type=['zip'],
        help="Select an ASTER L1A zip file for DEM reconstruction"
    )
    
    if not uploaded_file:
        st.info("👆 Please upload an ASTER L1A zip file to begin processing")
        return
    
    # Processing button
    if st.button("🚀 Process DEM", type="primary"):
        
        # Setup environment
        if not setup_environment():
            st.error("❌ Failed to setup ASP environment")
            return
        
        # Create temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Save uploaded file
            zip_path = os.path.join(temp_dir, uploaded_file.name)
            with open(zip_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            # Define paths - EXACT same structure as process_aster_dem.py
            base_name = os.path.splitext(uploaded_file.name)[0]
            work_dir = os.path.join(temp_dir, "ASTER_processing")
            
            # Create working directory
            os.makedirs(work_dir, exist_ok=True)
            
            st.info(f"🎯 Processing: {base_name}")
            
            try:
                # Step 1: Extract ASTER data
                extract_dir = os.path.join(work_dir, f"{base_name}_extracted")
                aster_dir = extract_aster_data(zip_path, extract_dir)
                
                # Step 2: Convert to ASP format
                asp_output_prefix = os.path.join(work_dir, f"{base_name}_asp", "out")
                if not process_aster_to_asp(aster_dir, asp_output_prefix):
                    st.error("❌ Failed to convert ASTER data to ASP format")
                    return
                
                # Step 3: Find the generated files
                asp_dir = os.path.dirname(asp_output_prefix)
                left_image = glob.glob(os.path.join(asp_dir, "*Band3N.tif"))  # Nadir (left)
                right_image = glob.glob(os.path.join(asp_dir, "*Band3B.tif"))  # Backward (right)
                left_camera = glob.glob(os.path.join(asp_dir, "*Band3N.xml"))
                right_camera = glob.glob(os.path.join(asp_dir, "*Band3B.xml"))
                
                if not (left_image and right_image and left_camera and right_camera):
                    st.error("❌ Could not find all required ASP files")
                    st.info(f"Left image: {left_image}")
                    st.info(f"Right image: {right_image}")
                    st.info(f"Left camera: {left_camera}")
                    st.info(f"Right camera: {right_camera}")
                    return
                
                st.success("✅ Found all ASP files:")
                st.info(f"- Left image: {os.path.basename(left_image[0])}")
                st.info(f"- Right image: {os.path.basename(right_image[0])}")
                st.info(f"- Left camera: {os.path.basename(left_camera[0])}")
                st.info(f"- Right camera: {os.path.basename(right_camera[0])}")
                
                # Step 4: Run stereo processing
                stereo_output_prefix = os.path.join(work_dir, f"{base_name}_stereo", "stereo")
                os.makedirs(os.path.dirname(stereo_output_prefix), exist_ok=True)
                
                if not run_stereo_processing(
                    left_image[0], right_image[0], 
                    left_camera[0], right_camera[0], 
                    stereo_output_prefix
                ):
                    st.error("❌ Stereo processing failed")
                    return
                
                # Step 5: Generate DEM
                point_cloud = f"{stereo_output_prefix}-PC.tif"
                
                if not os.path.exists(point_cloud):
                    st.error(f"❌ Point cloud not found: {point_cloud}")
                    return
                
                if not generate_dem(point_cloud, stereo_output_prefix, resolution=30):
                    st.error("❌ DEM generation failed")
                    return
                
                # Step 6: Find and analyze DEM
                dem_files = glob.glob(f"{stereo_output_prefix}-DEM.tif")
                if not dem_files:
                    st.error("❌ No DEM files found")
                    return
                
                dem_file = dem_files[0]
                st.success(f"✅ DEM created: {os.path.basename(dem_file)}")
                
                # Get DEM statistics
                stats = get_dem_stats(dem_file)
                if stats:
                    st.success("📊 **DEM Statistics:**")
                    st.write(f"- **Max elevation:** {stats['max_elevation']:.1f}m")
                    st.write(f"- **Min elevation:** {stats['min_elevation']:.1f}m")
                    st.write(f"- **Mean elevation:** {stats['mean_elevation']:.1f}m")
                    st.write(f"- **File size:** {stats['file_size_mb']:.1f} MB")
                    
                    if stats['max_elevation'] > 5000:
                        st.success(f"🏔️ **EXCELLENT!** High elevation preserved (>{stats['max_elevation']:.0f}m)")
                    else:
                        st.warning(f"⚠️ Max elevation ({stats['max_elevation']:.0f}m) - checking if this is expected")
                
                # Provide download link
                with open(dem_file, 'rb') as f:
                    st.download_button(
                        label="📥 Download DEM File",
                        data=f.read(),
                        file_name=os.path.basename(dem_file),
                        mime="application/octet-stream"
                    )
                
                st.success("🎉 **Processing Complete!**")
                
            except Exception as e:
                st.error(f"❌ Processing failed: {str(e)}")

if __name__ == "__main__":
    main()
