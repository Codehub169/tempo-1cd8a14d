import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom'; // Removed unused useLocation
import YouTubePage from './pages/YouTubePage';
import InstagramPage from './pages/InstagramPage';
import './App.css'; // Main App styles, can be imported from index.css too

function App() {
  const [theme, setTheme] = useState(() => {
    const storedTheme = localStorage.getItem('theme');
    // Ensure theme is strictly 'light' or 'dark'
    if (storedTheme === 'light' || storedTheme === 'dark') {
      return storedTheme;
    }
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  });

  useEffect(() => {
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      if (metaThemeColor) {
        metaThemeColor.setAttribute('content', '#1A1A1A');
      }
    } else {
      document.documentElement.classList.remove('dark');
      if (metaThemeColor) {
        metaThemeColor.setAttribute('content', '#F8F9FA');
      }
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  // Optional: Add a simple CSS file for basic body/html styling if not covered by index.css or Tailwind's preflight
  // e.g., frontend/src/App.css or frontend/src/index.css:
  // body, html, #root {
  //   min-height: 100vh;
  // }
  // #root {
  //   display: flex;
  //   flex-direction: column;
  // }

  return (
    <Routes>
      <Route path="/" element={<YouTubePage theme={theme} toggleTheme={toggleTheme} />} />
      <Route path="/instagram" element={<InstagramPage theme={theme} toggleTheme={toggleTheme} />} />
    </Routes>
  );
}

export default App;
