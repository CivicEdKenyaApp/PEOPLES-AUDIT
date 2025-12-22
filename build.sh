#!/bin/bash
# build.sh - Complete Build Script for Render Deployment

echo "Starting Render build process..."
echo "====================================="

# Set the project root (Render uses /opt/render/project/src)
PROJECT_ROOT="/opt/render/project/src"
echo "Project root: $PROJECT_ROOT"

# Create directory structure for Render
echo "Creating directory structure..."
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
mkdir -p "$PROJECT_ROOT/final_outputs"
mkdir -p "$PROJECT_ROOT/final_outputs/summaries"
mkdir -p "$PROJECT_ROOT/final_outputs/visuals"
mkdir -p "$PROJECT_ROOT/final_outputs/reports"
mkdir -p "$PROJECT_ROOT/final_outputs/data"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/temp"

echo "Directory structure created."

# Check Python version
echo ""
echo "Checking Python environment..."
python --version

# Upgrade pip and install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"

# Install API dependencies if not already in requirements.txt
echo "Installing API dependencies..."
pip install fastapi uvicorn

# Run the pipeline to generate HTML outputs
echo ""
echo "Running the People's Audit pipeline..."
cd "$PROJECT_ROOT"

# Check if input files exist
if [ ! -f "$PROJECT_ROOT/input/THE-PEOPLES-AUDIT_compressed.pdf" ]; then
    echo "Warning: Source PDF not found in input directory."
    echo "Creating sample data for demonstration..."
fi

# Run the main pipeline
echo "Executing main pipeline (this may take several minutes)..."
python main.py

# Verify pipeline outputs
echo ""
echo "Verifying pipeline outputs..."

# Check for HTML files in stage_4_visuals/html
HTML_DIR="$PROJECT_ROOT/stage_4_visuals/html"
if [ -d "$HTML_DIR" ]; then
    HTML_FILES=$(find "$HTML_DIR" -name "*.html" | wc -l)
    echo "Found $HTML_FILES HTML files in $HTML_DIR"
    
    if [ "$HTML_FILES" -gt 0 ]; then
        echo "Listing generated HTML files:"
        find "$HTML_DIR" -name "*.html" -exec basename {} \;
    else
        echo "No HTML files generated. Pipeline may have issues."
    fi
else
    echo "HTML directory not created: $HTML_DIR"
fi

# Check for sankey.html specifically
SANKEY_PATH="$PROJECT_ROOT/stage_4_visuals/sankey.html"
if [ -f "$SANKEY_PATH" ]; then
    echo "✓ Sankey diagram generated: $SANKEY_PATH"
else
    echo "✗ Sankey diagram not found at: $SANKEY_PATH"
    # Try to find it elsewhere
    ALTERNATIVE_SANKEY=$(find "$PROJECT_ROOT" -name "sankey.html" -type f | head -1)
    if [ -n "$ALTERNATIVE_SANKEY" ]; then
        echo "Found sankey.html at: $ALTERNATIVE_SANKEY"
        # Copy it to the expected location
        cp "$ALTERNATIVE_SANKEY" "$SANKEY_PATH"
        echo "Copied sankey.html to expected location"
    fi
fi

# Check for dashboard.html
DASHBOARD_PATH="$PROJECT_ROOT/stage_4_visuals/dashboard.html"
if [ -f "$DASHBOARD_PATH" ]; then
    echo "✓ Dashboard generated: $DASHBOARD_PATH"
else
    echo "✗ Dashboard not found at: $DASHBOARD_PATH"
    # Check if it's in charts directory
    CHART_DASHBOARD="$PROJECT_ROOT/stage_4_visuals/charts/dashboard.html"
    if [ -f "$CHART_DASHBOARD" ]; then
        cp "$CHART_DASHBOARD" "$DASHBOARD_PATH"
        echo "Copied dashboard.html from charts directory"
    fi
fi

