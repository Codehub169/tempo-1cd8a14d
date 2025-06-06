import React from 'react';

const YouTubeResults = ({ videoInfo, onDownload }) => {
  if (!videoInfo) return null;

  const { title, channel, duration, thumbnailUrl, videoFormats, audioFormats } = videoInfo;

  const FormatItem = ({ format, type }) => (
    <li className="format-item flex flex-col sm:flex-row justify-between items-start sm:items-center py-3 border-b border-[color:var(--color-border)] last:border-b-0">
      <div className="format-info mb-2 sm:mb-0">
        <span className="quality block sm:inline-block font-medium text-[color:var(--color-text-primary)] mr-2">{format.quality || format.format_note || format.resolution}</span>
        {format.filesize_approx_str && <span className="size text-xs text-[color:var(--color-text-secondary)]">(Approx. {format.filesize_approx_str})</span>}
      </div>
      <button 
        onClick={() => onDownload(videoInfo.original_url, format.format_id, type, `${title}.${format.ext}`)}
        className="btn btn-download bg-[color:var(--color-success)] hover:bg-[color:var(--color-success-hover)] text-white py-2 px-4 text-sm min-w-[120px] w-full sm:w-auto"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="inline-block mr-1.5 align-middle"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        Download
      </button>
    </li>
  );

  return (
    <section className="results-section mt-8 animate-fadeIn" id="resultsSection">
      <div className="video-info flex flex-col sm:flex-row gap-6 mb-8 p-6 bg-[color:var(--color-card)] rounded-[var(--border-radius)] shadow-[var(--shadow-md)] items-center sm:items-start">
        <div className="video-thumbnail w-full max-w-[240px] sm:w-40 sm:h-[90px] bg-[color:var(--color-input-bg)] rounded-[var(--border-radius)] flex items-center justify-center text-[color:var(--color-text-secondary)] text-sm overflow-hidden flex-shrink-0 aspect-video sm:aspect-auto">
          {thumbnailUrl ? (
            <img src={thumbnailUrl} alt="Video Thumbnail" className="w-full h-full object-cover" />
          ) : (
            <span>Thumbnail</span>
          )}
        </div>
        <div className="video-details text-center sm:text-left">
          <h3 className="text-xl font-semibold mb-1.5 text-[color:var(--color-text-primary)] line-clamp-2" title={title}>{title || 'Video Title Will Appear Here'}</h3>
          <p className="text-sm text-[color:var(--color-text-secondary)] mb-1">Channel: {channel || 'Channel Name'}</p>
          <p className="text-sm text-[color:var(--color-text-secondary)]">Duration: {duration || 'MM:SS'}</p>
        </div>
      </div>

      <div className="formats-container grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="format-group bg-[color:var(--color-card)] p-6 rounded-[var(--border-radius)] shadow-[var(--shadow-md)]">
          <h4 className="text-lg font-semibold mb-4 pb-2 border-b border-[color:var(--color-border)] text-[color:var(--color-text-primary)] flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 align-middle"><polygon points="23 7 16 12 23 17 23 7"></polygon><path d="M1 18V6a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2z"></path></svg>
            Video Formats
          </h4>
          {videoFormats && videoFormats.length > 0 ? (
            <ul className="format-list list-none p-0">
              {videoFormats.map((format) => (
                <FormatItem key={format.format_id} format={format} type="video" />
              ))}
            </ul>
          ) : (
            <p className="text-[color:var(--color-text-secondary)]">No video formats available.</p>
          )}
        </div>

        <div className="format-group bg-[color:var(--color-card)] p-6 rounded-[var(--border-radius)] shadow-[var(--shadow-md)]">
          <h4 className="text-lg font-semibold mb-4 pb-2 border-b border-[color:var(--color-border)] text-[color:var(--color-text-primary)] flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 align-middle"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>
            Audio Formats
          </h4>
          {audioFormats && audioFormats.length > 0 ? (
            <ul className="format-list list-none p-0">
              {audioFormats.map((format) => (
                <FormatItem key={format.format_id} format={format} type="audio" />
              ))}
            </ul>
          ) : (
            <p className="text-[color:var(--color-text-secondary)]">No audio formats available.</p>
          )}
        </div>
      </div>
    </section>
  );
};

export default YouTubeResults;
