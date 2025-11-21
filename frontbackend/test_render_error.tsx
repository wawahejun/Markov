import React from 'react';
import { createRoot } from 'react-dom/client';
import PrivacyDiscovery from './src/components/walrus/PrivacyDiscovery';

try {
  const container = document.getElementById('test');
  if (container) {
    const root = createRoot(container);
    root.render(<PrivacyDiscovery />);
  }
} catch (error) {
  console.error('Render error:', error);
}
