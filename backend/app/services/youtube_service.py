import yt_dlp
import asyncio
import os
import tempfile
import logging
from typing import Dict, Any, Tuple, List, Optional
import shutil
import math

logger = logging.getLogger(__name__)

def _format_filesize(size_bytes: Optional[int]) -> str:
    if size_bytes is None or size_bytes <= 0: # Handles 0 or None explicitly
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    # Ensure i is within the bounds of size_name
    i = max(0, min(i, len(size_name) - 1))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

async def _extract_yt_dlp_info(url: str, ydl_opts: Dict) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    try:
        # Ensure 'proxy' is applied if not already present, for safety, though it will be added by calling functions
        ydl_opts_with_proxy = ydl_opts.copy()
        ydl_opts_with_proxy.setdefault("proxy", "") # Ensure proxy is set if not passed

        with yt_dlp.YoutubeDL(ydl_opts_with_proxy) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=ydl_opts_with_proxy.get('skip_download', True) is False))
            return info
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp DownloadError processing {url}: {str(e)}")
        # More specific error messages for the user
        if "Unsupported URL" in str(e):
            raise ValueError(f"The provided URL is not supported: {url}")
        if "Video unavailable" in str(e):
            raise ValueError("This video is unavailable. It may have been removed or restricted.")
        if "Private video" in str(e):
            raise ValueError("This video is private and cannot be accessed.")
        if "Login required" in str(e).lower() or "authentication required" in str(e).lower():
             raise ValueError("This content requires login or authentication, which is not supported.")
        # Generic yt-dlp error
        raise ValueError(f"Could not process URL ({url}). The content may be region-restricted, private, or unavailable.")
    except Exception as e:
        logger.error(f"Unexpected error with yt-dlp for {url}: {str(e)}", exc_info=True)
        raise ValueError(f"An unexpected error occurred while processing URL ({url}).")

async def fetch_video_info(url: str) -> Dict[str, Any]:
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
        'youtube_include_dash_manifest': False, # Avoids overly verbose DASH formats
        'extract_flat': 'discard_in_playlist', # If a playlist URL is mistakenly given, process only the main video part
        'proxy': "" # Explicitly disable proxy
    }
    info = await _extract_yt_dlp_info(url, ydl_opts)

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
                'note': f.get('format_note', '')
            }

            # Video formats (with audio, common containers)
            if (f.get('vcodec') != 'none' and f.get('acodec') != 'none' and 
                f.get('ext') in ['mp4', 'webm'] and filesize and f.get('width') and f.get('height')):
                video_formats.append({
                    **common_format_info,
                    'resolution': f.get('resolution') or f'{f.get("width")}x{f.get("height")}',
                    'fps': f.get('fps'),
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                })
            # Audio-only formats (common containers)
            elif (f.get('acodec') != 'none' and f.get('vcodec') == 'none' and 
                  f.get('ext') in ['m4a', 'mp3', 'opus', 'ogg', 'wav'] and filesize):
                audio_formats.append({
                    **common_format_info,
                    'acodec': f.get('acodec'),
                    'tbr': f.get('abr'), # Total Bitrate (abr is often used for audio bitrate in yt-dlp)
                })
    
    # Sort by height (desc), then filesize (desc) for video
    video_formats.sort(key=lambda x: (x.get('height', 0) if isinstance(x.get('resolution', ''), str) and 'x' in x['resolution'] else 0, x.get('filesize') or 0), reverse=True)
    # Sort by bitrate (desc), then filesize (desc) for audio
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
        'upload_date': info.get('upload_date'), # YYYYMMDD format
        'video_formats': video_formats,
        'audio_formats': audio_formats,
        'original_url': info.get('webpage_url', url)
    }

async def download_media(url: str, format_id: str, media_type: str, filename_prefix: str) -> Tuple[str, str, str]:
    temp_dir = tempfile.mkdtemp(prefix='tubefetch_')
    
    # Use a generic output template, actual filename will be derived from yt-dlp info or client's request
    output_template = os.path.join(temp_dir, '%(id)s.%(ext)s') 

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': False,
        'extract_flat': 'discard_in_playlist',
        'proxy': "" # Explicitly disable proxy
    }

    try:
        # First, extract info to get the correct title and extension for the chosen format
        # This avoids downloading with a potentially incorrect client-provided filename_prefix structure
        info_ydl_opts = ydl_opts.copy()
        info_ydl_opts['skip_download'] = True
        info_dict_for_meta = await _extract_yt_dlp_info(url, info_ydl_opts)

        # Find the specific format details to get the extension
        chosen_format_ext = 'mp4' # Default extension
        if info_dict_for_meta.get('formats'):
            for f_meta in info_dict_for_meta['formats']:
                if f_meta.get('format_id') == format_id:
                    chosen_format_ext = f_meta.get('ext', chosen_format_ext)
                    break
        elif info_dict_for_meta.get('ext'): # For single file info
            chosen_format_ext = info_dict_for_meta.get('ext', chosen_format_ext)

        # Construct a safer output template using the fetched title and determined extension
        # yt-dlp sanitizes these fields. filename_prefix is used by the router for Content-Disposition.
        # The actual on-disk name pattern is controlled here.
        safe_title = info_dict_for_meta.get('title', 'media')
        # Replace problematic characters for filenames, yt-dlp outtmpl does this, but good to be aware
        # For simplicity, we let yt-dlp handle the final naming via its template processing.
        # The key is that `output_template` uses yt-dlp fields.
        ydl_opts['outtmpl'] = os.path.join(temp_dir, f'%(title)s.%(ext)s') 

        # Now perform the download
        info_dict = await _extract_yt_dlp_info(url, ydl_opts)
        
        downloaded_file_path = None
        if info_dict.get('requested_downloads') and len(info_dict['requested_downloads']) > 0:
            downloaded_file_path = info_dict['requested_downloads'][0].get('filepath')
        
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            logger.warning(f"'requested_downloads' not found or empty for {url}, format {format_id}. Attempting to find file in temp_dir: {temp_dir}")
            # Fallback: list files in temp_dir and pick the most likely one
            # This is a safeguard. yt-dlp should populate 'requested_downloads'.
            files_in_temp = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            if not files_in_temp:
                raise FileNotFoundError(f"yt-dlp finished but no file was found in the temp directory: {temp_dir}. URL: {url}, Format: {format_id}")
            # Heuristic: largest file or latest modified (if timestamps are reliable)
            downloaded_file_path = max(files_in_temp, key=lambda x: (os.path.getsize(x), os.path.getmtime(x)))
            logger.info(f"Fallback identified downloaded file: {downloaded_file_path}")

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
             raise FileNotFoundError(f"Downloaded file path could not be determined or does not exist: {downloaded_file_path} for URL: {url}, Format: {format_id}")

        actual_filename_on_disk = os.path.basename(downloaded_file_path)
        logger.info(f"Media downloaded to: {downloaded_file_path} (Disk filename: {actual_filename_on_disk}) for URL: {url}")
        
        # The router will use filename_prefix for the Content-Disposition header.
        # The actual_filename_on_disk is what's on the server.
        return temp_dir, downloaded_file_path, actual_filename_on_disk

    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Error during media download for {url}, format {format_id}: {str(e)}")
        if os.path.exists(temp_dir): # Ensure temp_dir was created
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during media download for {url}, format {format_id}: {str(e)}", exc_info=True)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        # Re-raise as ValueError for consistent error handling by the router for client-facing messages
        raise ValueError(f"An unexpected error occurred during download for {url}: {str(e)}")
