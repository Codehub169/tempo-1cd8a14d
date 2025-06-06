import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import UrlForm from '../components/UrlForm';
import InstagramResult from '../components/InstagramResult';
import { fetchInstagramInfo, downloadInstagramReel } from '../services/api';

const InstagramPage = ({ theme, toggleTheme }) => {
  const [reelUrl, setReelUrl] = useState('');
  const [isLoadingInfo, setIsLoadingInfo] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState(null);
  const [reelInfo, setReelInfo] = useState(null);
  const [statusMessage, setStatusMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    if (reelInfo || error) {
      const targetElementId = reelInfo ? 'resultsSection' : (error ? 'errorSection' : null);
      if (targetElementId) {
        const targetElement = document.getElementById(targetElementId);
        if (targetElement) {
          targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    }
  }, [reelInfo, error]);

  useEffect(() => {
    if (statusMessage.text) {
      const timer = setTimeout(() => setStatusMessage({ text: '', type: '' }), 3000);
      return () => clearTimeout(timer);
    }
  }, [statusMessage]);

  const handleFetchReelInfo = async () => {
    if (!reelUrl) {
      setError('Please enter an Instagram Reel URL.');
      setReelInfo(null);
      return;
    }
    // Basic regex for Instagram Reel URL (standard /reel/ shortcode /)
    const instagramReelRegex = /^https?:\/\/(?:www\.)?instagram\.com\/reel\/([a-zA-Z0-9_-]+)\/?/;
    if (!instagramReelRegex.test(reelUrl)) {
      setError('Invalid Instagram Reel URL format. Please use a valid Reel link (e.g., https://www.instagram.com/reel/Cxyz.../).');
      setReelInfo(null);
      return;
    }

    setIsLoadingInfo(true);
    setError(null);
    setReelInfo(null);
    setStatusMessage({ text: '', type: '' });

    try {
      const data = await fetchInstagramInfo(reelUrl);
      setReelInfo(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch Reel information.');
      setReelInfo(null);
    } finally {
      setIsLoadingInfo(false);
    }
  };

  const handleDownload = async (originalUrl, filename) => {
    setIsDownloading(true);
    setStatusMessage({ text: `Preparing Reel download for ${filename}...`, type: 'success' });
    try {
      await downloadInstagramReel(originalUrl, filename);
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
        pageTitleMain="Reel" 
        pageTitleHighlight="Grab" 
        isInstagramPage={true} 
        pageSubtitle="Download your favorite Instagram Reels instantly." 
        theme={theme} 
        toggleTheme={toggleTheme} 
      />
      <main className="w-full max-w-3xl flex-grow">
        <section id="downloaderSection" className="bg-light-card dark:bg-dark-card p-6 md:p-8 rounded-lg shadow-lg mb-8">
          <UrlForm 
            url={reelUrl} 
            setUrl={setReelUrl} 
            handleSubmit={handleFetchReelInfo} 
            placeholder="Paste Instagram Reel URL here (e.g., https://www.instagram.com/reel/C1a2b3X4Y5Z/)" 
            buttonText="Fetch Reel" 
            isLoading={isLoadingInfo} 
            buttonIconSvg={<FetchIcon />}
          />
        </section>

        {isLoadingInfo && (
          <section id="loadingSection" className="my-8">
            <div className="bg-light-card dark:bg-dark-card p-8 rounded-lg shadow-md flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-light-border dark:border-dark-border border-t-primary-accent rounded-full animate-spin"></div>
              <p className="text-light-text-secondary dark:text-dark-text-secondary">Grabbing your Reel... Please wait.</p>
            </div>
          </section>
        )}

        {error && (
          <section id="errorSection" className="my-8 bg-light-card dark:bg-dark-card p-6 rounded-lg border border-error text-error text-center shadow-md">
            <p className="font-medium">{error}</p>
          </section>
        )}

        {reelInfo && !isLoadingInfo && (
          <InstagramResult 
            reelInfo={reelInfo} 
            onDownload={handleDownload} // This function expects (originalUrl, filename)
            isLoading={isDownloading} // Prop name for InstagramResult is isLoading
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

export default InstagramPage;
