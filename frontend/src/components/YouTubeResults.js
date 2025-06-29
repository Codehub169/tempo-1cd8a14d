import React from 'react';

const DownloadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="inline-block align-middle">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="7 10 12 15 17 10"></polyline>
    <line x1="12" y1="15" x2="12" y2="3"></line>
  </svg>
);

const SpinnerIcon = () => (
  <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
);

const VideoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 align-middle">
      <polygon points="23 7 16 12 23 17 23 7"></polygon>
      <path d="M1 18V6a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2z"></path>
  </svg>
);

const AudioIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 align-middle">
      <path d="M9 18V5l12-2v13"></path>
      <circle cx="6" cy="18" r="3"></circle>
      <circle cx="18" cy="16" r="3"></circle>
  </svg>
);

const YouTubeResults = ({ videoInfo, onDownload, isDownloading }) => {
  if (!videoInfo) return null;

  const { title, channel, duration_string, thumbnail, video_formats, audio_formats, original_url } = videoInfo;

  const FormatItem = ({ format, type }) => {
    const generateFilename = () => {
      const baseTitle = title || 'media_file';
      // Sanitize title: remove characters invalid for most file systems, replace spaces, limit length
      const sanitizedTitle = baseTitle
        .replace(/[<>:"/\\|?*]/g, '_') // Replace forbidden characters with underscore
        .replace(/\s+/g, '_') // Replace sequences of whitespace with a single underscore
        .substring(0, 100); // Limit length to prevent excessively long filenames
      
      const extension = format.ext || (type === 'video' ? 'mp4' : 'm4a');
      return `${sanitizedTitle}.${extension}`;
    };

    return (
      <li className="format-item flex flex-col sm:flex-row justify-between items-start sm:items-center py-3 border-b border-light-border dark:border-dark-border last:border-b-0">
        <div className="format-info mb-2 sm:mb-0">
          <span className="quality block sm:inline-block font-medium text-light-text-primary dark:text-dark-text-primary mr-2 break-all">{format.note || format.resolution || 'N/A'}</span>
          {format.filesize_str && <span className="size text-xs text-light-text-secondary dark:text-dark-text-secondary">(Approx. {format.filesize_str})</span>}
        </div>
        <button 
          onClick={() => onDownload(original_url, format.format_id, type, generateFilename())}
          disabled={isDownloading}
          className="btn btn-download bg-success hover:bg-success-hover text-white py-2 px-4 rounded-md text-sm font-medium min-w-[140px] w-full sm:w-auto flex items-center justify-center gap-1.5 transition-colors duration-200 disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {isDownloading ? <SpinnerIcon /> : <DownloadIcon />}
          <span className="ml-1.5 whitespace-nowrap">{isDownloading ? 'Downloading...' : 'Download'}</span>
        </button>
      </li>
    );
  };

  return (
    <section className="results-section mt-8 animate-fadeIn" id="resultsSection">
      <div className="video-info flex flex-col sm:flex-row gap-6 mb-8 p-6 bg-light-card dark:bg-dark-card rounded-lg shadow-md items-center sm:items-start">
        <div className="video-thumbnail w-full max-w-[240px] sm:w-40 sm:min-w-[160px] sm:h-[90px] bg-light-input-bg dark:bg-dark-input-bg rounded-lg flex items-center justify-center text-light-text-secondary dark:text-dark-text-secondary text-sm overflow-hidden flex-shrink-0 aspect-video sm:aspect-auto">
          {thumbnail ? (
            <img src={thumbnail} alt={`${title || 'Video'} thumbnail`} className="w-full h-full object-cover" />
          ) : (
            <span className="p-2">Thumbnail Not Available</span>
          )}
        </div>
        <div className="video-details text-center sm:text-left flex-grow min-w-0">
          <h3 className="text-xl font-semibold mb-1.5 text-light-text-primary dark:text-dark-text-primary line-clamp-2 break-words" title={title || 'Video Title Will Appear Here'}>{title || 'Video Title Will Appear Here'}</h3>
          <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary mb-1 truncate">Channel: {channel || 'Channel Name'}</p>
          <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">Duration: {duration_string || 'MM:SS'}</p>
        </div>
      </div>

      <div className="formats-container grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="format-group bg-light-card dark:bg-dark-card p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-semibold mb-4 pb-2 border-b border-light-border dark:border-dark-border text-light-text-primary dark:text-dark-text-primary flex items-center">
            <VideoIcon />
            Video Formats
          </h4>
          {video_formats && video_formats.length > 0 ? (
            <ul className="format-list list-none p-0">
              {video_formats.map((format) => (
                <FormatItem key={format.format_id} format={format} type="video" />
              ))}
            </ul>
          ) : (
            <p className="text-light-text-secondary dark:text-dark-text-secondary">No video formats available.</p>
          )}
        </div>

        <div className="format-group bg-light-card dark:bg-dark-card p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-semibold mb-4 pb-2 border-b border-light-border dark:border-dark-border text-light-text-primary dark:text-dark-text-primary flex items-center">
            <AudioIcon />
            Audio Formats
          </h4>
          {audio_formats && audio_formats.length > 0 ? (
            <ul className="format-list list-none p-0">
              {audio_formats.map((format) => (
                <FormatItem key={format.format_id} format={format} type="audio" />
              ))}
            </ul>
          ) : (
            <p className="text-light-text-secondary dark:text-dark-text-secondary">No audio formats available.</p>
          )}
        </div>
      </div>
    </section>
  );
};

export default YouTubeResults;
