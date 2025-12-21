#!/bin/bash
# setup.sh - Complete Pipeline Setup Script

echo "Setting up People's Audit Pipeline..."
echo "====================================="

# Create directory structure
echo "Creating directory structure..."
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\input"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\reference_materials\legal_frameworks"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\reference_materials\oversight_reports"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\reference_materials\statistical_baselines"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\reference_materials\comparative_studies"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\reference_materials\institutional_contacts"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\stage_1_extract"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\stage_2_semantic"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\stage_3_llm_text"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\stage_4_visuals"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\stage_5_validation"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\final_outputs\summaries"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\final_outputs\visuals"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\final_outputs\reports"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\final_outputs\data"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\logs"
mkdir -p "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\temp"

echo "Directories created successfully."

# Check for required files
echo ""
echo "Checking for required files..."
REQUIRED_FILES=(
    "THE-PEOPLES-AUDIT_compressed.pdf"
    "constitution_of_kenya_2010.pdf"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\input\\$file" ]; then
        echo "✓ Found: $file"
    else
        echo "✗ Missing: $file"
        echo "  Please place this file in D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\input\\"
    fi
done

# Create Python virtual environment
echo ""
echo "Setting up Python environment..."
python -m venv "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\venv"

# Activate virtual environment
source "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\venv\Scripts\activate"

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r "D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\requirements.txt"

echo ""
echo "Setup complete!"
echo ""
echo "To run the pipeline:"
echo "1. Activate virtual environment:"
echo "   source D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\venv\Scripts\activate"
echo "2. Run the pipeline:"
echo "   python D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\main.py"
echo ""
echo "Outputs will be in: D:\CEKA\Scripts PROJECTS\PEOPLES_AUDIT\final_outputs\\"