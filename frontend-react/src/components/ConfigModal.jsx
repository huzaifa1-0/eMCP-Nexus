import { showToast } from './AlertToast';

import { useState } from 'react';
import { createWalletClient, custom, parseEther } from 'viem';
import { baseSepolia } from 'viem/chains';
import { useAuth } from '../hooks/useAuth';
import { API_BASE_URL } from '../api/config';

export default function ConfigModal({ tool, onClose }) {
  const { token, isLoggedIn } = useAuth();
  const [apiKey, setApiKey] = useState(null);
  const [isUnlocking, setIsUnlocking] = useState(false);
  
  if (!tool) return null;

  // If tool is paid and not unlocked yet, we hide the config URL
  const isPaidTool = tool.cost > 0;
  const showConfig = !isPaidTool || apiKey;

  const proxyUrl = `${window.location.origin}/api/proxy/${tool.id}/sse${apiKey ? `?api_key=${apiKey}` : ''}`;
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
    } catch {
      showToast('Failed to copy', 'error');
    }
  };

  const handleUnlock = async () => {
    if (!isLoggedIn) {
      showToast('Please log in first to unlock tools.', 'error');
      return;
    }
    
    if (!window.ethereum) {
      showToast('No Web3 wallet found. Please install MetaMask.', 'error');
      return;
    }

    setIsUnlocking(true);
    try {
      // 1. Connect Wallet
      const walletClient = createWalletClient({
        chain: baseSepolia,
        transport: custom(window.ethereum)
      });
      
      const [address] = await walletClient.requestAddresses();
      
      // 2. Send Payment Transaction
      showToast('Please confirm the transaction in your wallet...', 'info');
      const hash = await walletClient.sendTransaction({
        account: address,
        // Using a dummy receiver address for this prototype as per settings
        to: '0x0000000000000000000000000000000000000000', 
        value: parseEther(tool.cost.toString()),
      });
      
      showToast('Transaction sent! Verifying payment...', 'info');
      
      // 3. Verify Payment with Backend
      const res = await fetch(`${API_BASE_URL}/web3/unlock`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tool_id: tool.id,
          tx_hash: hash
        })
      });
      
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to unlock tool');
      }
      
      const data = await res.json();
      setApiKey(data.api_key);
      showToast('Tool unlocked successfully!', 'success');
      
    } catch (error) {
      console.error(error);
      showToast(error.message || 'Payment failed', 'error');
    } finally {
      setIsUnlocking(false);
    }
  };

  const reviews = tool.reviews || [];
  const averageRating = reviews.length > 0 
    ? (reviews.reduce((acc, r) => acc + r.rating, 0) / reviews.length).toFixed(1)
    : '0.0';

  return (
    <div className="config-modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="config-modal">
        <div className="config-modal-header">
          <div className="config-modal-title">{tool.name} — Full Details</div>
          <button className="close-config-btn" onClick={onClose}>&times;</button>
        </div>

        <div className="config-modal-scroll-area">
          {/* Enhanced Author Section */}
          <div className="modal-section author-hero">
            <div className="author-avatar-large">{tool.author?.charAt(0) || 'U'}</div>
            <div className="author-meta">
              <div className="author-label">CREATED BY</div>
              <div className="author-name-highlight">{tool.author || 'Anonymous'}</div>
              <div className="tool-stats">
                <span><i className="fas fa-layer-group"></i> {tool.author_tools_count || 1} {tool.author_tools_count === 1 ? 'Tool' : 'Tools'}</span>
                <span><i className="fas fa-check-circle"></i> Verified Creator</span>
              </div>
            </div>
          </div>

          <div className="modal-grid-layout">
            {/* Left Column: Configuration */}
            <div className="modal-column">
              <h3 className="section-title"><i className="fas fa-code"></i> JSON Configuration</h3>
              <p className="section-subtitle">Copy this into your Claude config file.</p>
              
              {showConfig ? (
                <div className="config-block-wrapper">
                  <div className="config-block">{configText}</div>
                  <button className="btn btn-primary btn-copy-floating" onClick={handleCopy}>
                    <i className="fas fa-copy"></i> Copy to Clipboard
                  </button>
                </div>
              ) : (
                <div className="config-block-wrapper" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '30px 20px', background: 'rgba(0,0,0,0.4)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <i className="fas fa-lock" style={{ fontSize: '32px', color: '#ffb703', marginBottom: '15px' }}></i>
                  <h4 style={{ color: '#fff', marginBottom: '10px' }}>Premium Tool</h4>
                  <p style={{ color: '#aaa', textAlign: 'center', marginBottom: '20px', fontSize: '14px' }}>
                    This tool requires a one-time Web3 payment to unlock its configuration.
                  </p>
                  <button 
                    className="btn btn-primary" 
                    onClick={handleUnlock} 
                    disabled={isUnlocking}
                    style={{ width: '100%', padding: '12px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px' }}
                  >
                    {isUnlocking ? (
                      <><i className="fas fa-circle-notch fa-spin"></i> Processing...</>
                    ) : (
                      <>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                        </svg>
                        Pay {tool.cost} ETH to Unlock
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Right Column: Instructions */}
            <div className="modal-column">
              <h3 className="section-title"><i className="fas fa-magic"></i> Setup Guide</h3>
              <p className="section-subtitle">Get started in seconds.</p>
              
              <div className="guide-steps-container">
                <div className="guide-step">
                  <div className="step-number">1</div>
                  <div className="step-text-small">
                    <strong>Locate Config</strong>
                    <p>Open <code>claude_desktop_config.json</code> in your AppData folder.</p>
                  </div>
                </div>

                <div className="guide-step">
                  <div className="step-number">2</div>
                  <div className="step-text-small">
                    <strong>Copy & Paste</strong>
                    <p>Copy the JSON block from the left and paste it under <code>mcpServers</code>.</p>
                  </div>
                </div>

                <div className="guide-step">
                  <div className="step-number">3</div>
                  <div className="step-text-small">
                    <strong>Restart</strong>
                    <p>Restart Claude to activate.</p>
                  </div>
                </div>
              </div>

              <div className="pro-tip-modern">
                <div className="pro-tip-icon"><i className="fas fa-lightbulb"></i></div>
                <div className="pro-tip-content">
                  <strong>Developer Tip</strong>
                  <p>Update Claude if tools don't appear.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="modal-divider"></div>

          {/* Reviews Section */}
          <div className="modal-section">
            <div className="reviews-header-row-horizontal">
              <h3 className="section-title" style={{ marginBottom: 0 }}><i className="fas fa-star"></i> User Reviews</h3>
              <div className="rating-summary-horizontal">
                <div className="rating-score">{averageRating}</div>
                <div className="rating-stars-inline">
                  {[...Array(5)].map((_, i) => (
                    <i key={i} className={`fas fa-star ${i < Math.floor(averageRating) ? 'active' : ''}`}></i>
                  ))}
                  <span className="review-count">({reviews.length} reviews)</span>
                </div>
              </div>
            </div>
            
            {reviews.length > 0 ? (
              <div className="reviews-grid-horizontal">
                {reviews.map((review, i) => (
                  <div key={i} className="review-card-modern">
                    <div className="review-card-header">
                      <div className="review-user-avatar-small">{review.user.charAt(0)}</div>
                      <div className="review-user-name-date">
                        <div className="review-username">{review.user}</div>
                        <div className="review-date">{new Date(review.timestamp).toLocaleDateString()}</div>
                      </div>
                      <div className="review-rating-stars-mini">
                        {[...Array(5)].map((_, j) => (
                          <i key={j} className={`fas fa-star ${j < review.rating ? 'active' : ''}`}></i>
                        ))}
                      </div>
                    </div>
                    <p className="review-card-comment">{review.comment || "No comment."}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-reviews-state">
                <i className="far fa-comment-dots"></i>
                <p>No reviews yet. Be the first to share!</p>
              </div>
            )}
          </div>
        </div>

        <div className="config-modal-footer">
          <button className="btn btn-secondary-outline" onClick={onClose}>Close Details</button>
        </div>
      </div>
    </div>
  );
}
