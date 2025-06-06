import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import UrlForm from '../components/UrlForm';
// import InstagramResult from '../components/InstagramResult'; // Will be used later
// import { fetchInstagramInfo } from '../services/api'; // Will be used later

const InstagramPage = ({ theme, toggleTheme }) => {
  const [reelUrl, setReelUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reelInfo, setReelInfo] = useState(null);

  // Effect to scroll to results or error when they appear
  useEffect(() => {
    if (reelInfo || error) {
      const targetElement = document.getElementById(reelInfo ? 'resultsSection' : 'errorSection');
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, [reelInfo, error]);

  const handleFetchReelInfo = async () => {
    if (!reelUrl) {
      setError('Please enter an Instagram Reel URL.');
      setReelInfo(null);
      return;
    }
    if (!reelUrl.includes('instagram.com/reel/')) {
      setError('Invalid Instagram Reel URL format.');
      setReelInfo(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    setReelInfo(null);

    // Simulate API Call
    setTimeout(() => {
      if (reelUrl.includes('error')) { // Simulate error
        setError('This is a simulated error. The Reel could not be processed.');
        setReelInfo(null);
      } else {
        const mockReelData = {
          uploader: reelUrl.includes('Cxyz') ? "@cool_creator123" : "@insta_explorer",
          caption: reelUrl.includes('Cxyz') ? "Just a quick dance challenge! #dance #reel #fun" : "Amazing drone shots of the coastline! #travel #drone",
          previewImageUrl: reelUrl.includes('Cxyz') ? "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDF8fHxlbnwwfHx8fHw%3D&auto=format&fit=crop&w=270&h=480&q=80" : "https://images.unsplash.com/photo-1516900448138-893403b9b0a3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDE0fHx8ZW58MHx8fHx8&auto=format&fit=crop&w=270&h=480&q=80",
          downloadUrl: "#simulated-download-link"
        };
        setReelInfo(mockReelData);
        setError(null);
      }
      setIsLoading(false);
    }, 2500);
  };

  const FetchIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
      <polyline points="7 10 12 15 17 10"></polyline>
      <line x1="12" y1="15" x2="12" y2="3"></line>
    </svg>
  );

  const DownloadIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
    </svg>
  );

  // Placeholder for status message
  const [statusMessage, setStatusMessage] = useState({ text: '', type: '' });
  useEffect(() => {
    if (statusMessage.text) {
      const timer = setTimeout(() => setStatusMessage({ text: '', type: '' }), 3000);
      return () => clearTimeout(timer);
    }
  }, [statusMessage]);

  const handleDownloadReel = () => {
    setStatusMessage({ text: 'Simulating Reel download...', type: 'success' });
    // Actual download logic: window.location.href = reelInfo.downloadUrl;
  };

  return (
    <div className="container mx-auto px-4 min-h-screen flex flex-col items-center text-text-primary">
      <Header 
        pageTitleMain="Reel" 
        pageTitleHighlight="Grab" 
        isInstagramPage={true} 
        pageSubtitle="Download your favorite Instagram Reels instantly." 
        theme={theme} 
        toggleTheme={toggleTheme} 
      />
      <main className="w-full max-w-3xl">
        <section id="downloaderSection" className="bg-card p-6 md:p-8 rounded-lg shadow-lg mb-8">
          <UrlForm 
            url={reelUrl} 
            setUrl={setReelUrl} 
            handleSubmit={handleFetchReelInfo} 
            placeholder="Paste Instagram Reel URL here (e.g., https://www.instagram.com/reel/Cxyz...)" 
            buttonText="Fetch Reel" 
            isLoading={isLoading} 
            buttonIconSvg={<FetchIcon />}
          />
        </section>

        {isLoading && (
          <section id="loadingSection" className="my-8">
            <div className="bg-card p-8 rounded-lg shadow-md flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-border border-t-primary-accent rounded-full animate-spin"></div>
              <p className="text-text-secondary">Grabbing your Reel... Please wait.</p>
            </div>
          </section>
        )}

        {error && (
          <section id="errorSection" className="my-8 bg-card p-6 rounded-lg border border-error text-error text-center shadow-md">
            <p className="font-medium">{error}</p>
          </section>
        )}

        {reelInfo && !isLoading && (
          <section id="resultsSection" className="my-8 animate-fadeIn">
            <div className="reel-info bg-card p-6 rounded-lg shadow-md flex flex-col items-center gap-6">
              <div className="reel-preview w-full max-w-[270px] aspect-[9/16] bg-input-bg rounded-lg overflow-hidden border border-border flex-shrink-0">
                {reelInfo.previewImageUrl ? 
                  <img src={reelInfo.previewImageUrl} alt="Reel Preview" className="w-full h-full object-cover" /> :
                  <span className="flex items-center justify-center h-full text-text-secondary text-sm">Reel Preview</span>
                }
              </div>
              <div className="reel-details text-center">
                <h3 className="text-lg font-semibold mb-1 text-text-primary">{reelInfo.uploader}</h3>
                <p className="text-sm text-text-secondary mb-4 max-h-[60px] overflow-hidden text-ellipsis">{reelInfo.caption}</p>
              </div>
              <button 
                onClick={handleDownloadReel}
                className="btn-download-reel bg-success text-white py-3 px-6 rounded-md text-base font-medium hover:bg-success-hover transition-colors duration-200 flex items-center justify-center gap-2 w-full max-w-[270px]">
                <DownloadIcon /> Download Reel
              </button>
            </div>
          </section>
        )}

        {statusMessage.text && (
          <div className={`fixed bottom-5 left-1/2 -translate-x-1/2 py-2 px-4 rounded-md shadow-lg text-white text-sm 
                          ${statusMessage.type === 'success' ? 'bg-primary-accent' : 'bg-error'} transition-opacity duration-300 opacity-100`}>
            {statusMessage.text}
          </div>
        )}

      </main>
      <footer className="w-full max-w-3xl text-center mt-auto py-6 border-t border-border text-text-secondary text-sm">
        <p>&copy; {new Date().getFullYear()} TubeFetch & ReelGrab. For demonstration purposes only.</p>
        <p>We are not affiliated with YouTube or Instagram. Download content responsibly.</p>
      </footer>
    </div>
  );
};

export default InstagramPage;
