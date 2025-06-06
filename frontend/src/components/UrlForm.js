import React from 'react';

const UrlForm = ({ url, setUrl, handleSubmit, placeholder, buttonText, isLoading, buttonIconSvg }) => {
  const SpinnerIcon = () => (
    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
  );

  const internalHandleSubmit = (e) => {
    e.preventDefault();
    handleSubmit();
  };

  return (
    <form onSubmit={internalHandleSubmit} className="input-group flex flex-col sm:flex-row gap-4">
      <input 
        type="url" 
        value={url} 
        onChange={(e) => setUrl(e.target.value)} 
        className="url-input flex-grow w-full appearance-none bg-input-bg text-text-primary border border-input-border rounded-lg py-3 px-4 text-base leading-tight focus:outline-none focus:border-primary-accent focus:shadow-outline-blue transition-colors duration-200 placeholder-text-secondary" 
        placeholder={placeholder} 
        disabled={isLoading}
        required
      />
      <button 
        type="submit" 
        className={`btn btn-primary bg-primary-accent text-white font-semibold py-3 px-6 rounded-lg hover:bg-primary-accent-hover focus:outline-none focus:shadow-outline-blue active:bg-primary-accent-hover transition-all duration-200 ease-in-out flex items-center justify-center gap-2 min-w-[150px] 
                    ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
        disabled={isLoading}
      >
        {isLoading ? <SpinnerIcon /> : buttonIconSvg}
        {isLoading ? 'Processing...' : buttonText}
      </button>
    </form>
  );
};

export default UrlForm;
