#!/bin/bash
# setup.sh - Complete Pipeline Setup Script for Local Development

echo "Setting up People's Audit Pipeline..."
echo "====================================="

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "Project root: $PROJECT_ROOT"

# Create directory structure
echo "Creating directory structure..."
mkdir -p "$PROJECT_ROOT/input"
mkdir -p "$PROJECT_ROOT/input/reference_materials"
mkdir -p "$PROJECT_ROOT/reference_materials"
mkdir -p "$PROJECT_ROOT/reference_materials/legal_frameworks"
mkdir -p "$PROJECT_ROOT/reference_materials/oversight_reports"
mkdir -p "$PROJECT_ROOT/reference_materials/statistical_baselines"
mkdir -p "$PROJECT_ROOT/reference_materials/comparative_studies"
mkdir -p "$PROJECT_ROOT/reference_materials/institutional_contacts"
mkdir -p "$PROJECT_ROOT/stage_1_extract"
mkdir -p "$PROJECT_ROOT/stage_2_semantic"
mkdir -p "$PROJECT_ROOT/stage_3_llm_text"
mkdir -p "$PROJECT_ROOT/stage_4_visuals"
mkdir -p "$PROJECT_ROOT/stage_4_visuals/html"
mkdir -p "$PROJECT_ROOT/stage_4_visuals/charts"
mkdir -p "$PROJECT_ROOT/stage_4_visuals/charts/html"
mkdir -p "$PROJECT_ROOT/stage_4_visuals/charts/png"
mkdir -p "$PROJECT_ROOT/stage_4_visuals/charts/svg"
mkdir -p "$PROJECT_ROOT/stage_4_visuals/charts/json"
mkdir -p "$PROJECT_ROOT/stage_5_validation"
mkdir -p "$PROJECT_ROOT/stage_5_validation/test_charts"
mkdir -p "$PROJECT_ROOT/stage_5_validation/test_charts/html"
mkdir -p "$PROJECT_ROOT/stage_5_validation/test_charts/png"
mkdir -p "$PROJECT_ROOT/final_outputs"
mkdir -p "$PROJECT_ROOT/final_outputs/summaries"
mkdir -p "$PROJECT_ROOT/final_outputs/visuals"
mkdir -p "$PROJECT_ROOT/final_outputs/reports"
mkdir -p "$PROJECT_ROOT/final_outputs/data"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/temp"
mkdir -p "$PROJECT_ROOT/test_output"
mkdir -p "$PROJECT_ROOT/test_charts"

echo "Directories created successfully."

# Check for required files
echo ""
echo "Checking for required files..."
REQUIRED_FILES=(
    "THE-PEOPLES-AUDIT_compressed.pdf"
    "constitution_of_kenya_2010.pdf"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/input/$file" ]; then
        echo "✓ Found: $file"
    else
        echo "✗ Missing: $file"
        echo "  Please place this file in $PROJECT_ROOT/input/"
    fi
done

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version || python --version

# Create Python virtual environment
echo ""
echo "Setting up Python environment..."
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv "$PROJECT_ROOT/venv" || python -m venv "$PROJECT_ROOT/venv"
    echo "Virtual environment created at: $PROJECT_ROOT/venv"
fi

# Determine OS for activation script
OS_TYPE=$(uname -s)
echo "Operating System: $OS_TYPE"

if [[ "$OS_TYPE" == "MINGW"* ]] || [[ "$OS_TYPE" == "MSYS"* ]] || [[ "$OS_TYPE" == "CYGWIN"* ]]; then
    # Windows Git Bash/Cygwin
    ACTIVATE_SCRIPT="$PROJECT_ROOT/venv/Scripts/activate"
    PYTHON_EXEC="$PROJECT_ROOT/venv/Scripts/python"
    PIP_EXEC="$PROJECT_ROOT/venv/Scripts/pip"
elif [[ "$OS_TYPE" == "Darwin" ]] || [[ "$OS_TYPE" == "Linux" ]]; then
    # macOS or Linux
    ACTIVATE_SCRIPT="$PROJECT_ROOT/venv/bin/activate"
    PYTHON_EXEC="$PROJECT_ROOT/venv/bin/python"
    PIP_EXEC="$PROJECT_ROOT/venv/bin/pip"
else
    echo "Unsupported operating system: $OS_TYPE"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$ACTIVATE_SCRIPT" || {
    echo "Failed to activate virtual environment."
    echo "Please activate manually:"
    if [[ "$OS_TYPE" == "MINGW"* ]] || [[ "$OS_TYPE" == "MSYS"* ]] || [[ "$OS_TYPE" == "CYGWIN"* ]]; then
        echo "source $ACTIVATE_SCRIPT"
    else
        echo "source $ACTIVATE_SCRIPT"
    fi
    exit 1
}

# Install dependencies
echo "Installing Python dependencies..."
"$PIP_EXEC" install --upgrade pip
"$PIP_EXEC" install -r "$PROJECT_ROOT/requirements.txt"

# Install additional packages needed for deployment
"$PIP_EXEC" install fastapi uvicorn

echo ""
echo "Setup complete!"
echo ""
echo "To run the pipeline locally:"
echo "1. Activate virtual environment:"
if [[ "$OS_TYPE" == "MINGW"* ]] || [[ "$OS_TYPE" == "MSYS"* ]] || [[ "$OS_TYPE" == "CYGWIN"* ]]; then
    echo "   source $PROJECT_ROOT/venv/Scripts/activate"
else
    echo "   source $PROJECT_ROOT/venv/bin/activate"
fi
echo "2. Run the pipeline:"
echo "   python $PROJECT_ROOT/main.py"
echo "3. Test the API locally:"
echo "   python $PROJECT_ROOT/api_server.py"
echo "   Then visit: http://localhost:8000/"
echo ""
echo "Outputs will be in: $PROJECT_ROOT/final_outputs/"
echo "Visualizations will be in: $PROJECT_ROOT/stage_4_visuals/"
echo ""
echo "For Render deployment, use the build.sh script."