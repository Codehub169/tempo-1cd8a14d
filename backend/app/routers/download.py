from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel # BaseModel is used for request bodies, not needed for GET query params here
import os
import logging

from ..services import youtube_service, instagram_service
from ..services.youtube_service import BackgroundTask # Import for cleanup task

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models are typically for request bodies (POST, PUT). 
# For GET requests with query parameters, FastAPI handles validation directly.

@router.get("/youtube/info", tags=["YouTube"])
async def get_youtube_info_route(url: str = Query(..., description="The YouTube video URL")):
    """Fetches information and available formats for a YouTube video."""
    try:
        logger.info(f"Fetching YouTube info for URL: {url}")
        info = await youtube_service.fetch_video_info(url)
        if not info:
            raise HTTPException(status_code=404, detail="Video information not found or could not be processed.")
        return info
    except ValueError as ve:
        logger.error(f"Validation error fetching YouTube info for {url}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching YouTube info for {url}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.get("/youtube/download", tags=["YouTube"])
async def download_youtube_media_route(
    url: str = Query(..., description="The YouTube video URL"), 
    format_id: str = Query(..., description="The format ID to download"), 
    media_type: str = Query(..., alias="type", description="The type of media ('video' or 'audio')"), 
    filename: str = Query(..., description="Desired filename for the download")
):
    """Downloads YouTube video or audio for a given format ID."""
    try:
        logger.info(f"YouTube download request: URL={url}, FormatID={format_id}, Type={media_type}, Filename={filename}")
        file_path, actual_filename_on_disk = await youtube_service.download_media(url, format_id, media_type, filename)
        
        # Use the user-provided filename for Content-Disposition, but serve the actual file from disk.
        return FileResponse(
            path=file_path,
            filename=filename, # This is the filename suggested to the browser
            media_type='application/octet-stream',
            background=BackgroundTask(os.remove, file_path) # Cleanup task
        )
    except ValueError as ve:
        logger.error(f"Validation error downloading YouTube media for {url}, format {format_id}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fnfe:
        logger.error(f"File not found during YouTube download for {url}, format {format_id}: {str(fnfe)}")
        raise HTTPException(status_code=404, detail="Downloaded file could not be found on server.")
    except Exception as e:
        logger.error(f"Error downloading YouTube media for {url}, format {format_id}: {str(e)}", exc_info=True)
        # Ensure temp file is cleaned up if an error occurs before FileResponse is created
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temp file {file_path} due to error.")
            except Exception as cleanup_e:
                logger.error(f"Error cleaning up temp file {file_path}: {cleanup_e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred during download: {str(e)}")

@router.get("/instagram/info", tags=["Instagram"])
async def get_instagram_info_route(url: str = Query(..., description="The Instagram Reel URL")):
    """Fetches information about an Instagram Reel."""
    try:
        logger.info(f"Fetching Instagram info for URL: {url}")
        info = await instagram_service.fetch_reel_info(url)
        if not info:
            raise HTTPException(status_code=404, detail="Reel information not found or could not be processed.")
        return info
    except ValueError as ve:
        logger.error(f"Validation error fetching Instagram info for {url}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching Instagram info for {url}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.get("/instagram/download", tags=["Instagram"])
async def download_instagram_reel_route(
    url: str = Query(..., description="The Instagram Reel URL"), 
    filename: str = Query(..., description="Desired filename for the download")
):
    """Downloads an Instagram Reel."""
    try:
        logger.info(f"Instagram Reel download request: URL={url}, Filename={filename}")
        file_path, actual_filename_on_disk = await instagram_service.download_reel(url, filename)
        
        return FileResponse(
            path=file_path, 
            filename=filename, # This is the filename suggested to the browser
            media_type='video/mp4', # Reels are typically MP4
            background=BackgroundTask(os.remove, file_path) # Cleanup task
        )
    except ValueError as ve:
        logger.error(f"Validation error downloading Instagram Reel for {url}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fnfe:
        logger.error(f"File not found during Instagram Reel download for {url}: {str(fnfe)}")
        raise HTTPException(status_code=404, detail="Downloaded file could not be found on server.")
    except Exception as e:
        logger.error(f"Error downloading Instagram Reel for {url}: {str(e)}", exc_info=True)
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temp file {file_path} due to error.")
            except Exception as cleanup_e:
                logger.error(f"Error cleaning up temp file {file_path}: {cleanup_e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred during download: {str(e)}")
