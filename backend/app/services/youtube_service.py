import yt_dlp
import asyncio
import os
import tempfile
import logging
from typing import Dict, Any, Tuple, List, Optional
import shutil
import math
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

# Helper context manager to temporarily unset environment variables
@contextmanager
def temp_unset_env_vars(vars_to_unset: List[str]):
    original_values = {}
    for var in vars_to_unset:
        if var in os.environ:
            original_values[var] = os.environ[var]
            del os.environ[var]
    try:
        yield
    finally:
        for var, value in original_values.items():
            os.environ[var] = value

def _format_filesize(size_bytes: Optional[int]) -> str:
    if size_bytes is None or size_bytes <= 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    if size_bytes < 1024: # Avoid log issues for small byte values by handling them directly
        return f"{size_bytes} B"
    i = int(math.floor(math.log(size_bytes, 1024)))
    # Ensure 'i' is within the bounds of size_name tuple
    i = max(0, min(i, len(size_name) - 1))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

async def _extract_yt_dlp_info(url: str, ydl_opts: Dict, cookiefile_path: Optional[str] = None) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    
    ydl_opts_processed = ydl_opts.copy()
    # Forcefully disable proxy and ignore external yt-dlp config files.
    ydl_opts_processed["proxy"] = ""
    ydl_opts_processed["ignoreconfig"] = True

    if cookiefile_path:
        cookie_path_obj = Path(cookiefile_path)
        if cookie_path_obj.exists() and cookie_path_obj.is_file():
            ydl_opts_processed['cookies'] = str(cookie_path_obj)
            logger.info(f"Using cookie file for yt-dlp: {cookiefile_path}")
        else:
            logger.warning(f"Cookie file specified ({cookiefile_path}) but not found or not a file. Proceeding without cookies.")
    else:
        logger.debug("No cookie file specified for yt-dlp.")

    proxy_env_vars_to_clear = [
        'HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY', 'SOCKS_PROXY',
        'http_proxy', 'https_proxy', 'ftp_proxy', 'socks_proxy',
        'ALL_PROXY', 'NO_PROXY', 
        'all_proxy', 'no_proxy'
    ]

    try:
        with temp_unset_env_vars(proxy_env_vars_to_clear):
            with yt_dlp.YoutubeDL(ydl_opts_processed) as ydl:
                info = await loop.run_in_executor(
                    None, 
                    lambda: ydl.extract_info(url, download=not ydl_opts_processed.get('skip_download', True))
                )
            return info
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp DownloadError processing {url} with options {ydl_opts_processed}: {str(e)}")
        if "Unsupported URL" in str(e):
            raise ValueError(f"The provided URL is not supported: {url}")
        if "Video unavailable" in str(e):
            raise ValueError("This video is unavailable. It may have been removed or restricted.")
        if "Private video" in str(e):
            raise ValueError("This video is private and cannot be accessed.")
        if "Login required" in str(e).lower() or "authentication required" in str(e).lower():
             raise ValueError("This content requires login or authentication. If you have a cookies file, ensure YOUTUBE_COOKIES_FILE environment variable is set correctly and points to a valid file.")
        raise ValueError(f"Could not process URL '{url}'. The content may be region-restricted, private, unavailable, or a network issue occurred: {e}")
    except Exception as e:
        logger.error(f"Unexpected error with yt-dlp for {url} with options {ydl_opts_processed}: {str(e)}", exc_info=True)
        raise ValueError(f"Unexpected error while processing URL '{url}': {e}")

def _get_height_from_resolution(resolution_str: Optional[str]) -> int:
    """Safely extracts height from a resolution string like '1920x1080'."""
    if resolution_str and isinstance(resolution_str, str) and 'x' in resolution_str:
        parts = resolution_str.split('x')
        if len(parts) == 2:
            try:
                return int(parts[1])
            except ValueError:
                return 0 # Height part is not a valid integer
    return 0 # Not a valid resolution string or no height found

