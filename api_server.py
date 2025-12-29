import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- Application Initialization ---
app = FastAPI(
    title="PEOPLES AUDIT Pipeline API",
    description="API to serve HTML visualizations and data outputs from the People's Audit governance pipeline.",
    version="1.0.0"
)

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pipeline_api")

# --- Path Configuration (Based on your Render Environment) ---
ROOT_DIR = Path(os.getenv("PEOPLES_AUDIT_ROOT", "/opt/render/project/src"))

# Paths to your specific output directories
HTML_VISUALS_DIR = ROOT_DIR / "stage_4_visuals" / "html"
CHARTS_HTML_DIR = ROOT_DIR / "stage_4_visuals" / "charts" / "html"
TEST_CHARTS_DIR = ROOT_DIR / "stage_5_validation" / "test_charts" / "html"
DASHBOARD_PATH = ROOT_DIR / "stage_4_visuals" / "dashboard.html"
SANKEY_PATH = ROOT_DIR / "stage_4_visuals" / "sankey.html"
STAGE_3_DATA_DIR = ROOT_DIR / "stage_3_llm_text"
FINAL_OUTPUTS_DATA_DIR = ROOT_DIR / "final_outputs" / "data"

# List of directories to search for HTML files
HTML_SOURCE_DIRS = [HTML_VISUALS_DIR, TEST_CHARTS_DIR, CHARTS_HTML_DIR]

# --- CORS Configuration ---
# Allows your React sites on Vercel to embed or fetch these resources
ALLOWED_ORIGINS = [
    "https://civicedkenya.vercel.app",
    "https://civiceducationkenya.com",
    "https://www.civiceducationkenya.com",
    "https://ceka254.vercel.app",
    "https://recall254.vercel.app",
    "http://localhost:3000",  # For local development of your sites
    "*",  # Allow all origins for iframe embedding (can be restricted if needed)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "OPTIONS"],  # Added HEAD and OPTIONS
    allow_headers=["*"],
)

# --- Static File Mounting ---
# Mount charts directory for static file serving
CHARTS_STATIC_DIR = ROOT_DIR / "stage_4_visuals" / "charts"
if CHARTS_STATIC_DIR.exists():
    try:
        app.mount("/charts", StaticFiles(directory=str(CHARTS_STATIC_DIR)), name="charts")
        logger.info(f"Mounted static files from: {CHARTS_STATIC_DIR}")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")

# --- Helper Functions ---
def find_html_file(filename: str) -> Optional[Path]:
    """
    Searches all configured HTML source directories for a given filename.
    Returns the full Path if found, otherwise None.
    """
    # Also check the root stage_4_visuals directory for sankey.html
    if filename == "sankey.html" and SANKEY_PATH.exists():
        logger.debug(f"Found sankey.html at: {SANKEY_PATH}")
        return SANKEY_PATH
    
    for base_dir in HTML_SOURCE_DIRS:
        file_path = base_dir / filename
        if file_path.exists() and file_path.suffix.lower() == ".html":
            logger.debug(f"Found HTML file at: {file_path}")
            return file_path
    
    # Also check stage_4_visuals root
    root_check = ROOT_DIR / "stage_4_visuals" / filename
    if root_check.exists() and root_check.suffix.lower() == ".html":
        logger.debug(f"Found HTML file at: {root_check}")
        return root_check
    
    logger.warning(f"HTML file not found in any source directory: {filename}")
    return None

def get_directory_listing(directory: Path, extension: str = "*") -> List[str]:
    """Returns a sorted list of files with a given extension in a directory."""
    if not directory.exists():
        return []
    files = [f.name for f in directory.glob(f"*.{extension}") if f.is_file()]
    return sorted(files)

# --- API Endpoints ---

@app.get("/", include_in_schema=False)
@app.head("/", include_in_schema=False)
async def root():
    """Simple redirect to the auto-generated docs."""
    return JSONResponse(
        content={
            "message": "PEOPLES AUDIT Pipeline API",
            "docs_url": "/docs",
            "endpoints": {
                "html_files": "/html/{filename}",
                "sankey": "/sankey",
                "dashboard": "/dashboard",
                "charts": "/charts/html/{filename}",
                "test_charts": "/test-charts/{filename}",
                "data_files": "/data/{filetype}/{filename}",
                "list_available": "/list"
            }
        }
    )

