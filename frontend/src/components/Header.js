import React from 'react';
import { NavLink } from 'react-router-dom';

const Header = ({ pageTitleMain, pageTitleHighlight, pageSubtitle, theme, toggleTheme, isInstagramPage = false }) => {
  const SunIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"></circle>
      <line x1="12" y1="1" x2="12" y2="3"></line>
      <line x1="12" y1="21" x2="12" y2="23"></line>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
      <line x1="1" y1="12" x2="3" y2="12"></line>
      <line x1="21" y1="12" x2="23" y2="12"></line>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
    </svg>
  );

  const MoonIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
    </svg>
  );

  const titleHighlightClass = isInstagramPage 
    ? "bg-clip-text text-transparent bg-gradient-to-r from-instagram-pink via-instagram-purple to-instagram-yellow"
    : "text-brand-red";

  return (
    <header className="w-full max-w-3xl py-6 md:py-8 mb-6 md:mb-8">
      <div className="header-content flex flex-col sm:flex-row justify-between items-center sm:items-start gap-4 mb-6">
        <div className="site-title-group text-center sm:text-left flex-grow">
          <h1 className="font-secondary text-3xl md:text-4xl font-bold mb-1">
            {pageTitleMain}<span className={titleHighlightClass}>{pageTitleHighlight}</span>
          </h1>
          <p className="subtitle text-sm md:text-base text-light-text-secondary dark:text-dark-text-secondary">
            {pageSubtitle}
          </p>
        </div>
        <button 
          onClick={toggleTheme} 
          className="theme-switcher bg-light-theme-switcher-bg dark:bg-dark-theme-switcher-bg text-light-text-primary dark:text-dark-text-primary border border-light-border dark:border-dark-border rounded-full w-10 h-10 flex items-center justify-center text-xl hover:bg-light-theme-switcher-hover-bg dark:hover:bg-dark-theme-switcher-hover-bg transition-colors duration-200 flex-shrink-0"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
        </button>
      </div>
      <nav className="main-navigation flex flex-col sm:flex-row justify-center items-center gap-2 sm:gap-3 p-2 bg-light-card dark:bg-dark-card sm:bg-transparent rounded-lg sm:rounded-none shadow-sm sm:shadow-none">
        <NavLink 
          to="/" 
          className={({ isActive }) => 
            `nav-link py-2 px-4 rounded-md font-medium text-sm transition-colors duration-200 w-full sm:w-auto text-center 
            ${isActive 
              ? 'bg-nav-link-active text-nav-link-active-color border border-nav-link-active'
              : 'bg-light-nav-link-bg dark:bg-dark-nav-link-bg text-light-text-primary dark:text-dark-text-primary hover:bg-light-nav-link-bg-hover dark:hover:bg-dark-nav-link-bg-hover border border-light-border dark:border-dark-border'}`
          }
        >
          YouTube Downloader
        </NavLink>
        <NavLink 
          to="/instagram" 
          className={({ isActive }) => 
            `nav-link py-2 px-4 rounded-md font-medium text-sm transition-colors duration-200 w-full sm:w-auto text-center 
            ${isActive 
              ? 'bg-nav-link-active text-nav-link-active-color border border-nav-link-active'
              : 'bg-light-nav-link-bg dark:bg-dark-nav-link-bg text-light-text-primary dark:text-dark-text-primary hover:bg-light-nav-link-bg-hover dark:hover:bg-dark-nav-link-bg-hover border border-light-border dark:border-dark-border'}`
          }
        >
          Instagram Reels
        </NavLink>
      </nav>
    </header>
  );
};

export default Header;
