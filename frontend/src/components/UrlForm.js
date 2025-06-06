import React from 'react';

const UrlForm = ({ url, setUrl, handleSubmit, placeholder, buttonText, isLoading, buttonIconSvg }) => {
  const SpinnerIcon = () => (
    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
  );

  const internalHandleSubmit = (e) => {
    e.preventDefault();
    if (!isLoading) {
      handleSubmit();
    }
  };

  return (
    <form onSubmit={internalHandleSubmit} className="input-group flex flex-col sm:flex-row gap-3 sm:gap-4">
      <input 
        type="url" 
        value={url} 
        onChange={(e) => setUrl(e.target.value)} 
        className="url-input flex-grow w-full appearance-none bg-light-input-bg dark:bg-dark-input-bg text-light-text-primary dark:text-dark-text-primary border border-light-input-border dark:border-dark-input-border rounded-lg py-3 px-4 text-base leading-tight focus:outline-none focus:border-primary-accent focus:ring-1 focus:ring-primary-accent transition-colors duration-200 placeholder:text-light-text-secondary dark:placeholder:text-dark-text-secondary"
        placeholder={placeholder} 
        disabled={isLoading}
        required
      />
      <button 
        type="submit" 
        className={`btn btn-primary bg-primary-accent text-white font-semibold py-3 px-6 rounded-lg hover:bg-primary-accent-hover focus:outline-none focus:ring-2 focus:ring-primary-accent focus:ring-opacity-50 active:bg-primary-accent-hover transition-all duration-200 ease-in-out flex items-center justify-center gap-2 min-w-[150px] sm:min-w-[160px] 
                    ${isLoading ? 'opacity-70 cursor-not-allowed' : 'hover:shadow-md'}`}
        disabled={isLoading}
      >
        {isLoading ? <SpinnerIcon /> : buttonIconSvg}
        <span className="ml-2">{isLoading ? 'Processing...' : buttonText}</span>
      </button>
    </form>
  );
};

export default UrlForm;
