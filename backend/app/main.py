import os
import logging
import urllib.request
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import download

# Configure a single logger for this module
# Logging level and format will typically be configured by Uvicorn or a global logging setup.
logger = logging.getLogger(__name__)

# --- BEGIN PROXY CLEAR AT PYTHON APP STARTUP ---
PROXY_ENV_VARS_TO_CLEAR = [
    'HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY', 'SOCKS_PROXY', 'ALL_PROXY', 'NO_PROXY',
    'http_proxy', 'https_proxy', 'ftp_proxy', 'socks_proxy', 'all_proxy', 'no_proxy'
]

logger.info("Attempting to clear proxy environment variables at Python app startup...")
cleared_vars_count = 0
for var_name in PROXY_ENV_VARS_TO_CLEAR:
    if var_name in os.environ:
        original_value = os.environ.pop(var_name, None)
        logger.debug(f"Cleared environment variable at startup: {var_name} (was: {original_value})")
        cleared_vars_count += 1
if cleared_vars_count > 0:
    logger.info(f"Cleared {cleared_vars_count} proxy-related environment variables.")
else:
    logger.info("No proxy-related environment variables found to clear at startup.")
logger.info("Proxy environment variable clearing attempt finished.")
# --- END PROXY CLEAR --- 

# --- BEGIN URLLIB PROXY OVERRIDE --- 
# Explicitly disable proxies for urllib.request, which yt-dlp might use under the hood.
try:
    logger.info("Attempting to install a no-proxy opener for urllib.request.")
    no_proxy_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    urllib.request.install_opener(no_proxy_opener)
    logger.info("Successfully installed no-proxy opener for urllib.request.")
    
    current_proxies = urllib.request.getproxies()
    logger.debug(f"Current urllib.request.getproxies() after override: {current_proxies}")
    if not current_proxies:
        logger.info("urllib.request.getproxies() is empty, confirming no proxies are configured for urllib.request.")
    else:
        logger.warning(f"urllib.request.getproxies() is NOT empty: {current_proxies}. Proxy override might not be fully effective.")
except Exception as e_proxy_override:
    logger.error(f"Failed to install no-proxy opener for urllib.request: {e_proxy_override}", exc_info=True)
# --- END URLLIB PROXY OVERRIDE ---

app = FastAPI(
    title="TubeFetch & ReelGrab API",
    description="API for downloading YouTube videos/audio and Instagram Reels.",
    version="1.0.0",
    # docs_url="/api/docs",  # Default is /docs
    # redoc_url="/api/redoc" # Default is /redoc
)

# CORS Middleware Configuration
# Adjust origins based on your deployment needs.
origins = [
    "http://localhost:3000",  # Common React dev port
    "http://localhost:9000",  # Backend serving frontend directly
    # e.g., "https://your-production-frontend.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Specify methods used by your API
    allow_headers=["Content-Type", "Authorization"], # Specify necessary headers, or use ["*"] if broadly needed
)

# API Routers
app.include_router(download.router, prefix="/api")

# Serve Frontend Static Files
# Assumes main.py is at backend/app/main.py
project_root = Path(__file__).resolve().parent.parent.parent 
frontend_build_path_options = [
    project_root / "frontend" / "build", # For Create React App
    project_root / "frontend" / "dist"  # For Vite, etc.
]

frontend_build_path_resolved = None
for path_option in frontend_build_path_options:
    if path_option.exists() and path_option.is_dir():
        frontend_build_path_resolved = path_option
        logger.info(f"Found frontend build directory at: {frontend_build_path_resolved}")
        break

if frontend_build_path_resolved:
    logger.info(f"Serving frontend static files from: {frontend_build_path_resolved}")
    app.mount("/", StaticFiles(directory=str(frontend_build_path_resolved), html=True), name="static-frontend")
else:
    path_options_str = [str(p) for p in frontend_build_path_options]
    logger.warning(
        f"WARNING: Frontend build directory not found at any of the expected locations: {path_options_str}. "
        f"The frontend will not be served by FastAPI. Ensure your frontend is built and paths are correct relative to project root: {project_root}."
    )

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint to confirm the API is running."""
    return {"status": "ok", "message": "API is responsive"}

# This block allows running the app directly with `python backend/app/main.py` for development/testing.
# Uvicorn's command line (`uvicorn app.main:app --reload`) is preferred for robust server management.
if __name__ == "__main__":
    import uvicorn
    # Basic logging configuration for direct script execution.
    # Uvicorn will typically manage logging when it runs the app.
    logging.basicConfig(
        level=logging.DEBUG, # Use DEBUG for more verbose output when running directly
        format='%(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
    )
    logger.info("Starting Uvicorn server directly for main:app from __main__ block...")
    # Note: --reload is typically handled by the uvicorn CLI command.
    # For direct run, uvicorn.run does not handle reload as smoothly as the CLI.
    uvicorn.run(app, host="0.0.0.0", port=9000)
