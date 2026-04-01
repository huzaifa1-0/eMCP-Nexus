export default function MCPCard({ tool, onCopyConfig }) {
  const subTools = tool.tool_definitions || [];
  const hasUrl = !!tool.url;

  return (
    <div className="mcp-card">
      <div className="mcp-card-header">
        <div className="mcp-card-title">{tool.name}</div>
        <span className={`mcp-badge ${hasUrl ? 'live' : 'deploying'}`}>
          {hasUrl ? 'Live' : 'Deploying'}
        </span>
      </div>

      <div className="mcp-description">
        <strong>Description:</strong>
        <div className="line-clamp-3">{tool.description}</div>
      </div>

      {subTools.length > 0 ? (
        <div className="sub-tools-section">
          <div className="sub-tools-label">
            <i className="fas fa-wrench"></i> INCLUDED TOOLS ({subTools.length})
          </div>
          {subTools.slice(0, 3).map((t, i) => (
            <div key={i} className="sub-tool-item">
              <span className="sub-tool-name">{t.name}</span>
              <span className="sub-tool-cost">
                {tool.cost > 0 ? `$${tool.cost}` : 'Free'}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ margin: '14px 0', fontSize: '13px', color: '#555', fontStyle: 'italic' }}>
          No specific tools discovered yet.
        </p>
      )}

      <div style={{ marginTop: '16px' }}>
        <button
          className={`btn btn-secondary ${!hasUrl ? 'disabled' : ''}`}
          style={{
            width: '100%',
            justifyContent: 'center',
            opacity: hasUrl ? 1 : 0.5,
            cursor: hasUrl ? 'pointer' : 'not-allowed',
          }}
          onClick={() => hasUrl && onCopyConfig?.(tool)}
        >
          <i className="fas fa-copy"></i> Copy Config
        </button>
      </div>

      <div className="mcp-card-footer">
        <span><i className="far fa-clock"></i> Recent</span>
        <span className="mcp-cost">{tool.cost > 0 ? `${tool.cost} USDC` : 'Free'}</span>
      </div>
    </div>
  );
}
