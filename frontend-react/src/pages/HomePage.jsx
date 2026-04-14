import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import AuthModal from '../components/AuthModal';
import AlertToast from '../components/AlertToast';
import { API_BASE_URL } from '../api/config';

export default function HomePage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [stats, setStats] = useState({ users: '...', tools: '...', uptime: '99.9%' });
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isLoggedIn) {
      navigate('/marketplace');
    }
    fetchStats();
  }, [isLoggedIn, navigate]);

  async function fetchStats() {
    try {
      const res = await fetch(`${API_BASE_URL}/stats`);
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      setStats({
        users: data.active_users ?? 0,
        tools: data.mcp_tools ?? 0,
        uptime: data.uptime || '99.9%',
      });
    } catch {
      setStats({ users: '100+', tools: '50+', uptime: '99.9%' });
    }
  }

  return (
    <>
      <Navbar onSignIn={() => setModalOpen(true)} />
      <AlertToast />

      <section className="hero">
        <div className="web3-badge">⭐ Web3-Enabled Platform</div>
        <h1>Model Context Protocol</h1>
        <p>
          Create, manage, and deploy MCP tools with blockchain-powered authentication.
          Experience the future of modular computing with Web3 wallet integration.
        </p>

        <div className="stats">
          <div className="stat">
            <h2>{stats.users}</h2>
            <p>Active Users</p>
          </div>
          <div className="stat">
            <h2>{stats.tools}</h2>
            <p>MCP Tools</p>
          </div>
          <div className="stat">
            <h2>{stats.uptime}</h2>
            <p>Uptime</p>
          </div>
        </div>
      </section>

      <section className="get-started">
        <h2>Get Started</h2>
        <p>Sign in with your Web3 wallet or traditional account to access the platform.</p>
        <button className="sign-in-btn" onClick={() => setModalOpen(true)}>Sign In</button>
        <div className="options">
          <div className="option">Connect with MetaMask, WalletConnect, or other Web3 wallets</div>
          <div className="option">Blockchain-verified identity and secure authentication</div>
        </div>
      </section>

      <section className="features-section" id="features">
        <h2>Platform Features</h2>
        <p>Everything you need to create, manage, and deploy MCP tools with enterprise-grade security.</p>
        <div className="features">
          <div className="feature-card">
            <div className="icon">⚡</div>
            <h3>Lightning Fast</h3>
            <p>Deploy and manage MCP tools with instant configuration and real-time updates.</p>
          </div>
          <div className="feature-card">
            <div className="icon">🛡️</div>
            <h3>Secure by Design</h3>
            <p>End-to-end encryption with blockchain authentication and row-level security.</p>
          </div>
          <div className="feature-card">
            <div className="icon">👥</div>
            <h3>Collaborative</h3>
            <p>Share configurations, collaborate on tools, and build together with your team.</p>
          </div>
        </div>
      </section>

      <Footer />
      <AuthModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </>
  );
}
