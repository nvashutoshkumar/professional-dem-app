#!/usr/bin/env python3
"""
Test Single ASTER File Processing - CORRECTED VERSION
Uses the exact same logic as chandra_basin_complete_workflow_corrected.py
"""

import os
import sys
import glob
import zipfile
import subprocess
import numpy as np
import rasterio
from pathlib import Path
import time

def setup_environment():
    """Set up the ASP environment following NASA tutorial"""
    asp_bin_path = "/home/ashutokumar/Pinn_mass_balance/ASP_setup/StereoPipeline-3.6.0-alpha-2025-08-05-x86_64-Linux/bin"
    current_path = os.environ.get('PATH', '')
    if asp_bin_path not in current_path:
        os.environ['PATH'] = f"{asp_bin_path}:{current_path}"
    
    os.environ['OPENTOPOGRAPHY_API_KEY'] = "523da07408e277366b4b10399fc41d99"
    
    print("🏔️ SINGLE ASTER FILE TEST - CORRECTED")
    print("Following NASA ASP Tutorial methodology with UTM 43N")
    print("=" * 60)
    print(f"ASP Version: {get_asp_version()}")

def get_asp_version():
    """Get ASP version"""
    try:
        result = subprocess.run("stereo --version", shell=True, capture_output=True, text=True)
        return result.stdout.split('\n')[0] if result.returncode == 0 else "Unknown"
    except:
        return "Unknown"

def extract_aster_data(zip_file, output_dir):
    """Extract ASTER L1A zip file - files are at root level"""
    print(f"📦 Extracting {os.path.basename(zip_file)}...")
    os.makedirs(output_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    # Files are directly in the extracted directory (no subdirectory)
    return output_dir

def process_aster_to_asp(aster_dir, output_prefix):
    """Convert ASTER L1A to ASP format using aster2asp - following tutorial exactly"""
    print(f"🔄 Converting ASTER to ASP format...")
    
    output_dir = os.path.dirname(output_prefix)
    os.makedirs(output_dir, exist_ok=True)
    
    # Exact tutorial command
    cmd = f"aster2asp {aster_dir} -o {output_prefix}"
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ aster2asp completed successfully!")
            return True
        else:
            print(f"❌ aster2asp failed:")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running aster2asp: {e}")
        return False

def run_stereo_processing(left_image, right_image, left_camera, right_camera, output_prefix):
    """Run stereo with ASTER rigorous camera model - following NASA tutorial exactly"""
    print("🛰️ Running stereo processing with ASTER rigorous camera model...")
    
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)
    
    # Exact NASA tutorial parameters for ASTER rigorous camera
    cmd = f"stereo -t aster --stereo-algorithm asp_bm --subpixel-mode 1 {left_image} {right_image} {left_camera} {right_camera} {output_prefix}"
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Stereo processing completed successfully!")
            return True
        else:
            print(f"❌ Stereo processing failed:")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running stereo: {e}")
        return False

def generate_dem(point_cloud, output_prefix, resolution=30):
    """Generate DEM from point cloud using correct UTM projection - following NASA tutorial"""
    print(f"🗻 Generating DEM with {resolution}m resolution in UTM 43N...")
    
    # Use correct UTM zone for Chandra Basin (EPSG:32643) - this is the key fix!
    tsrs = 'EPSG:32643'  # UTM Zone 43N for Chandra Basin
    
    cmd = f"point2dem --tr {resolution} --t_srs '{tsrs}' --errorimage {point_cloud}"
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ DEM generation completed successfully!")
            return True
        else:
            print(f"❌ DEM generation failed:")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error generating DEM: {e}")
        return False

def get_dem_stats(dem_file):
    """Get comprehensive DEM statistics"""
    try:
        with rasterio.open(dem_file) as src:
            data = src.read(1, masked=True)
            if data.mask.all():
                return None
            
            stats = {
                'min_elevation': float(data.min()),
                'max_elevation': float(data.max()),
                'mean_elevation': float(data.mean()),
                'std_elevation': float(data.std()),
                'valid_pixels': int((~data.mask).sum()),
                'total_pixels': int(data.size),
                'bounds': src.bounds,
                'crs': str(src.crs),
                'shape': src.shape,
                'file_size_mb': os.path.getsize(dem_file) / (1024 * 1024)
            }
            return stats
    except Exception as e:
        print(f"❌ Error reading DEM stats: {e}")
        return None

