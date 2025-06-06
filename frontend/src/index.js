import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Assuming you have a basic index.css or will add one for global styles
import App from './App';
import { BrowserRouter } from 'react-router-dom';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
