import yt_dlp
import asyncio
import os
import tempfile
import logging
from typing import Dict, Any, Tuple, Optional
import shutil

from .youtube_service import _extract_yt_dlp_info, _format_filesize 

logger = logging.getLogger(__name__)

async def fetch_reel_info(url: str) -> Dict[str, Any]:
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
        'extract_flat': 'discard_in_playlist',
        'proxy': "" # Explicitly disable proxy
    }
    info = await _extract_yt_dlp_info(url, ydl_opts)

    full_description = info.get('description') or info.get('title')
    
    display_caption = full_description
    if full_description:
        max_caption_length = 150 
        if len(full_description) > max_caption_length:
            truncated = full_description[:max_caption_length]
            last_space = truncated.rfind(' ')
            if last_space != -1:
                display_caption = truncated[:last_space].rstrip() + "..."
            else:
                display_caption = truncated + "..."
    else:
        display_caption = "No caption available"

    direct_video_url = None
    file_extension = info.get('ext', 'mp4')
    file_size_bytes = info.get('filesize') or info.get('filesize_approx')

    if info.get('url') and info.get('protocol') in ['http', 'https', 'm3u8_native', 'm3u8', 'rtmp']:
        direct_video_url = info.get('url')
    elif info.get('formats'):
        for f in info['formats']:
            if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                direct_video_url = f.get('url')
                file_extension = f.get('ext', file_extension)
                file_size_bytes = f.get('filesize') or f.get('filesize_approx') or file_size_bytes
                break 

    return {
        'id': info.get('id'),
        'uploader': info.get('uploader'),
        'uploader_id': info.get('uploader_id'),
        'title': info.get('title') or full_description, 
        'description': full_description, 
        'caption': display_caption,
        'thumbnail': info.get('thumbnail'),
        'preview_image_url': info.get('thumbnail'), 
        'duration': info.get('duration'),
        'upload_date': info.get('upload_date'), 
        'original_url': info.get('webpage_url', url),
        'direct_video_url': direct_video_url,
        'ext': file_extension,
        'filesize_str': _format_filesize(file_size_bytes) if file_size_bytes is not None else "N/A"
    }

async def download_reel(url: str, filename_prefix: str) -> Tuple[str, str, str]:
    temp_dir = tempfile.mkdtemp(prefix='reelgrab_')
    
    output_template = os.path.join(temp_dir, '%(uploader_id)s_%(id)s.%(ext)s')

    ydl_opts = {
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': False,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best',
        'extract_flat': 'discard_in_playlist',
        'proxy': "" # Explicitly disable proxy
    }

    try:
        info_dict = await _extract_yt_dlp_info(url, ydl_opts)
        
        downloaded_file_path = None
        if info_dict.get('requested_downloads') and len(info_dict['requested_downloads']) > 0:
            downloaded_file_path = info_dict['requested_downloads'][0].get('filepath') or info_dict['requested_downloads'][0].get('filename')
        
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            logger.warning(f"'requested_downloads' did not yield a valid file path for Instagram reel {url}. Path: {downloaded_file_path}. Attempting to find file in temp_dir: {temp_dir}")
            files_in_temp = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            if not files_in_temp:
                raise FileNotFoundError(f"yt-dlp finished but no file was found in the temp directory for Reel: {temp_dir}. URL: {url}")
            downloaded_file_path = max(files_in_temp, key=os.path.getsize)
            logger.info(f"Fallback identified downloaded Reel file: {downloaded_file_path} by size.")

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
             raise FileNotFoundError(f"Downloaded Reel file path could not be determined or does not exist: {downloaded_file_path} for URL: {url}")

        actual_filename_on_disk = os.path.basename(downloaded_file_path)
        logger.info(f"Instagram Reel downloaded to: {downloaded_file_path} (Disk filename: {actual_filename_on_disk}) for URL: {url}")
        
        return temp_dir, downloaded_file_path, actual_filename_on_disk

    except (ValueError, FileNotFoundError) as e: 
        logger.error(f"Error during Reel download for {url}: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True) 
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Reel download for {url}: {str(e)}", exc_info=True)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True) 
        raise ValueError(f"An unexpected error occurred during Reel download for {url}.")