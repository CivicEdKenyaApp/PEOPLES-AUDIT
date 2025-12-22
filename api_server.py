import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

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
# FIXED: Using pathlib.Path directly, not FastAPI's Path
ROOT_DIR = Path(os.getenv("PEOPLES_AUDIT_ROOT", "/opt/render/project/src"))

# Paths to your specific output directories (as seen in your file tree)
HTML_VISUALS_DIR = ROOT_DIR / "stage_4_visuals" / "html"
TEST_CHARTS_DIR = ROOT_DIR / "stage_5_validation" / "test_charts" / "html"
DASHBOARD_PATH = ROOT_DIR / "stage_4_visuals" / "dashboard.html"
STAGE_3_DATA_DIR = ROOT_DIR / "stage_3_llm_text"
FINAL_OUTPUTS_DATA_DIR = ROOT_DIR / "final_outputs" / "data"

# List of directories to search for HTML files
HTML_SOURCE_DIRS = [HTML_VISUALS_DIR, TEST_CHARTS_DIR]

# --- CORS Configuration ---
# Allows your React sites on Vercel to embed or fetch these resources
ALLOWED_ORIGINS = [
    "https://civicedkenya.vercel.app",
    "https://ceka254.vercel.app",
    "https://recall254.vercel.app",
    "http://localhost:3000",  # For local development of your sites
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --- Helper Functions ---
def find_html_file(filename: str) -> Optional[Path]:
    """
    Searches all configured HTML source directories for a given filename.
    Returns the full Path if found, otherwise None.
    """
    for base_dir in HTML_SOURCE_DIRS:
        file_path = base_dir / filename
        if file_path.exists() and file_path.suffix.lower() == ".html":
            logger.debug(f"Found HTML file at: {file_path}")
            return file_path
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
                "test_charts": "/test-charts/{filename}",
                "data_files": "/data/{filetype}/{filename}",
                "list_available": "/list"
            }
        }
    )

@app.get("/healthz")
async def health_check():
    """
    Health check endpoint for Render monitoring.
    Render will periodically ping this endpoint to ensure your service is alive.
    """
    return {"status": "healthy", "service": "peoples-audit-api"}

@app.get("/html/{filename}", response_class=HTMLResponse)
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
async def get_sankey(filename: str = "sankey.html"):
    """
    Serves the main Sankey diagram visualization.
    Defaults to 'sankey.html'.
    Example: /sankey?filename=sankey_detailed.html
    """
    file_path = find_html_file(filename)
    if file_path:
        logger.info(f"Serving Sankey diagram: {filename}")
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail=f"Sankey file not found: {filename}")

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serves the main dashboard.html file."""
    if DASHBOARD_PATH.exists():
        logger.info("Serving dashboard.html")
        return HTMLResponse(content=DASHBOARD_PATH.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Dashboard file (dashboard.html) not found.")

@app.get("/test-charts/{filename}", response_class=HTMLResponse)
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
        # Check stage_3_llm_text first, then final_outputs/data
        potential_dirs = [STAGE_3_DATA_DIR, FINAL_OUTPUTS_DATA_DIR]
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
async def list_available_files():
    """
    Returns a JSON index of all available HTML and data files.
    Useful for debugging and for your frontend to know what's available.
    """
    index = {
        "html_visualizations": get_directory_listing(HTML_VISUALS_DIR, "html"),
        "test_charts": get_directory_listing(TEST_CHARTS_DIR, "html"),
        "csv_data_files": get_directory_listing(STAGE_3_DATA_DIR, "csv") + get_directory_listing(FINAL_OUTPUTS_DATA_DIR, "csv"),
        "json_data_files": get_directory_listing(STAGE_3_DATA_DIR, "json") + get_directory_listing(FINAL_OUTPUTS_DATA_DIR, "json"),
        "dashboard_available": DASHBOARD_PATH.exists()
    }
    logger.debug("Generated file listing index.")
    return index

# --- Application Startup Logic ---
@app.on_event("startup")
async def startup_event():
    """Logs the configuration and available files when the API starts."""
    logger.info(f"PEOPLES AUDIT Pipeline API starting up.")
    logger.info(f"Root directory configured as: {ROOT_DIR}")
    logger.info(f"HTML visuals directory: {HTML_VISUALS_DIR} (Exists: {HTML_VISUALS_DIR.exists()})")
    logger.info(f"Dashboard path: {DASHBOARD_PATH} (Exists: {DASHBOARD_PATH.exists()})")

    # Do a quick check for some key files
    if not HTML_VISUALS_DIR.exists():
        logger.warning(f"Primary HTML directory not found: {HTML_VISUALS_DIR}. Pipeline may not have run.")