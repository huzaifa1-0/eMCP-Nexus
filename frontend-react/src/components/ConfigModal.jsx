import { showToast } from './AlertToast';

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
    } catch {
      showToast('Failed to copy', 'error');
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
              <div className="config-block-wrapper">
                <div className="config-block">{configText}</div>
                <button className="btn btn-primary btn-copy-floating" onClick={handleCopy}>
                  <i className="fas fa-copy"></i> Copy to Clipboard
                </button>
              </div>
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
