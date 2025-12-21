from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path as PathlibPath
import os
import logging

# Initialize FastAPI
app = FastAPI(title="Peoples Audit Pipeline API", description="Serves HTML visualizations and outputs of the Peoples Audit pipeline")

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("pipeline_api")

# Environment paths
ROOT_DIR = PathlibPath(os.getenv("PEOPLES_AUDIT_ROOT", "/app"))
HTML_DIR = ROOT_DIR / "stage_4_visuals" / "html"
TEST_HTML_DIR = ROOT_DIR / "stage_5_validation" / "test_charts" / "html"
DASHBOARD_HTML = ROOT_DIR / "stage_4_visuals" / "dashboard.html"
OUTPUT_DIRS = [HTML_DIR, TEST_HTML_DIR]

# CORS middleware to allow embedding on external sites (CEKA/Nasaka)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

# Serve any HTML file dynamically from main HTML directory
@app.get("/html/{filename}", response_class=HTMLResponse)
async def serve_html(filename: str):
    for base_dir in OUTPUT_DIRS:
        file_path = base_dir / filename
        if file_path.exists() and file_path.suffix.lower() == ".html":
            logger.info(f"Serving HTML file: {file_path}")
            return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    logger.warning(f"Requested HTML file not found: {filename}")
    raise HTTPException(status_code=404, detail=f"HTML file not found: {filename}")

# Serve dashboard HTML
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    if DASHBOARD_HTML.exists():
        return HTMLResponse(content=DASHBOARD_HTML.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Dashboard not found")

# Serve specific Sankey visualization (default: sankey.html)
@app.get("/sankey", response_class=HTMLResponse)
async def get_sankey(filename: str = "sankey.html"):
    sankey_path = HTML_DIR / filename
    if sankey_path.exists():
        logger.info(f"Serving Sankey: {filename}")
        return HTMLResponse(content=sankey_path.read_text(encoding="utf-8"))
    logger.warning(f"Sankey file not found: {filename}")
    raise HTTPException(status_code=404, detail="Sankey file not found")

# Serve test chart HTML files
@app.get("/test-charts/{filename}", response_class=HTMLResponse)
async def get_test_chart(filename: str):
    file_path = TEST_HTML_DIR / filename
    if file_path.exists() and file_path.suffix.lower() == ".html":
        logger.info(f"Serving Test Chart: {filename}")
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail=f"Test chart not found: {filename}")

# Serve static CSV/JSON outputs dynamically if needed
@app.get("/outputs/{filetype}/{filename}")
async def get_output_file(
    filetype: str = Path(..., regex="^(csv|json)$"),
    filename: str = Query(...)
):
    dir_map = {
        "csv": ROOT_DIR / "stage_3_llm_text",
        "json": ROOT_DIR / "stage_3_llm_text"
    }
    base_dir = dir_map.get(filetype)
    if base_dir is None:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    file_path = base_dir / filename
    if file_path.exists():
        logger.info(f"Serving output file: {file_path}")
        return FileResponse(path=file_path, media_type="application/octet-stream", filename=filename)
    raise HTTPException(status_code=404, detail=f"File not found: {filename}")

# Optional: Serve the latest HTML files index
@app.get("/list-html")
async def list_html():
    result = {}
    for base_dir in OUTPUT_DIRS:
        html_files = [f.name for f in base_dir.glob("*.html")]
        result[str(base_dir)] = html_files
    return result
