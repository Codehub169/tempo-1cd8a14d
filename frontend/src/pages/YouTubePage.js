import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import UrlForm from '../components/UrlForm';
import YouTubeResults from '../components/YouTubeResults';
import { fetchYouTubeInfo, downloadYouTubeMedia } from '../services/api';

const YouTubePage = ({ theme, toggleTheme }) => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isLoadingInfo, setIsLoadingInfo] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false); // Separate state for download
  const [error, setError] = useState(null);
  const [videoInfo, setVideoInfo] = useState(null);
  const [statusMessage, setStatusMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    if (videoInfo || error) {
      const targetElementId = videoInfo ? 'resultsSection' : (error ? 'errorSection' : null);
      if (targetElementId) {
        const targetElement = document.getElementById(targetElementId);
        if (targetElement) {
          targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    }
  }, [videoInfo, error]);

  useEffect(() => {
    if (statusMessage.text) {
      const timer = setTimeout(() => setStatusMessage({ text: '', type: '' }), 3000);
      return () => clearTimeout(timer);
    }
  }, [statusMessage]);

  const handleFetchYouTubeInfo = async () => {
    if (!youtubeUrl) {
      setError('Please enter a YouTube URL.');
      setVideoInfo(null);
      return;
    }
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11}).*/;
    if (!youtubeRegex.test(youtubeUrl)) {
      setError('Invalid YouTube URL format. Please use a valid video link.');
      setVideoInfo(null);
      return;
    }

    setIsLoadingInfo(true);
    setError(null);
    setVideoInfo(null);
    setStatusMessage({ text: '', type: '' });

    try {
      const data = await fetchYouTubeInfo(youtubeUrl);
      setVideoInfo(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch video information.');
      setVideoInfo(null);
    } finally {
      setIsLoadingInfo(false);
    }
  };

  const handleDownload = async (originalUrl, formatId, type, filename) => {
    setIsDownloading(true);
    setStatusMessage({ text: `Preparing ${type} download for ${filename}...`, type: 'success' });
    try {
      await downloadYouTubeMedia(originalUrl, formatId, type, filename);
      setStatusMessage({ text: `${filename} download started!`, type: 'success' });
    } catch (err) {
      setStatusMessage({ text: err.response?.data?.detail || err.message || `Failed to download ${filename}.`, type: 'error' });
      console.error("Download error:", err);
    } finally {
      setIsDownloading(false);
    }
  };

  const FetchIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
      <polyline points="7 10 12 15 17 10"></polyline>
      <line x1="12" y1="15" x2="12" y2="3"></line>
    </svg>
  );

  return (
    <div className="container mx-auto px-4 min-h-screen flex flex-col items-center text-light-text-primary dark:text-dark-text-primary">
      <Header 
        pageTitleMain="Tube" 
        pageTitleHighlight="Fetch" 
        pageSubtitle="Download YouTube videos and audio quickly and easily." 
        theme={theme} 
        toggleTheme={toggleTheme} 
      />
      <main className="w-full max-w-3xl flex-grow">
        <section id="downloaderSection" className="bg-light-card dark:bg-dark-card p-6 md:p-8 rounded-lg shadow-lg mb-8">
          <UrlForm 
            url={youtubeUrl} 
            setUrl={setYoutubeUrl} 
            handleSubmit={handleFetchYouTubeInfo} 
            placeholder="Paste YouTube video URL here (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)" 
            buttonText="Fetch Info" 
            isLoading={isLoadingInfo} 
            buttonIconSvg={<FetchIcon />}
          />
        </section>

        {isLoadingInfo && (
          <section id="loadingSection" className="my-8">
            <div className="bg-light-card dark:bg-dark-card p-8 rounded-lg shadow-md flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-light-border dark:border-dark-border border-t-primary-accent rounded-full animate-spin"></div>
              <p className="text-light-text-secondary dark:text-dark-text-secondary">Processing your link... Please wait.</p>
            </div>
          </section>
        )}

        {error && (
          <section id="errorSection" className="my-8 bg-light-card dark:bg-dark-card p-6 rounded-lg border border-error text-error text-center shadow-md">
            <p className="font-medium">{error}</p>
          </section>
        )}

        {videoInfo && !isLoadingInfo && (
          <YouTubeResults 
            videoInfo={videoInfo} 
            onDownload={handleDownload} 
            isDownloading={isDownloading} 
          />
        )}
        
        {statusMessage.text && (
          <div className={`fixed bottom-5 left-1/2 -translate-x-1/2 py-2 px-4 rounded-md shadow-lg text-white text-sm 
                          ${statusMessage.type === 'success' ? 'bg-primary-accent' : 'bg-error'} transition-opacity duration-300 opacity-100 z-50`}>
            {statusMessage.text}
          </div>
        )}

      </main>
      <footer className="w-full max-w-3xl text-center mt-auto py-6 border-t border-light-border dark:border-dark-border text-light-text-secondary dark:text-dark-text-secondary text-sm">
        <p>&copy; {new Date().getFullYear()} TubeFetch & ReelGrab. For demonstration purposes only.</p>
        <p>We are not affiliated with YouTube or Instagram. Download content responsibly.</p>
      </footer>
    </div>
  );
};

export default YouTubePage;