async def fetch_video_info(url: str) -> Dict[str, Any]:
    youtube_cookies_file = os.getenv("YOUTUBE_COOKIES_FILE")
    if youtube_cookies_file:
        logger.info(f"YOUTUBE_COOKIES_FILE environment variable is set. Will attempt to use: {youtube_cookies_file}")
    else:
        logger.debug("YOUTUBE_COOKIES_FILE environment variable is not set. Proceeding without cookies.")

    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True, 
        'forcejson': True,
        'youtube_include_dash_manifest': False,
        'extract_flat': 'discard_in_playlist',
    }
    info = await _extract_yt_dlp_info(url, ydl_opts, cookiefile_path=youtube_cookies_file)

    video_formats: List[Dict[str, Any]] = []
    audio_formats: List[Dict[str, Any]] = []

    if info.get('formats'):
        for f in info['formats']:
            filesize = f.get('filesize') or f.get('filesize_approx')
            filesize_str = _format_filesize(filesize)
            
            common_format_info = {
                'format_id': f.get('format_id'),
                'ext': f.get('ext'),
                'filesize': filesize,
                'filesize_str': filesize_str,
                'note': f.get('format_note'), 
            }

            if (f.get('vcodec') != 'none' and f.get('acodec') != 'none' and 
                f.get('ext') in ['mp4', 'webm', 'mkv', 'flv'] and 
                filesize and f.get('width') and f.get('height')):
                video_formats.append({
                    **common_format_info,
                    'resolution': f.get('resolution') or f"{f['width']}x{f['height']}",
                    'fps': f.get('fps'),
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                })
            elif (f.get('acodec') != 'none' and f.get('vcodec') == 'none' and 
                  f.get('ext') in ['m4a', 'mp3', 'opus', 'ogg', 'wav', 'aac'] and filesize):
                audio_formats.append({
                    **common_format_info,
                    'acodec': f.get('acodec'),
                    'tbr': f.get('abr'), 
                })
    
    video_formats.sort(key=lambda x: (_get_height_from_resolution(x.get('resolution')), x.get('filesize') or 0), reverse=True)
    audio_formats.sort(key=lambda x: (x.get('tbr') or 0, x.get('filesize') or 0), reverse=True)

    return {
        'id': info.get('id'),
        'title': info.get('title', 'N/A'),
        'thumbnail': info.get('thumbnail'),
        'description': info.get('description'),
        'duration': info.get('duration'),
        'duration_string': info.get('duration_string'),
        'channel': info.get('uploader') or info.get('channel'),
        'view_count': info.get('view_count'),
        'upload_date': info.get('upload_date'),
        'video_formats': video_formats,
        'audio_formats': audio_formats,
        'original_url': info.get('webpage_url', url)
    }

async def download_media(url: str, format_id: str, media_type: str, client_filename: str) -> Tuple[str, str, str]:
    youtube_cookies_file = os.getenv("YOUTUBE_COOKIES_FILE")
    if youtube_cookies_file:
        logger.info(f"YOUTUBE_COOKIES_FILE environment variable is set for download. Will attempt to use: {youtube_cookies_file}")
    else:
        logger.debug("YOUTUBE_COOKIES_FILE environment variable is not set for download. Proceeding without cookies.")

    temp_dir = tempfile.mkdtemp(prefix='tubefetch_')
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s') 

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': False, 
        'extract_flat': 'discard_in_playlist',
    }

    try:
        info_dict = await _extract_yt_dlp_info(url, ydl_opts, cookiefile_path=youtube_cookies_file)
        
        downloaded_file_path = None
        if info_dict.get('requested_downloads') and len(info_dict['requested_downloads']) > 0:
            downloaded_file_path = info_dict['requested_downloads'][0].get('filepath') or info_dict['requested_downloads'][0].get('filename')
        
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            logger.warning(f"'requested_downloads' did not yield a valid file path for {url}, format {format_id}. Path: {downloaded_file_path}. Searching in temp_dir: {temp_dir}")
            files_in_temp = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            if not files_in_temp:
                raise FileNotFoundError(f"yt-dlp finished but no file was found in the temp directory: {temp_dir}. URL: {url}, Format: {format_id}")
            downloaded_file_path = max(files_in_temp, key=os.path.getsize) 
            logger.info(f"Fallback identified downloaded file: {downloaded_file_path} by size.")

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
             raise FileNotFoundError(f"Downloaded file path could not be determined or does not exist: {downloaded_file_path} for URL: {url}, Format: {format_id}")

        actual_filename_on_disk = os.path.basename(downloaded_file_path)
        logger.info(f"Media downloaded to: {downloaded_file_path} (Disk filename: {actual_filename_on_disk}, Client filename hint: {client_filename}) for URL: {url}")
        
        return temp_dir, downloaded_file_path, actual_filename_on_disk

    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Error during media download for {url}, format {format_id}: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise 
    except Exception as e:
        logger.error(f"Unexpected error during media download for {url}, format {format_id}: {str(e)}", exc_info=True)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError(f"Unexpected error while processing URL '{url}' during download: {e}")
