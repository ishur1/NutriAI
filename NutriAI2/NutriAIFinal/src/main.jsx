import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';

// Mount the React app into the <div id="root"></div> in index.html.
createRoot(document.getElementById('root')).render(
  // StrictMode helps catch common React issues during development.
  <StrictMode>
    <App />
  </StrictMode>
);