# Create a simple test HTML if no outputs were generated
if [ ! -f "$SANKEY_PATH" ] && [ ! -f "$DASHBOARD_PATH" ]; then
    echo "Creating minimal test HTML for API..."
    
    # Create test sankey.html
    cat > "$SANKEY_PATH" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>People's Audit - Sankey Diagram</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #2c3e50; }
        .info { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>People's Audit Sankey Diagram</h1>
        <div class="info">
            <p>This is a placeholder Sankey diagram. The full pipeline needs input PDFs to generate complete visualizations.</p>
            <p>For local development, place your PDF files in the <code>input/</code> directory:</p>
            <ul>
                <li><code>THE-PEOPLES-AUDIT_compressed.pdf</code></li>
                <li><code>constitution_of_kenya_2010.pdf</code></li>
            </ul>
            <p>API Endpoints:</p>
            <ul>
                <li><a href="/sankey">/sankey</a> - Sankey diagram</li>
                <li><a href="/dashboard">/dashboard</a> - Dashboard</li>
                <li><a href="/healthz">/healthz</a> - Health check</li>
                <li><a href="/list">/list</a> - List all available files</li>
            </ul>
        </div>
        <div id="chart"></div>
        <script>
            // Simple placeholder chart
            const chartDiv = document.getElementById('chart');
            chartDiv.innerHTML = `
                <div style="background: linear-gradient(90deg, #4CAF50, #2196F3, #FF5722); height: 400px; position: relative; border-radius: 8px; overflow: hidden;">
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; text-align: center;">
                        <h2>Sankey Diagram Placeholder</h2>
                        <p>Public Fund Flows Visualization</p>
                        <p>With actual data, this would show:</p>
                        <ul style="list-style: none; padding: 0;">
                            <li>• Government revenue sources</li>
                            <li>• Public expenditure allocation</li>
                            <li>• Corruption leakage points</li>
                            <li>• Constitutional compliance gaps</li>
                        </ul>
                    </div>
                </div>
            `;
        </script>
    </div>
</body>
</html>
EOF
    
    # Create test dashboard.html
    cat > "$DASHBOARD_PATH" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>People's Audit Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; background: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); }
        header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #eee; }
        h1 { color: #2c3e50; font-size: 2.8rem; margin-bottom: 10px; background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); }
        .stat-value { font-size: 2.5rem; font-weight: bold; margin-bottom: 5px; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        .section { margin: 40px 0; }
        .section-title { color: #2c3e50; font-size: 1.8rem; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }
        .file-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .file-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); border-left: 4px solid #3498db; transition: transform 0.3s ease; }
        .file-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); }
        .file-title { color: #2c3e50; font-size: 1.2rem; margin-bottom: 10px; }
        .file-desc { color: #7f8c8d; font-size: 0.9rem; margin-bottom: 15px; }
        .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; font-weight: 500; transition: background 0.3s ease; }
        .btn:hover { background: #2980b9; }
        .info-box { background: #e8f4fc; border-left: 4px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-chart-line"></i> People's Audit Dashboard</h1>
            <p class="subtitle">Comprehensive Analysis of Kenya's Economic Governance Crisis</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">12.05T</div>
                    <div class="stat-label">Total Public Debt (2025)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">56%</div>
                    <div class="stat-label">Debt Service to Revenue</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">800B</div>
                    <div class="stat-label">Annual Corruption Loss</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">15.5M</div>
                    <div class="stat-label">Food Insecure Kenyans</div>
                </div>
            </div>
        </header>
        
        <div class="info-box">
            <h3><i class="fas fa-info-circle"></i> Deployment Status</h3>
            <p>This is a test dashboard generated for the Render deployment. To see full visualizations:</p>
            <ol>
                <li>Place your PDF files in the <code>input/</code> directory</li>
                <li>Run the pipeline locally with <code>python main.py</code></li>
                <li>Commit the generated HTML files to your repository</li>
                <li>Render will deploy with the actual visualizations</li>
            </ol>
            <p><strong>Current API Endpoints:</strong></p>
            <ul>
                <li><a href="/sankey">/sankey</a> - Sankey diagram visualization</li>
                <li><a href="/dashboard">/dashboard</a> - This dashboard</li>
                <li><a href="/healthz">/healthz</a> - Health check endpoint</li>
                <li><a href="/list">/list</a> - List all available files</li>
                <li><a href="/docs">/docs</a> - Auto-generated API documentation</li>
            </ul>
        </div>
        
        <div class="section">
            <h2 class="section-title"><i class="fas fa-file-alt"></i> Pipeline Outputs</h2>
            <div class="file-grid">
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-project-diagram"></i> Sankey Diagram</h3>
                    <p class="file-desc">Interactive visualization of public fund flows and corruption leakage</p>
                    <a href="/sankey" class="btn" target="_blank"><i class="fas fa-external-link-alt"></i> View Interactive</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-chart-bar"></i> Data Charts</h3>
                    <p class="file-desc">Debt growth, corruption by sector, constitutional violations</p>
                    <a href="/list" class="btn"><i class="fas fa-list"></i> View Available</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-database"></i> JSON Data</h3>
                    <p class="file-desc">Complete extracted data for developers and researchers</p>
                    <a href="/list" class="btn"><i class="fas fa-eye"></i> View Files</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-code"></i> API Documentation</h3>
                    <p class="file-desc">Interactive API docs with all endpoints and examples</p>
                    <a href="/docs" class="btn" target="_blank"><i class="fas fa-book"></i> Open Docs</a>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title"><i class="fas fa-rocket"></i> Embed in Vercel Sites</h2>
            <div class="file-card">
                <h3 class="file-title"><i class="fab fa-react"></i> React/Vite Integration</h3>
                <p>Embed visualizations in CEKA and Nasaka IEBC sites:</p>
                <pre><code>// Option 1: iframe
&lt;iframe 
  src="https://peoples-audit.onrender.com/sankey"
  width="100%" 
  height="900px"
  style={{ border: "none" }}
/&gt;

// Option 2: Fetch and inject
const [html, setHtml] = useState("");
useEffect(() => {
  fetch("https://peoples-audit.onrender.com/sankey")
    .then(res => res.text())
    .then(setHtml);
}, []);
return &lt;div dangerouslySetInnerHTML={{ __html: html }} /&gt;;</code></pre>
            </div>
        </div>
        
        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #7f8c8d; font-size: 0.9rem;">
            <p>People's Audit Pipeline | Data Source: Okoa Uchumi Campaign / TISA</p>
            <p>Deployed on Render | API: https://peoples-audit.onrender.com</p>
            <p>Generated: $(date +"%Y-%m-%d %H:%M") | Pipeline Version: 1.0</p>
        </footer>
    </div>
</body>
</html>
EOF
    
    echo "Created test HTML files for API demonstration"
fi

# Verify API server file exists
if [ ! -f "$PROJECT_ROOT/api_server.py" ]; then
    echo "Error: api_server.py not found in $PROJECT_ROOT"
    exit 1
fi

echo ""
echo "Build process completed successfully!"
echo ""
echo "Pipeline outputs generated in:"
echo "  - $PROJECT_ROOT/stage_4_visuals/html/ (HTML visualizations)"
echo "  - $PROJECT_ROOT/stage_4_visuals/ (Dashboard and sankey)"
echo "  - $PROJECT_ROOT/final_outputs/ (Final outputs)"
echo ""
echo "API will serve files from:"
echo "  - https://peoples-audit.onrender.com/sankey"
echo "  - https://peoples-audit.onrender.com/dashboard"
echo "  - https://peoples-audit.onrender.com/healthz"
echo ""
echo "To embed in Vercel sites, use the URLs above in iframe or fetch calls."