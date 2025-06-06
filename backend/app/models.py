from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Union

class FormatDetail(BaseModel):
    format_id: str
    ext: str
    resolution: Optional[str] = None # For video
    quality_label: Optional[str] = None # e.g., 720p, 1080p
    filesize: Optional[int] = None
    filesize_str: Optional[str] = None # Human-readable filesize
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    note: Optional[str] = None # e.g. "medium", "ultralow"
    tbr: Optional[float] = None # Average bitrate for audio
    fps: Optional[int] = None # Frames per second for video

class YouTubeVideoInfo(BaseModel):
    id: str
    title: str
    thumbnail: Optional[HttpUrl] = None
    channel: Optional[str] = None
    duration: Optional[int] = None
    duration_string: Optional[str] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None # YYYYMMDD
    description: Optional[str] = None
    video_formats: List[FormatDetail] = []
    audio_formats: List[FormatDetail] = []
    original_url: HttpUrl

class InstagramReelInfo(BaseModel):
    id: str
    uploader: Optional[str] = None
    uploader_id: Optional[str] = None
    title: Optional[str] = None # Often the caption
    description: Optional[str] = None # Full caption
    thumbnail: Optional[HttpUrl] = None
    preview_image_url: Optional[HttpUrl] = None # Alias for thumbnail for frontend consistency
    duration: Optional[float] = None
    upload_date: Optional[str] = None # YYYYMMDD
    direct_video_url: Optional[HttpUrl] = None # If yt-dlp provides a direct link
    original_url: HttpUrl
    caption: Optional[str] = None # Short caption for display

class ErrorResponse(BaseModel):
    detail: str

class DownloadSuccessResponse(BaseModel):
    message: str
    file_path: Optional[str] = None # Path on server, for debugging or internal use
    filename: str # Suggested filename for client

class InfoRequest(BaseModel):
    url: HttpUrl

class YouTubeDownloadRequest(BaseModel):
    url: HttpUrl
    format_id: str
    media_type: str # 'video' or 'audio'
    filename: Optional[str] = None

class InstagramDownloadRequest(BaseModel):
    url: HttpUrl
    filename: Optional[str] = None
