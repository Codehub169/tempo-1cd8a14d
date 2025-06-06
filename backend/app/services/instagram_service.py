import yt_dlp
import asyncio
import os
import tempfile
import logging
from typing import Dict, Any, Tuple
import shutil # For robust directory cleanup

# Reusing BackgroundTask and _extract_yt_dlp_info from youtube_service
from .youtube_service import BackgroundTask, _extract_yt_dlp_info 

logger = logging.getLogger(__name__)

async def fetch_reel_info(url: str) -> Dict[str, Any]:
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
        # Consider adding cookiefile option for broader Instagram support if needed:
        # 'cookiefile': 'path/to/instagram_cookies.txt',
    }
    info = await _extract_yt_dlp_info(url, ydl_opts)

    # Map yt-dlp fields to what the frontend expects (uploader, caption, previewImageUrl, id, originalUrl)
    # Instagram Reels might not have a distinct 'title'; 'description' is often the caption.
    caption = info.get('description') or info.get('title') or "No caption available"
    
    # Truncate caption if it's too long for preview
    max_caption_length = 150 
    if caption and len(caption) > max_caption_length:
        caption = caption[:max_caption_length] + "..."

    return {
        'id': info.get('id'),
        'uploader': info.get('uploader', 'N/A'),
        'caption': caption,
        'previewImageUrl': info.get('thumbnail'),
        'duration': info.get('duration'),
        'duration_string': info.get('duration_string'),
        'upload_date': info.get('upload_date'), # YYYYMMDD
        'originalUrl': info.get('webpage_url', url), # Webpage URL or the input URL
        # It's useful to also send the direct video URL if yt-dlp found one, for potential direct linking or alternative download methods
        'direct_video_url': info.get('url') if info.get('ext') == 'mp4' else None, 
    }

async def download_reel(url: str, filename_prefix: str) -> Tuple[str, str]:
    temp_dir = tempfile.mkdtemp(prefix='reelgrab_')
    
    # Instagram Reels are typically MP4. yt-dlp will handle choosing the best format.
    # We'll use filename_prefix for the browser suggestion, yt-dlp determines actual disk name.
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s') # Default title.mp4 or similar
    if filename_prefix:
        # A more controlled output name if desired, but ensure extension is handled by yt-dlp
        # For simplicity, stick to yt-dlp's default title-based naming within temp_dir.
        # The router will use `filename_prefix` for the `FileResponse`'s `filename` argument.
        pass 

    ydl_opts = {
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': False, # Ensure download happens
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Prefer MP4 for Reels
        # 'cookiefile': 'path/to/instagram_cookies.txt', # If needed
        # 'verbose': True,
    }

    try:
        info_dict = await _extract_yt_dlp_info(url, ydl_opts)
        
        downloaded_file_path = None
        if info_dict.get('requested_downloads') and len(info_dict['requested_downloads']) > 0:
            downloaded_file_path = info_dict['requested_downloads'][0].get('filepath')
        
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            logger.warning("'requested_downloads' not found or empty for Instagram, attempting to find file in temp_dir")
            files_in_temp = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            if not files_in_temp:
                raise FileNotFoundError(f"yt-dlp finished but no file was found in the temp directory for Reel: {temp_dir}")
            downloaded_file_path = max(files_in_temp, key=os.path.getctime)
            logger.info(f"Fallback found downloaded Reel file: {downloaded_file_path}")

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
             raise FileNotFoundError(f"Downloaded Reel file path could not be determined or does not exist: {downloaded_file_path}")

        actual_filename_on_disk = os.path.basename(downloaded_file_path)
        logger.info(f"Instagram Reel downloaded to: {downloaded_file_path} (Disk filename: {actual_filename_on_disk})")
        
        return downloaded_file_path, actual_filename_on_disk

    except (ValueError, FileNotFoundError) as e: 
        logger.error(f"Error during Reel download preparation for {url}: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True) 
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Reel download for {url}: {str(e)}", exc_info=True)
        shutil.rmtree(temp_dir, ignore_errors=True) 
        raise ValueError(f"An unexpected error occurred during Reel download: {str(e)}")
