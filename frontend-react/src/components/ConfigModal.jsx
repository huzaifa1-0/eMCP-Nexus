import { useState } from 'react';
import { showToast } from './AlertToast';
import { API_BASE_URL } from '../api/config';

export default function ConfigModal({ tool, onClose }) {
  if (!tool) return null;

  const proxyUrl = `${window.location.origin}/api/proxy/${tool.id}/sse`;
  const config = {
    mcpServers: {
      [tool.name.toLowerCase().replace(/\s+/g, '-')]: {
        url: proxyUrl,
        transport: 'sse',
      },
    },
  };
  const configText = JSON.stringify(config, null, 2);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(configText);
      showToast('Configuration copied!', 'success');
      onClose();
    } catch {
      showToast('Failed to copy', 'error');
    }
  };

  return (
    <div className="config-modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="config-modal">
        <div className="config-modal-header">
          <div className="config-modal-title">Use with Claude Desktop</div>
          <button className="close-config-btn" onClick={onClose}>&times;</button>
        </div>
        <p style={{ color: '#999', fontSize: '14px', marginBottom: '14px' }}>
          Add this configuration to your <code style={{ color: '#4cc9f0' }}>claude_desktop_config.json</code> file to use this tool.
        </p>
        <div className="config-block">{configText}</div>
        <div className="config-modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Close</button>
          <button className="btn btn-primary" onClick={handleCopy}>
            <i className="fas fa-copy"></i> Copy to Clipboard
          </button>
        </div>
      </div>
    </div>
  );
}
