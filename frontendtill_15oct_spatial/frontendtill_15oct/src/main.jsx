/** React entry point that mounts the application.
 * Edit this file when changing the root render setup.

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles/index.css';

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);

 */
/** React entry point that mounts the application.
 * Edit this file when changing the root render setup.
 */
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles/index.css';
import './styles/palette-overrides.css';

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);

