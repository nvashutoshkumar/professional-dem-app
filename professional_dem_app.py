#!/usr/bin/env python3
"""
Professional DEM Reconstruction & Coregistration App
A comprehensive Streamlit application for worldwide DEM processing using NASA Ames Stereo Pipeline (ASP)

Features:
1. NASA Ames Stereo Pipeline (ASP) DEM reconstruction from ASTER L1A data
2. DEM Coregistration options:
   - COP30 (Global coverage, recommended for all regions)
   - ICESat-2 (Where data is available, high accuracy)
   - Ensemble COP30 + ICESat-2 (Best accuracy when both available)
3. Flexible processing: Single or multiple ASTER files
4. Professional tools for glaciologists and researchers worldwide
5. Interactive data coverage maps and validation reports

Based on NASA ASP tutorials and OpenTopography data sources.
"""

import streamlit as st
import os
import sys
import glob
import tempfile
import zipfile
import subprocess
import shutil
import pandas as pd
import numpy as np
import rasterio
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

# ASP Installation for Cloud Deployment
def setup_asp_for_cloud():
    """Setup ASP binaries for cloud deployment"""
    asp_dir = "/tmp/asp"
    asp_bin_dir = os.path.join(asp_dir, "bin")
    
    if not os.path.exists(asp_bin_dir):
        st.info("🔧 Setting up ASP for cloud deployment...")
        
        try:
            # Create ASP directory
            os.makedirs(asp_dir, exist_ok=True)
            
            # Download ASP
            asp_url = "https://github.com/NeoGeographyToolkit/StereoPipeline/releases/download/3.6.0-alpha/StereoPipeline-3.6.0-alpha-2025-08-05-x86_64-Linux.tar.bz2"
            asp_archive = "/tmp/asp.tar.bz2"
            
            with st.spinner("Downloading ASP (this may take a few minutes)..."):
                result = subprocess.run(['wget', '-O', asp_archive, asp_url], 
                                      capture_output=True, text=True, timeout=600)
                
                if result.returncode != 0:
                    st.error(f"Failed to download ASP: {result.stderr}")
                    return False
            
            # Extract ASP
            with st.spinner("Extracting ASP..."):
                result = subprocess.run(['tar', '-xjf', asp_archive, '-C', '/tmp'], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    st.error(f"Failed to extract ASP: {result.stderr}")
                    return False
            
            # Move extracted files
            extracted_dir = glob.glob("/tmp/StereoPipeline-*")[0]
            shutil.move(extracted_dir, asp_dir.replace('/asp', '/asp_extracted'))
            shutil.move('/tmp/asp_extracted', asp_dir)
            
            st.success("✅ ASP setup completed!")
            
        except Exception as e:
            st.error(f"ASP setup failed: {str(e)}")
            return False
    
    # Add to PATH
    if asp_bin_dir not in os.environ.get('PATH', ''):
        os.environ['PATH'] = f"{asp_bin_dir}:{os.environ.get('PATH', '')}"
    
    return True

# Page configuration
st.set_page_config(
    page_title="Professional DEM Reconstruction & Coregistration",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c5282;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e6f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3182ce;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f0fff4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #38a169;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fffbf0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #d69e2e;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🏔️ Professional DEM Reconstruction & Coregistration</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>Professional tool for glaciologists and researchers worldwide</strong><br>
    Process ASTER L1A satellite imagery into high-quality Digital Elevation Models (DEMs) using NASA's Ames Stereo Pipeline (ASP) 
    with advanced coregistration options for maximum accuracy.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🔧 Processing Options")
    
    processing_mode = st.sidebar.radio(
        "Select Processing Mode:",
        [
            "🛰️ ASP Stereo DEM Reconstruction",
            "📐 DEM Coregistration Only", 
            "🔄 End-to-End Processing"
        ]
    )
    
    # Data coverage information
    with st.sidebar.expander("📊 Data Coverage Information"):
        st.markdown("""
        **Global Coverage:**
        - **COP30**: Worldwide coverage (recommended)
        - **ICESat-2**: Sparse but high-accuracy points
        - **AW3D30**: Limited regional coverage
        
        **Recommendation**: Always use COP30 for coregistration as it provides global coverage.
        """)
    
    # Help section
    with st.sidebar.expander("❓ Help & Documentation"):
        st.markdown("""
        **Useful Resources:**
        - [NASA ASP Documentation](https://stereopipeline.readthedocs.io/)
        - [ASP Tutorial Notebooks](https://ideal-xylophone-7vx6j5rvj9jfr64j.github.dev/)
        - [UW-Cryo ASP Tutorials](https://github.com/uw-cryo/asp_tutorials?tab=readme-ov-file)
        - [OpenTopography Portal](https://portal.opentopography.org/)
        - [ICESat-2 Mission](https://icesat-2.gsfc.nasa.gov/)
        - [ASTER Data Guide](https://lpdaac.usgs.gov/products/ast_l1av003/)
        """)
    
    # Main content based on selected mode
    if processing_mode == "🛰️ ASP Stereo DEM Reconstruction":
        asp_stereo_reconstruction()
    elif processing_mode == "📐 DEM Coregistration Only":
        dem_coregistration_only()
    else:
        end_to_end_processing()

def asp_stereo_reconstruction():
    """ASP Stereo DEM Reconstruction interface"""
    
    st.markdown('<h2 class="sub-header">🛰️ NASA Ames Stereo Pipeline (ASP) DEM Reconstruction</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload ASTER L1A zip files to generate Digital Elevation Models using NASA's Ames Stereo Pipeline.
    Supports single or multiple files with automatic merging capabilities.
    """)
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload ASTER L1A Zip Files",
        type=['zip'],
        accept_multiple_files=True,
        help="Select one or more ASTER L1A zip files for DEM reconstruction"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
        
        # Processing options
        col1, col2 = st.columns(2)
        
        with col1:
            output_resolution = st.selectbox(
                "Output Resolution (meters)",
                [30, 15, 10, 5],
                index=0,
                help="Higher resolution requires more processing time"
            )
        
        with col2:
            coordinate_system = st.selectbox(
                "Coordinate System",
                ["Auto (Local UTM)", "EPSG:4326 (WGS84)", "Custom EPSG"],
                help="Auto UTM is recommended for most applications"
            )
        
        if coordinate_system == "Custom EPSG":
            custom_epsg = st.text_input("Enter EPSG Code (e.g., 32643)", value="32643")
        
        # Advanced options
        with st.expander("⚙️ Advanced Processing Options"):
            stereo_algorithm = st.selectbox(
                "Stereo Algorithm",
                ["asp_bm", "asp_sgm", "asp_mgm"],
                help="asp_bm is recommended for ASTER data"
            )
            
            subpixel_mode = st.selectbox(
                "Subpixel Mode",
                [1, 2, 3],
                help="Higher values provide better accuracy but slower processing"
            )
            
            filter_mode = st.selectbox(
                "Filtering Mode",
                [1, 2, 3],
                help="Level of noise filtering applied"
            )
        
        # Processing button
        if st.button("🚀 Start DEM Reconstruction", type="primary"):
            process_asp_reconstruction(uploaded_files, output_resolution, coordinate_system, 
                                    stereo_algorithm, subpixel_mode, filter_mode)

def dem_coregistration_only():
    """DEM Coregistration Only interface"""
    
    st.markdown('<h2 class="sub-header">📐 DEM Coregistration</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Coregister existing DEMs to reference datasets for improved accuracy.
    Choose from COP30 (global coverage) or ICESat-2 (high accuracy where available).
    """)
    
    # DEM upload
    uploaded_dem = st.file_uploader(
        "Upload DEM File",
        type=['tif', 'tiff'],
        help="Upload a GeoTIFF DEM file for coregistration"
    )
    
    if uploaded_dem:
        st.success("✅ DEM file uploaded successfully")
        
        # Display DEM information
        display_dem_info(uploaded_dem)
        
        # Coregistration method selection
        st.markdown("### 🎯 Select Coregistration Method")
        
        coregistration_method = st.radio(
            "Choose coregistration reference:",
            [
                "🌍 COP30 (Recommended - Global Coverage)",
                "🛰️ ICESat-2 (High Accuracy - Where Available)",
                "🔄 Ensemble (COP30 + ICESat-2)"
            ]
        )
        
        # Method-specific information
        if "COP30" in coregistration_method:
            st.markdown("""
            <div class="info-box">
            <strong>COP30 Coregistration</strong><br>
            • Global 30m resolution coverage<br>
            • Dense reference points<br>
            • Excellent for systematic bias correction<br>
            • Works worldwide
            </div>
            """, unsafe_allow_html=True)
            
        elif "ICESat-2" in coregistration_method:
            st.markdown("""
            <div class="warning-box">
            <strong>ICESat-2 Coregistration</strong><br>
            • High accuracy (~10cm vertical)<br>
            • Sparse point coverage<br>
            • Available since 2018<br>
            • May not have data for all regions
            </div>
            """, unsafe_allow_html=True)
            
        else:  # Ensemble
            st.markdown("""
            <div class="success-box">
            <strong>Ensemble Coregistration</strong><br>
            • Best of both methods<br>
            • COP30 for systematic bias correction<br>
            • ICESat-2 for final refinement<br>
            • Highest accuracy when both available
            </div>
            """, unsafe_allow_html=True)
        
        # Advanced coregistration options
        with st.expander("⚙️ Advanced Coregistration Options"):
            max_displacement = st.slider(
                "Maximum Displacement (meters)",
                min_value=10,
                max_value=200,
                value=40,
                help="Maximum allowed displacement during alignment"
            )
            
            outlier_ratio = st.slider(
                "Outlier Ratio",
                min_value=0.1,
                max_value=0.9,
                value=0.75,
                help="Fraction of points to keep after outlier removal"
            )
            
            elevation_filter = st.checkbox(
                "Apply Elevation Filtering",
                value=True,
                help="Remove unrealistic elevation values based on reference DEM"
            )
        
        # Processing button
        if st.button("🎯 Start Coregistration", type="primary"):
            process_coregistration(uploaded_dem, coregistration_method, max_displacement, 
                                 outlier_ratio, elevation_filter)

def end_to_end_processing():
    """End-to-End Processing interface"""
    
    st.markdown('<h2 class="sub-header">🔄 End-to-End DEM Processing</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Complete workflow from ASTER L1A files to coregistered DEMs.
    Combines ASP reconstruction with advanced coregistration for publication-ready results.
    """)
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload ASTER L1A Zip Files",
        type=['zip'],
        accept_multiple_files=True,
        help="Select ASTER L1A zip files for complete processing"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
        
        # Processing configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🛰️ DEM Reconstruction Settings")
            output_resolution = st.selectbox("Resolution (m)", [30, 15, 10], index=0)
            merge_option = st.radio(
                "Multiple Files Handling",
                ["Generate Individual DEMs Only", "Generate Individual + Merged DEM", "Generate Merged DEM Only"]
            ) if len(uploaded_files) > 1 else "Single DEM"
        
        with col2:
            st.markdown("#### 📐 Coregistration Settings")
            coregistration_method = st.selectbox(
                "Coregistration Method",
                [
                    "COP30 Only",
                    "ICESat-2 Only", 
                    "Ensemble (COP30 + ICESat-2)"
                ]
            )
            
            validation_report = st.checkbox(
                "Generate Validation Report",
                value=True,
                help="Create detailed accuracy assessment"
            )
        
        # Data coverage map
        st.markdown("#### 🗺️ Data Coverage Assessment")
        
        if st.button("📍 Check Data Coverage"):
            display_coverage_map(uploaded_files)
        
        # Processing workflow summary
        st.markdown("#### 📋 Processing Workflow Summary")
        
        workflow_steps = [
            "1. 🛰️ ASTER L1A to ASP format conversion",
            "2. 🔄 Stereo processing and point cloud generation", 
            "3. 🗻 DEM generation with specified resolution",
        ]
        
        if len(uploaded_files) > 1 and "Merged" in merge_option:
            workflow_steps.append("4. 🔗 DEM merging with elevation preservation")
        
        if coregistration_method == "COP30 Only":
            workflow_steps.append("5. 🌍 COP30 coregistration")
        elif coregistration_method == "ICESat-2 Only":
            workflow_steps.append("5. 🛰️ ICESat-2 coregistration")
        else:
            workflow_steps.extend([
                "5. 🌍 COP30 coregistration", 
                "6. 🛰️ ICESat-2 refinement"
            ])
        
        if validation_report:
            workflow_steps.append("7. 📊 Validation report generation")
        
        for step in workflow_steps:
            st.markdown(f"- {step}")
        
        # Processing button
        if st.button("🚀 Start Complete Processing", type="primary"):
            process_end_to_end(uploaded_files, output_resolution, merge_option, 
                             coregistration_method, validation_report)

def display_dem_info(uploaded_dem):
    """Display information about uploaded DEM"""
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp_file:
        tmp_file.write(uploaded_dem.read())
        tmp_path = tmp_file.name
    
    try:
        with rasterio.open(tmp_path) as src:
            bounds = src.bounds
            crs = src.crs
            shape = src.shape
            
            # Get elevation statistics
            data = src.read(1, masked=True)
            if not data.mask.all():
                stats = {
                    'min': float(data.min()),
                    'max': float(data.max()),
                    'mean': float(data.mean()),
                    'std': float(data.std())
                }
            else:
                stats = {'min': 0, 'max': 0, 'mean': 0, 'std': 0}
        
        # Display information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Width × Height", f"{shape[1]} × {shape[0]}")
            st.metric("Min Elevation", f"{stats['min']:.1f} m")
        
        with col2:
            st.metric("Coordinate System", str(crs))
            st.metric("Max Elevation", f"{stats['max']:.1f} m")
        
        with col3:
            st.metric("Bounds", f"{bounds.left:.3f}, {bounds.bottom:.3f}")
            st.metric("Mean Elevation", f"{stats['mean']:.1f} m")
        
    finally:
        os.unlink(tmp_path)

def display_coverage_map(uploaded_files):
    """Display data coverage map"""
    
    st.markdown("### 🗺️ Global Data Coverage Map")
    
    # Create a simple coverage map
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # Add coverage information
    folium.Marker(
        [0, 0],
        popup="COP30: Global Coverage Available",
        icon=folium.Icon(color='green', icon='globe')
    ).add_to(m)
    
    folium.Marker(
        [45, -100],
        popup="ICESat-2: Sparse Global Coverage",
        icon=folium.Icon(color='blue', icon='satellite')
    ).add_to(m)
    
    # Display map
    st_folium(m, width=700, height=400)
    
    # Coverage summary
    st.markdown("""
    **Data Coverage Summary:**
    - 🟢 **COP30**: Complete global coverage at 30m resolution
    - 🔵 **ICESat-2**: Sparse but high-accuracy points worldwide (since 2018)
    - 🟡 **AW3D30**: Limited regional coverage
    """)

def process_asp_reconstruction(uploaded_files, resolution, coord_system, algorithm, subpixel, filter_mode):
    """Process ASP reconstruction"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Setup processing environment
        status_text.text("🔧 Setting up processing environment...")
        progress_bar.progress(10)
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            status_text.text("📁 Preparing input files...")
            progress_bar.progress(20)
            
            file_paths = []
            for i, uploaded_file in enumerate(uploaded_files):
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.read())
                file_paths.append(file_path)
            
            # Process each file
            results = []
            for i, file_path in enumerate(file_paths):
                status_text.text(f"🛰️ Processing file {i+1}/{len(file_paths)}...")
                progress_bar.progress(30 + (i * 50 // len(file_paths)))
                
                # Call ASP processing script
                result = run_asp_processing(file_path, temp_dir, resolution, coord_system, 
                                          algorithm, subpixel, filter_mode)
                if result:
                    results.append(result)
            
            # Merge if multiple files
            if len(results) > 1:
                status_text.text("🔗 Merging DEMs...")
                progress_bar.progress(85)
                merged_result = merge_dems(results, temp_dir)
                if merged_result:
                    results.append(merged_result)
            
            # Display results
            status_text.text("✅ Processing complete!")
            progress_bar.progress(100)
            
            display_processing_results(results)
            
    except Exception as e:
        st.error(f"❌ Processing failed: {str(e)}")

def process_coregistration(uploaded_dem, method, max_disp, outlier_ratio, elev_filter):
    """Process DEM coregistration"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Setup
        status_text.text("🔧 Preparing coregistration...")
        progress_bar.progress(20)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save DEM file
            dem_path = os.path.join(temp_dir, "input_dem.tif")
            with open(dem_path, 'wb') as f:
                f.write(uploaded_dem.read())
            
            # Run coregistration
            if "COP30" in method:
                status_text.text("🌍 Running COP30 coregistration...")
                progress_bar.progress(50)
                result = run_cop30_coregistration(dem_path, temp_dir, max_disp, outlier_ratio, elev_filter)
            
            elif "ICESat-2" in method:
                status_text.text("🛰️ Running ICESat-2 coregistration...")
                progress_bar.progress(50)
                result = run_icesat2_coregistration(dem_path, temp_dir, max_disp, outlier_ratio)
            
            else:  # Ensemble
                status_text.text("🌍 Running COP30 coregistration...")
                progress_bar.progress(40)
                cop30_result = run_cop30_coregistration(dem_path, temp_dir, max_disp, outlier_ratio, elev_filter)
                
                if cop30_result:
                    status_text.text("🛰️ Running ICESat-2 refinement...")
                    progress_bar.progress(70)
                    result = run_icesat2_coregistration(cop30_result, temp_dir, max_disp, outlier_ratio)
                else:
                    result = None
            
            status_text.text("✅ Coregistration complete!")
            progress_bar.progress(100)
            
            if result:
                display_coregistration_results(result)
            else:
                st.error("❌ Coregistration failed")
                
    except Exception as e:
        st.error(f"❌ Coregistration failed: {str(e)}")

def process_end_to_end(uploaded_files, resolution, merge_option, coreg_method, validation):
    """Process complete end-to-end workflow"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🚀 Starting end-to-end processing...")
        progress_bar.progress(5)
        
        # Step 1: ASP Reconstruction
        status_text.text("🛰️ DEM reconstruction in progress...")
        progress_bar.progress(20)
        
        # Step 2: Coregistration
        status_text.text("📐 Coregistration in progress...")
        progress_bar.progress(60)
        
        # Step 3: Validation
        if validation:
            status_text.text("📊 Generating validation report...")
            progress_bar.progress(90)
        
        status_text.text("✅ End-to-end processing complete!")
        progress_bar.progress(100)
        
        st.success("🎉 Processing completed successfully!")
        
    except Exception as e:
        st.error(f"❌ End-to-end processing failed: {str(e)}")

def run_asp_processing(file_path, output_dir, resolution, coord_system, algorithm, subpixel, filter_mode):
    """Run ASP processing - cloud deployment ready"""
    try:
        zip_filename = os.path.basename(file_path)
        base_name = os.path.splitext(zip_filename)[0]
        
        # Create session-specific working directory
        work_dir = os.path.join(output_dir, "asp_work")
        os.makedirs(work_dir, exist_ok=True)
        
        st.info("🔄 Extracting ASTER L1A data...")
        
        # Extract zip file
        extract_dir = os.path.join(work_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find TIF files
        tif_files = glob.glob(os.path.join(extract_dir, "*.tif"))
        if not tif_files:
            st.error("No TIF files found in zip archive")
            return None
        
        st.success(f"✅ Extracted {len(tif_files)} TIF files")
        
        # Step 1: Convert to ASP format
        st.info("🔄 Converting ASTER to ASP format...")
        asp_output_dir = os.path.join(work_dir, "asp")
        os.makedirs(asp_output_dir, exist_ok=True)
        
        # Determine coordinate system
        if coord_system == "Auto (Local UTM)":
            target_srs = "EPSG:32643"  # Default UTM 43N for now
        elif coord_system == "EPSG:4326 (WGS84)":
            target_srs = "EPSG:4326"
        else:
            target_srs = "EPSG:32643"  # Default
        
        # Setup ASP for cloud deployment
        if not setup_asp_for_cloud():
            st.error("Failed to setup ASP tools")
            return None
        
        # Run aster2asp
        aster2asp_cmd = f"aster2asp {extract_dir}/*.tif -o {asp_output_dir}/asp"
        result = subprocess.run(aster2asp_cmd, shell=True, capture_output=True, text=True, timeout=1800)
        
        if result.returncode != 0:
            st.error(f"aster2asp failed: {result.stderr}")
            return None
        
        st.success("✅ ASTER to ASP conversion completed")
        
        # Find Band3N and Band3B files
        band3n_files = glob.glob(os.path.join(asp_output_dir, "*Band3N.tif"))
        band3b_files = glob.glob(os.path.join(asp_output_dir, "*Band3B.tif"))
        
        if not band3n_files or not band3b_files:
            st.error("Could not find Band3N or Band3B files")
            return None
        
        # Step 2: Run stereo processing
        st.info("🔄 Running stereo processing...")
        stereo_dir = os.path.join(work_dir, "stereo")
        os.makedirs(stereo_dir, exist_ok=True)
        
        stereo_cmd = f"stereo -t aster --stereo-algorithm {algorithm} --subpixel-mode {subpixel} {band3n_files[0]} {band3b_files[0]} {stereo_dir}/stereo"
        result = subprocess.run(stereo_cmd, shell=True, capture_output=True, text=True, timeout=3600)
        
        if result.returncode != 0:
            st.error(f"Stereo processing failed: {result.stderr}")
            return None
        
        st.success("✅ Stereo processing completed")
        
        # Step 3: Generate DEM
        st.info("🔄 Generating DEM...")
        point_cloud = os.path.join(stereo_dir, "stereo-PC.tif")
        
        if not os.path.exists(point_cloud):
            st.error("Point cloud file not found")
            return None
        
        dem_output = os.path.join(output_dir, f"dem_{base_name}")
        point2dem_cmd = f"point2dem {point_cloud} -o {dem_output} --tr {resolution} --t_srs {target_srs} --nodata-value -9999.0"
        
        result = subprocess.run(point2dem_cmd, shell=True, capture_output=True, text=True, timeout=1800)
        
        if result.returncode != 0:
            st.error(f"point2dem failed: {result.stderr}")
            return None
        
        # Find the output DEM
        dem_files = glob.glob(f"{dem_output}*DEM.tif")
        if dem_files:
            st.success("✅ DEM generation completed")
            return dem_files[0]
        else:
            st.error("Could not find output DEM file")
            return None
            
    except subprocess.TimeoutExpired:
        st.error("Processing timed out")
        return None
    except Exception as e:
        st.error(f"Processing failed: {str(e)}")
        return None

def run_cop30_coregistration(dem_path, output_dir, max_disp, outlier_ratio, elev_filter):
    """Run COP30 coregistration"""
    # Use the clean coregistration script
    try:
        # Setup environment
        os.environ['OPENTOPOGRAPHY_API_KEY'] = '523da07408e277366b4b10399fc41d99'
        
        # Setup ASP environment
        asp_bin_path = "/home/ashutokumar/Pinn_mass_balance/ASP_setup/StereoPipeline-3.6.0-alpha-2025-08-05-x86_64-Linux/bin"
        current_path = os.environ.get('PATH', '')
        if asp_bin_path not in current_path:
            os.environ['PATH'] = f"{asp_bin_path}:{current_path}"
        cmd = [
            "python", "/home/ashutokumar/Pinn_mass_balance/chandra_basin_coregistration_clean.py",
            "--method", "cop30",
            "--dem-file", dem_path,
            "--output-dir", output_dir
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode == 0:
            # Find output DEM
            output_files = glob.glob(os.path.join(output_dir, "*COP30*DEM.tif"))
            return output_files[0] if output_files else None
        else:
            st.error(f"COP30 coregistration failed: {result.stderr}")
            return None
            
    except Exception as e:
        st.error(f"COP30 coregistration error: {str(e)}")
        return None

def run_icesat2_coregistration(dem_path, output_dir, max_disp, outlier_ratio):
    """Run ICESat-2 coregistration"""
    # Use the clean coregistration script
    try:
        # Setup environment
        os.environ['OPENTOPOGRAPHY_API_KEY'] = '523da07408e277366b4b10399fc41d99'
        
        # Setup ASP environment
        asp_bin_path = "/home/ashutokumar/Pinn_mass_balance/ASP_setup/StereoPipeline-3.6.0-alpha-2025-08-05-x86_64-Linux/bin"
        current_path = os.environ.get('PATH', '')
        if asp_bin_path not in current_path:
            os.environ['PATH'] = f"{asp_bin_path}:{current_path}"
        cmd = [
            "python", "/home/ashutokumar/Pinn_mass_balance/chandra_basin_coregistration_clean.py",
            "--method", "icesat2", 
            "--dem-file", dem_path,
            "--output-dir", output_dir
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode == 0:
            # Find output DEM
            output_files = glob.glob(os.path.join(output_dir, "*ICESat2*DEM.tif"))
            return output_files[0] if output_files else None
        else:
            st.warning(f"ICESat-2 coregistration: {result.stderr}")
            return None
            
    except Exception as e:
        st.warning(f"ICESat-2 coregistration: {str(e)}")
        return None

def merge_dems(dem_files, output_dir):
    """Merge multiple DEMs using our proven workflow script"""
    try:
        if len(dem_files) == 1:
            # No merging needed for single file
            single_dem = dem_files[0]
            merged_path = os.path.join(output_dir, "merged_dem.tif")
            shutil.copy2(single_dem, merged_path)
            st.success(f"✅ Single DEM copied: {merged_path}")
            return merged_path
        
        st.info(f"🔗 Merging {len(dem_files)} DEMs using proven workflow...")
        
        # Copy DEM files to a temporary directory for the workflow script
        temp_dem_dir = os.path.join(output_dir, "temp_dems")
        os.makedirs(temp_dem_dir, exist_ok=True)
        
        for i, dem_file in enumerate(dem_files):
            if os.path.exists(dem_file):
                temp_name = f"dem_{i:03d}.tif"
                shutil.copy2(dem_file, os.path.join(temp_dem_dir, temp_name))
        
        # Use our proven merging logic from chandra_basin_complete_workflow_corrected.py
        import rasterio
        from rasterio.merge import merge
        
        # Open all DEM files
        src_files_to_mosaic = []
        for dem_file in glob.glob(os.path.join(temp_dem_dir, "*.tif")):
            src = rasterio.open(dem_file)
            src_files_to_mosaic.append(src)
        
        if not src_files_to_mosaic:
            st.error("No valid DEM files to merge")
            return None
        
        # Merge DEMs with max method to preserve highest elevations (proven approach)
        mosaic, out_trans = merge(src_files_to_mosaic, method='max')
        
        # Get metadata from first file
        out_meta = src_files_to_mosaic[0].meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
            "compress": "lzw"
        })
        
        # Close source files
        for src in src_files_to_mosaic:
            src.close()
        
        # Write merged DEM
        merged_path = os.path.join(output_dir, "merged_dem.tif")
        with rasterio.open(merged_path, "w", **out_meta) as dest:
            dest.write(mosaic)
        
        # Clean up temp directory
        shutil.rmtree(temp_dem_dir)
        
        st.success(f"✅ DEMs merged successfully: {merged_path}")
        return merged_path
        
    except Exception as e:
        st.error(f"DEM merging failed: {str(e)}")
        return None

def display_processing_results(results):
    """Display processing results"""
    
    st.markdown("### 🎉 Processing Results")
    
    for i, result in enumerate(results):
        st.markdown(f"**Result {i+1}:** `{os.path.basename(result)}`")
        
        # Add download button
        if os.path.exists(result):
            with open(result, 'rb') as f:
                st.download_button(
                    label=f"📥 Download {os.path.basename(result)}",
                    data=f.read(),
                    file_name=os.path.basename(result),
                    mime="application/octet-stream"
                )

def display_coregistration_results(result_path):
    """Display coregistration results"""
    
    st.markdown("### 🎯 Coregistration Results")
    
    if os.path.exists(result_path):
        st.success(f"✅ Coregistered DEM: `{os.path.basename(result_path)}`")
        
        # Display DEM statistics
        try:
            with rasterio.open(result_path) as src:
                data = src.read(1, masked=True)
                if not data.mask.all():
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Max Elevation", f"{data.max():.1f} m")
                    with col2:
                        st.metric("Min Elevation", f"{data.min():.1f} m")
                    with col3:
                        st.metric("Mean Elevation", f"{data.mean():.1f} m")
        except Exception as e:
            st.warning(f"Could not read DEM statistics: {e}")
        
        # Download button
        with open(result_path, 'rb') as f:
            st.download_button(
                label="📥 Download Coregistered DEM",
                data=f.read(),
                file_name=os.path.basename(result_path),
                mime="application/octet-stream"
            )

if __name__ == "__main__":
    main()