def main():
    """Main workflow using corrected NASA ASP Tutorial methodology"""
    setup_environment()
    
    # Specific file to test
    zip_file = "/home/ashutokumar/Pinn_mass_balance/DEM/2011_old/AST_L1A_00304212011054141_20250626170033_1110403.zip"
    
    if not os.path.exists(zip_file):
        print(f"❌ File not found: {zip_file}")
        return
    
    work_dir = "/home/ashutokumar/Pinn_mass_balance/TEST_CORRECTED_SINGLE"
    os.makedirs(work_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(zip_file))[0]
    
    print(f"🎯 Testing file: {os.path.basename(zip_file)}")
    print(f"📁 Work directory: {work_dir}")
    print(f"🔧 Using UTM 43N (EPSG:32643) for Chandra Basin")
    
    try:
        start_time = time.time()
        
        # Step 1: Extract ASTER data (files at root level)
        extract_dir = os.path.join(work_dir, f"{base_name}_extracted")
        aster_dir = extract_aster_data(zip_file, extract_dir)
        
        # Step 2: Convert to ASP format
        asp_output_prefix = os.path.join(work_dir, f"{base_name}_asp", "out")
        if not process_aster_to_asp(aster_dir, asp_output_prefix):
            return
        
        # Step 3: Find the generated files (following tutorial pattern)
        asp_dir = os.path.dirname(asp_output_prefix)
        left_image = glob.glob(os.path.join(asp_dir, "*Band3N.tif"))  # Nadir (left)
        right_image = glob.glob(os.path.join(asp_dir, "*Band3B.tif"))  # Backward (right)
        left_camera = glob.glob(os.path.join(asp_dir, "*Band3N.xml"))
        right_camera = glob.glob(os.path.join(asp_dir, "*Band3B.xml"))
        
        print(f"Found files:")
        print(f"  Left image: {left_image}")
        print(f"  Right image: {right_image}")
        print(f"  Left camera: {left_camera}")
        print(f"  Right camera: {right_camera}")
        
        if not (left_image and right_image and left_camera and right_camera):
            print("❌ Could not find all required ASP files")
            return
        
        # Step 4: Run stereo processing with ASTER session
        stereo_output_prefix = os.path.join(work_dir, f"{base_name}_stereo", "run")
        
        if not run_stereo_processing(
            left_image[0], right_image[0], 
            left_camera[0], right_camera[0], 
            stereo_output_prefix
        ):
            return
        
        # Step 5: Generate DEM with correct UTM projection
        point_cloud = f"{stereo_output_prefix}-PC.tif"
        
        if not os.path.exists(point_cloud):
            print(f"❌ Point cloud not found: {point_cloud}")
            return
        
        if not generate_dem(point_cloud, stereo_output_prefix, resolution=30):
            return
        
        # Step 6: Find and validate DEM file
        dem_files = glob.glob(f"{stereo_output_prefix}-DEM.tif")
        if not dem_files:
            print("❌ No DEM files found")
            return
        
        dem_file = dem_files[0]
        stats = get_dem_stats(dem_file)
        
        if stats:
            processing_time = time.time() - start_time
            print(f"\n🎉 SUCCESS!")
            print(f"✅ DEM file: {os.path.basename(dem_file)}")
            print(f"✅ Max elevation: {stats['max_elevation']:.1f}m")
            print(f"✅ Min elevation: {stats['min_elevation']:.1f}m")
            print(f"✅ Processing time: {processing_time:.1f}s")
            print(f"✅ File size: {stats['file_size_mb']:.1f} MB")
            print(f"✅ CRS: {stats['crs']}")
            
            if stats['max_elevation'] > 5000:
                print(f"🏔️ EXCELLENT! High elevation preserved (>{stats['max_elevation']:.0f}m)")
            else:
                print(f"⚠️ Max elevation lower than expected")
        else:
            print("❌ Could not read DEM stats")
            
    except Exception as e:
        print(f"❌ Error processing: {e}")

if __name__ == "__main__":
    main()
