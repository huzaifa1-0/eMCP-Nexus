import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import AuthModal from '../components/AuthModal';
import AlertToast, { showToast } from '../components/AlertToast';
import MCPCard from '../components/MCPCard';
import ConfigModal from '../components/ConfigModal';
import ChatWidget from '../components/ChatWidget';
import { API_BASE_URL } from '../api/config';

export default function MarketplacePage() {
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const [tools, setTools] = useState([]);
  const [statusText, setStatusText] = useState('Loading...');
  const [resultsText, setResultsText] = useState('Loading...');
  const [searchQuery, setSearchQuery] = useState('');
  const [configTool, setConfigTool] = useState(null);
  const [authModal, setAuthModal] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (!isLoggedIn) {
      showToast('Please log in to access the marketplace', 'error');
      setTimeout(() => navigate('/'), 1500);
      return;
    }
    fetchTools();
    initVoice();
  }, [isLoggedIn, navigate]);

  async function fetchTools() {
    try {
      const res = await fetch(`${API_BASE_URL}/tools/`);
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      setTools(data);
      const label = data.length === 1 ? 'eMCP tool available' : 'eMCP tools available';
      setStatusText(`${data.length} ${label}`);
      setResultsText(`${data.length} ${label}`);
    } catch {
      setStatusText('System Offline');
      setResultsText('Failed to connect');
      setTools([]);
    }
  }

  async function performSearch() {
    const query = searchQuery.trim();
    if (!query) { fetchTools(); return; }

    setResultsText('AI is analyzing your request...');
    setTools([]);

    try {
      const res = await fetch(`${API_BASE_URL}/search/?query=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error('Search failed');
      const data = await res.json();
      const results = data.results;
      const label = results.length === 1 ? 'match found' : 'matches found';
      setResultsText(`${results.length} AI ${label}`);
      setTools(results);
    } catch {
      setResultsText('Search failed');
      showToast('Search failed. Please try again.', 'error');
    }
  }

  function initVoice() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SR();
      recognition.continuous = false;
      recognition.lang = 'en-US';
      recognition.interimResults = false;

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setSearchQuery(transcript);
        setTimeout(() => performSearch(), 100);
      };
      recognition.onend = () => setListening(false);
      recognition.onerror = () => setListening(false);
      recognitionRef.current = recognition;
    }
  }

  function toggleVoice() {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.start();
        setListening(true);
      } catch (e) { console.error(e); }
    }
  }

  return (
    <>
      <Navbar onSignIn={() => setAuthModal(true)} />
      <AlertToast />

      <div className="page-container" style={{ padding: '20px' }}>
        <div className="alert">
          <i className="fas fa-info-circle"></i>
          Discover and integrate Modular Compute Protocol tools into your applications
        </div>

        <div className="page-header">
          <div className="page-title">
            <i className="fas fa-store"></i> MCP Marketplace
          </div>
          <div className="status-badge">
            <i className="fas fa-check-circle"></i> {statusText}
          </div>
        </div>

        <div className="search-container">
          <div className="search-box">
            <div className="search-input-wrapper">
              <input
                type="text"
                className="search-input"
                placeholder={listening ? 'Listening...' : 'Search eMCPs, tools, or descriptions...'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyUp={(e) => e.key === 'Enter' && performSearch()}
              />
              {recognitionRef.current && (
                <button
                  className={`voice-btn ${listening ? 'listening' : ''}`}
                  onClick={toggleVoice}
                  title="Search by voice"
                >
                  <i className="fas fa-microphone"></i>
                </button>
              )}
            </div>
            <button className="search-btn" onClick={performSearch}>
              <i className="fas fa-search"></i> Search
            </button>
          </div>
          <div className="results-count">{resultsText}</div>
        </div>

        <div className="divider"></div>

        {tools.length === 0 && resultsText !== 'AI is analyzing your request...' ? (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: '#888' }}>
            <i className="fas fa-box-open" style={{ fontSize: '48px', marginBottom: '20px', color: '#4cc9f0', display: 'block' }}></i>
            <h3 style={{ fontSize: '22px', marginBottom: '10px', color: '#ccc' }}>No tools yet</h3>
            <p style={{ marginBottom: '20px' }}>The marketplace is empty. Be the first to publish a tool!</p>
          </div>
        ) : resultsText === 'AI is analyzing your request...' ? (
          <div className="page-loading">
            <div className="loading-spinner"></div>
            <p>AI is analyzing your request...</p>
          </div>
        ) : (
          <div className="mcp-grid">
            {tools.map((tool) => (
              <MCPCard key={tool.id} tool={tool} onCopyConfig={(t) => setConfigTool(t)} />
            ))}
          </div>
        )}
      </div>

      <Footer />
      <ChatWidget />
      {configTool && <ConfigModal tool={configTool} onClose={() => setConfigTool(null)} />}
      <AuthModal isOpen={authModal} onClose={() => setAuthModal(false)} />
    </>
  );
}
