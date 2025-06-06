from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from .routers import download

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TubeFetch & ReelGrab API",
    description="API for downloading YouTube videos/audio and Instagram Reels.",
    version="1.0.0"
)

# CORS Middleware
# Origins for development and production. Adjust as necessary.
# Vite typically uses 5173 or 3000. Create React App uses 3000.
# The backend itself serves the frontend on 9000 in production setup.
origins = [
    "http://localhost:3000",  # Common React dev port (CRA, or Vite fallback)
    # "http://localhost:5173", # Vite default port - removed as per request
    "http://localhost:9000",  # Production port where backend serves frontend
    # Add other origins if deployed elsewhere, e.g., your production frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# API Routers
app.include_router(download.router, prefix="/api")

# Serve Frontend Static Files
# This assumes the frontend is built into 'frontend/build' or 'frontend/dist'
# The startup.sh script handles the build process.
project_root = Path(__file__).resolve().parent.parent.parent # backend/app -> backend -> project_root
frontend_build_path_options = [
    project_root / "frontend" / "build",
    project_root / "frontend" / "dist" # Common for Vite builds
]

frontend_build_path = None
for path_option in frontend_build_path_options:
    if path_option.exists() and path_option.is_dir():
        frontend_build_path = path_option
        logger.info(f"Found frontend build directory at: {frontend_build_path}")
        break

if frontend_build_path:
    logger.info(f"Serving frontend static files from: {frontend_build_path}")
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="static-frontend")
else:
    logger.warning(
        f"WARNING: Frontend build directory not found at expected locations: {frontend_build_path_options}. "
        f"Frontend will not be served by FastAPI. Ensure your frontend is built and the path is correct."
    )

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint to confirm the API is running."""
    return {"status": "ok", "message": "API is responsive"}

# Example of how to configure logging if not done globally
# import uvicorn
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     logger.info("Starting Uvicorn server for main:app")
#     uvicorn.run(app, host="0.0.0.0", port=9000)