@app.get("/healthz")
@app.head("/healthz")
async def health_check():
    """
    Health check endpoint for Render monitoring.
    Render will periodically ping this endpoint to ensure your service is alive.
    """
    return {"status": "healthy", "service": "peoples-audit-api"}

@app.get("/html/{filename}", response_class=HTMLResponse)
@app.head("/html/{filename}")
async def serve_html(filename: str):
    """
    Dynamically serves any HTML file from the pipeline's output directories.
    Example: /html/sankey.html
    """
    file_path = find_html_file(filename)
    if file_path:
        logger.info(f"Serving HTML: {filename}")
        try:
            html_content = file_path.read_text(encoding="utf-8")
            return HTMLResponse(content=html_content)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Could not read file: {filename}")
    raise HTTPException(status_code=404, detail=f"HTML file not found: {filename}")

@app.get("/sankey", response_class=HTMLResponse)
@app.head("/sankey")
async def get_sankey(theme: str = Query("light", description="Theme: light or dark")):
    """
    Serves the main Sankey diagram visualization.
    Supports theme parameter (light/dark) for iframe embedding.
    Example: /sankey?theme=light
    """
    try:
        # Look for sankey.html in stage_4_visuals directory
        file_path = SANKEY_PATH
        
        # If not found, try searching
        if not file_path.exists():
            file_path = find_html_file("sankey.html")
        
        if file_path and file_path.exists():
            logger.info(f"Serving Sankey diagram (theme: {theme})")
            html_content = file_path.read_text(encoding="utf-8")
            
            # Optionally inject theme into HTML if needed
            # This is a simple approach - you might want to modify the HTML generation
            # to support themes natively
            if theme and theme != "light":
                # You can modify the HTML here to apply dark theme
                # For now, just return the content as-is
                pass
            
            return HTMLResponse(content=html_content)
        else:
            logger.error(f"Sankey file not found at: {SANKEY_PATH}")
            # Try alternative locations
            alt_paths = [
                ROOT_DIR / "stage_4_visuals" / "sankey.html",
                ROOT_DIR / "final_outputs" / "visuals" / "sankey.html",
                HTML_VISUALS_DIR / "sankey.html",
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    logger.info(f"Found sankey.html at alternative location: {alt_path}")
                    return HTMLResponse(content=alt_path.read_text(encoding="utf-8"))
            
            raise HTTPException(
                status_code=404, 
                detail=f"Sankey file not found. Checked: {SANKEY_PATH}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving Sankey diagram: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error serving Sankey diagram: {str(e)}")

@app.get("/dashboard", response_class=HTMLResponse)
@app.head("/dashboard")
async def get_dashboard(theme: str = Query("light", description="Theme: light or dark")):
    """Serves the main dashboard.html file."""
    try:
        # Check primary location
        if DASHBOARD_PATH.exists():
            logger.info(f"Serving dashboard.html (theme: {theme})")
            html_content = DASHBOARD_PATH.read_text(encoding="utf-8")
            return HTMLResponse(content=html_content)
        
        # Try alternative location in charts directory
        alt_dashboard = CHARTS_HTML_DIR.parent / "dashboard.html"
        if alt_dashboard.exists():
            logger.info(f"Serving dashboard.html from charts directory (theme: {theme})")
            html_content = alt_dashboard.read_text(encoding="utf-8")
            return HTMLResponse(content=html_content)
        
        raise HTTPException(
            status_code=404, 
            detail=f"Dashboard file not found. Checked: {DASHBOARD_PATH}, {alt_dashboard}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error serving dashboard: {str(e)}")

@app.get("/test-charts/{filename}", response_class=HTMLResponse)
@app.head("/test-charts/{filename}")
async def get_test_chart(filename: str):
    """
    Serves HTML files from the test_charts directory.
    Example: /test-charts/budget_allocation.html
    """
    file_path = TEST_CHARTS_DIR / filename
    if file_path.exists() and file_path.suffix.lower() == ".html":
        logger.info(f"Serving test chart: {filename}")
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail=f"Test chart not found: {filename}")

