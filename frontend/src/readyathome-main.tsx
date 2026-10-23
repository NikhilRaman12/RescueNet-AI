import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import ReadyAtHome from './readyathome';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('ReadyAtHome page is missing its root element.');
}

createRoot(rootElement).render(
  <StrictMode>
    <ReadyAtHome />
  </StrictMode>,
);
