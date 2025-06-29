/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        'brand-red': '#FF0000',
        'primary-accent': '#007BFF',
        'primary-accent-hover': '#0056b3',
        'success': '#28A745',
        'success-hover': '#218838', // Added
        'warning': '#FFC107',
        'error': '#DC3545',
        
        // Instagram Gradient Colors - Added
        'instagram-pink': '#d62976',
        'instagram-purple': '#962fbf',
        'instagram-yellow': '#feda75', 

        // Dark Mode Palette
        'dark-bg': '#1A1A1A',
        'dark-card': '#282828',
        'dark-border': '#444444',
        'dark-text-primary': '#E0E0E0',
        'dark-text-secondary': '#A0A0A0',
        'dark-input-bg': '#333333',
        'dark-input-border': '#444444',
        'dark-btn-disabled-bg': '#555555',
        'dark-nav-link-bg': '#2c2c2c',
        'dark-nav-link-bg-hover': '#383838',
        'dark-theme-switcher-bg': '#333333',
        'dark-theme-switcher-hover-bg': '#444444',
        
        // Light Mode Palette
        'light-bg': '#F8F9FA',
        'light-card': '#FFFFFF',
        'light-border': '#DEE2E6',
        'light-text-primary': '#212529',
        'light-text-secondary': '#6C757D',
        'light-input-bg': '#FFFFFF',
        'light-input-border': '#CED4DA',
        'light-btn-disabled-bg': '#ced4da',
        'light-nav-link-bg': '#e9ecef',
        'light-nav-link-bg-hover': '#d3d9df',
        'light-theme-switcher-bg': '#e9ecef',
        'light-theme-switcher-hover-bg': '#dee2e6',

        // Active Navigation Link Styles - Added
        'nav-link-active': '#007BFF', // Using primary-accent value
        'nav-link-active-color': '#FFFFFF', // White text on primary-accent background
        'border-nav-link-active': '#0056b3', // Using primary-accent-hover for border
      },
      fontFamily: {
        primary: ['Inter', 'sans-serif'],
        secondary: ['Roboto Slab', 'serif'],
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
      borderRadius: {
        DEFAULT: '8px',
        'md': '8px',
      }
    },
  },
  plugins: [],
};