@app.get("/data/{filetype}/{filename}")
@app.head("/data/{filetype}/{filename}")
async def get_data_file(filetype: str, filename: str):
    """
    Serves static data files (CSV, JSON, XLSX) from the pipeline outputs.
    Example: /data/csv/budget_analysis.csv
    """
    # Validate filetype
    if filetype not in ["csv", "json", "xlsx"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {filetype}")
    
    # Map file types to their likely directories based on your pipeline
    if filetype in ["csv", "json"]:
        # Check stage_3_llm_text first, then final_outputs/data, then stage_4_visuals
        potential_dirs = [
            STAGE_3_DATA_DIR, 
            FINAL_OUTPUTS_DATA_DIR,
            ROOT_DIR / "stage_4_visuals"  # Also check here for CSV files
        ]
    elif filetype == "xlsx":
        potential_dirs = [FINAL_OUTPUTS_DATA_DIR]
    
    for base_dir in potential_dirs:
        file_path = base_dir / filename
        if file_path.exists():
            logger.info(f"Serving data file: {file_path}")
            # Determine media type for proper browser handling
            media_types = {
                "csv": "text/csv",
                "json": "application/json",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
            return FileResponse(
                path=file_path,
                media_type=media_types.get(filetype, "application/octet-stream"),
                filename=filename
            )

    logger.warning(f"Data file not found: {filename} (type: {filetype})")
    raise HTTPException(status_code=404, detail=f"Data file not found: {filename}")

@app.get("/list", response_class=JSONResponse)
@app.head("/list")
async def list_available_files():
    """
    Returns a JSON index of all available HTML and data files.
    Useful for debugging and for your frontend to know what's available.
    """
    index = {
        "html_visualizations": get_directory_listing(HTML_VISUALS_DIR, "html"),
        "charts_html": get_directory_listing(CHARTS_HTML_DIR, "html"),
        "test_charts": get_directory_listing(TEST_CHARTS_DIR, "html"),
        "csv_data_files": (
            get_directory_listing(STAGE_3_DATA_DIR, "csv") + 
            get_directory_listing(FINAL_OUTPUTS_DATA_DIR, "csv") +
            get_directory_listing(ROOT_DIR / "stage_4_visuals", "csv")
        ),
        "json_data_files": (
            get_directory_listing(STAGE_3_DATA_DIR, "json") + 
            get_directory_listing(FINAL_OUTPUTS_DATA_DIR, "json")
        ),
        "dashboard_available": DASHBOARD_PATH.exists(),
        "sankey_available": SANKEY_PATH.exists(),
        "paths": {
            "root_dir": str(ROOT_DIR),
            "sankey_path": str(SANKEY_PATH),
            "dashboard_path": str(DASHBOARD_PATH),
            "charts_html_dir": str(CHARTS_HTML_DIR),
        }
    }
    logger.debug("Generated file listing index.")
    return index

# --- Application Startup Logic ---
@app.on_event("startup")
async def startup_event():
    """Logs the configuration and available files when the API starts."""
    logger.info("=" * 80)
    logger.info("PEOPLES AUDIT Pipeline API starting up.")
    logger.info("=" * 80)
    logger.info(f"Root directory configured as: {ROOT_DIR}")
    logger.info(f"Root directory exists: {ROOT_DIR.exists()}")
    logger.info(f"HTML visuals directory: {HTML_VISUALS_DIR} (Exists: {HTML_VISUALS_DIR.exists()})")
    logger.info(f"Charts HTML directory: {CHARTS_HTML_DIR} (Exists: {CHARTS_HTML_DIR.exists()})")
    logger.info(f"Dashboard path: {DASHBOARD_PATH} (Exists: {DASHBOARD_PATH.exists()})")
    logger.info(f"Sankey path: {SANKEY_PATH} (Exists: {SANKEY_PATH.exists()})")

    # Do a quick check for some key files
    if not HTML_VISUALS_DIR.exists():
        logger.warning(f"Primary HTML directory not found: {HTML_VISUALS_DIR}. Pipeline may not have run.")
    
    if not SANKEY_PATH.exists():
        logger.warning(f"Sankey file not found at: {SANKEY_PATH}")
        # Check alternative locations
        alt_paths = [
            ROOT_DIR / "stage_4_visuals" / "sankey.html",
            ROOT_DIR / "final_outputs" / "visuals" / "sankey.html",
        ]
        for alt_path in alt_paths:
            if alt_path.exists():
                logger.info(f"Found sankey.html at alternative location: {alt_path}")
                break
        else:
            logger.error("Sankey file not found in any expected location!")
    
    if CHARTS_HTML_DIR.exists():
        chart_files = list(CHARTS_HTML_DIR.glob("*.html"))
        logger.info(f"Found {len(chart_files)} chart HTML files in {CHARTS_HTML_DIR}")
    else:
        logger.warning(f"Charts HTML directory not found: {CHARTS_HTML_DIR}")
    
    logger.info("=" * 80)
