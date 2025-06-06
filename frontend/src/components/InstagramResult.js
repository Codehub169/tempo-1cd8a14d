import React from 'react';

const InstagramResult = ({ reelInfo, onDownload, isLoading }) => {
  if (!reelInfo) return null;

  const { uploader, caption, previewImageUrl, original_url } = reelInfo;

  return (
    <section className="results-section mt-8 animate-fadeIn" id="resultsSection">
      <div className="reel-info flex flex-col items-center gap-6 p-6 bg-[color:var(--color-card)] rounded-[var(--border-radius)] shadow-[var(--shadow-md)]">
        <div className="reel-preview w-full max-w-[270px] aspect-[9/16] bg-[color:var(--color-input-bg)] rounded-[var(--border-radius)] flex items-center justify-center text-[color:var(--color-text-secondary)] text-sm overflow-hidden border border-[color:var(--color-border)]">
          {previewImageUrl ? (
            <img src={previewImageUrl} alt="Reel Preview" className="w-full h-full object-cover" />
          ) : (
            <span>Reel Preview</span>
          )}
        </div>
        <div className="reel-details text-center">
          <h3 className="text-lg font-semibold mb-1 text-[color:var(--color-text-primary)]">{uploader || '@username'}</h3>
          <p className="text-sm text-[color:var(--color-text-secondary)] mb-4 max-h-[60px] overflow-hidden text-ellipsis line-clamp-3" title={caption}>
            {caption || 'Short caption of the reel will appear here...'}
          </p>
        </div>
        <button 
          onClick={() => onDownload(original_url, `${uploader}_reel.mp4`)}
          disabled={isLoading}
          className="btn btn-download-reel bg-[color:var(--color-success)] hover:bg-[color:var(--color-success-hover)] text-white py-3 px-6 text-base w-full max-w-[270px] disabled:bg-[color:var(--color-btn-disabled-bg)] disabled:cursor-not-allowed flex items-center justify-center"
        >
          {isLoading ? (
            <div className="spinner w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="inline-block mr-2 align-middle"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          )}
          {isLoading ? 'Downloading...' : 'Download Reel'}
        </button>
      </div>
    </section>
  );
};

export default InstagramResult;
