import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import UrlForm from '../components/UrlForm';
// import YouTubeResults from '../components/YouTubeResults'; // Will be used later
// import { fetchYouTubeInfo } from '../services/api'; // Will be used later

const YouTubePage = ({ theme, toggleTheme }) => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [videoInfo, setVideoInfo] = useState(null);

  // Effect to scroll to results or error when they appear
  useEffect(() => {
    if (videoInfo || error) {
      const targetElement = document.getElementById(videoInfo ? 'resultsSection' : 'errorSection');
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, [videoInfo, error]);

  const handleFetchYouTubeInfo = async () => {
    if (!youtubeUrl) {
      setError('Please enter a YouTube URL.');
      setVideoInfo(null);
      return;
    }
    if (!youtubeUrl.includes('youtube.com/watch?v=') && !youtubeUrl.includes('youtu.be/')) {
      setError('Invalid YouTube URL format. Please use a valid video link.');
      setVideoInfo(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    setVideoInfo(null);

    // Simulate API Call
    setTimeout(() => {
      if (youtubeUrl.includes('error')) { // Simulate error
        setError('This is a simulated error. The video could not be processed.');
        setVideoInfo(null);
      } else {
        const mockData = {
          title: youtubeUrl.includes('dQw4w9WgXcQ') ? "Rick Astley - Never Gonna Give You Up" : "Epic Nature Documentary - 4K Film",
          channel: youtubeUrl.includes('dQw4w9WgXcQ') ? "Rick Astley" : "Nature Wonders HD",
          duration: youtubeUrl.includes('dQw4w9WgXcQ') ? "03:32" : "47:12",
          thumbnailUrl: youtubeUrl.includes('dQw4w9WgXcQ') ? "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg" : "https://images.unsplash.com/photo-1500964757637-c85e8a162699?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bmF0dXJlJTIwbGFuZHNjYXBlfGVufDB8fDB8fHww&auto=format&fit=crop&w=160&h=90",
          videoFormats: [
            { quality: "MP4 2160p (4K)", size: "1.2 GB", type: "video", id: "v1" },
            { quality: "MP4 1080p (HD)", size: "450 MB", type: "video", id: "v2" },
          ],
          audioFormats: [
            { quality: "MP3 320kbps", size: "45 MB", type: "audio", id: "a1" },
            { quality: "M4A 128kbps", size: "18 MB", type: "audio", id: "a2" },
          ]
        };
        setVideoInfo(mockData);
        setError(null);
      }
      setIsLoading(false);
    }, 2500);
  };

  const DownloadIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
      <polyline points="7 10 12 15 17 10"></polyline>
      <line x1="12" y1="15" x2="12" y2="3"></line>
    </svg>
  );

  const VideoIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="inline-block mr-2 align-middle">
        <polygon points="23 7 16 12 23 17 23 7"></polygon>
        <path d="M1 18V6a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2z"></path>
    </svg>
  );

  const AudioIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="inline-block mr-2 align-middle">
        <path d="M9 18V5l12-2v13"></path>
        <circle cx="6" cy="18" r="3"></circle>
        <circle cx="18" cy="16" r="3"></circle>
    </svg>
  );

  // Placeholder for status message, ideally handled globally
  const [statusMessage, setStatusMessage] = useState({ text: '', type: '' });
  useEffect(() => {
    if (statusMessage.text) {
      const timer = setTimeout(() => setStatusMessage({ text: '', type: '' }), 3000);
      return () => clearTimeout(timer);
    }
  }, [statusMessage]);

  const handleDownloadClick = (format) => {
    setStatusMessage({ text: `Simulating download for ${format.type}: ${format.quality}...`, type: 'success' });
    // Actual download logic would be here, e.g., calling an API endpoint
    // window.location.href = `/api/download?url=${youtubeUrl}&formatId=${format.id}`;
  };

  return (
    <div className="container mx-auto px-4 min-h-screen flex flex-col items-center text-text-primary">
      <Header 
        pageTitleMain="Tube" 
        pageTitleHighlight="Fetch" 
        pageSubtitle="Download YouTube videos and audio quickly and easily." 
        theme={theme} 
        toggleTheme={toggleTheme} 
      />
      <main className="w-full max-w-3xl">
        <section id="downloaderSection" className="bg-card p-6 md:p-8 rounded-lg shadow-lg mb-8">
          <UrlForm 
            url={youtubeUrl} 
            setUrl={setYoutubeUrl} 
            handleSubmit={handleFetchYouTubeInfo} 
            placeholder="Paste YouTube video URL here (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)" 
            buttonText="Fetch" 
            isLoading={isLoading} 
            buttonIconSvg={<DownloadIcon />}
          />
        </section>

        {isLoading && (
          <section id="loadingSection" className="my-8">
            <div className="bg-card p-8 rounded-lg shadow-md flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-border border-t-primary-accent rounded-full animate-spin"></div>
              <p className="text-text-secondary">Processing your link... Please wait.</p>
            </div>
          </section>
        )}

        {error && (
          <section id="errorSection" className="my-8 bg-card p-6 rounded-lg border border-error text-error text-center shadow-md">
            <p className="font-medium">{error}</p>
          </section>
        )}

        {videoInfo && !isLoading && (
          <section id="resultsSection" className="my-8 animate-fadeIn">
            <div className="video-info bg-card p-6 rounded-lg shadow-md mb-8 flex flex-col sm:flex-row items-center sm:items-start gap-6">
              <div className="video-thumbnail w-full sm:w-40 h-auto sm:h-[90px] bg-input-bg rounded-lg overflow-hidden flex-shrink-0">
                {videoInfo.thumbnailUrl ? 
                  <img src={videoInfo.thumbnailUrl} alt="Video Thumbnail" className="w-full h-full object-cover" /> :
                  <span className="flex items-center justify-center h-full text-text-secondary text-sm">Thumbnail</span>
                }
              </div>
              <div className="video-details text-center sm:text-left">
                <h3 className="text-xl font-semibold mb-1 text-text-primary">{videoInfo.title}</h3>
                <p className="text-sm text-text-secondary">Channel: {videoInfo.channel}</p>
                <p className="text-sm text-text-secondary">Duration: {videoInfo.duration}</p>
              </div>
            </div>

            <div className="formats-container grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="format-group bg-card p-6 rounded-lg shadow-md">
                <h4 className="text-lg font-semibold mb-4 pb-2 border-b border-border text-text-primary"><VideoIcon />Video Formats</h4>
                <ul className="space-y-3">
                  {videoInfo.videoFormats.map((format) => (
                    <li key={format.id} className="format-item flex flex-col sm:flex-row justify-between items-center py-3 border-b border-border last:border-b-0">
                      <div className="format-info text-sm mb-2 sm:mb-0">
                        <span className="quality font-medium text-text-primary block sm:inline">{format.quality}</span>
                        <span className="size text-xs text-text-secondary ml-0 sm:ml-2 block sm:inline">(Approx. {format.size})</span>
                      </div>
                      <button 
                        onClick={() => handleDownloadClick(format)}
                        className="btn-download bg-success text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-success-hover transition-colors duration-200 flex items-center gap-2 w-full sm:w-auto justify-center">
                        <DownloadIcon /> Download
                      </button>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="format-group bg-card p-6 rounded-lg shadow-md">
                <h4 className="text-lg font-semibold mb-4 pb-2 border-b border-border text-text-primary"><AudioIcon />Audio Formats</h4>
                <ul className="space-y-3">
                  {videoInfo.audioFormats.map((format) => (
                    <li key={format.id} className="format-item flex flex-col sm:flex-row justify-between items-center py-3 border-b border-border last:border-b-0">
                      <div className="format-info text-sm mb-2 sm:mb-0">
                        <span className="quality font-medium text-text-primary block sm:inline">{format.quality}</span>
                        <span className="size text-xs text-text-secondary ml-0 sm:ml-2 block sm:inline">(Approx. {format.size})</span>
                      </div>
                      <button 
                        onClick={() => handleDownloadClick(format)}
                        className="btn-download bg-success text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-success-hover transition-colors duration-200 flex items-center gap-2 w-full sm:w-auto justify-center">
                         <DownloadIcon /> Download
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
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

export default YouTubePage;
