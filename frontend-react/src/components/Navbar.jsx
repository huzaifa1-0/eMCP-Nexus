import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Navbar({ onSignIn }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const { isLoggedIn, userEmail, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <Link to="/" className="logo">
        ⚡ <span>eMCP</span> Nexus
      </Link>

      <button className="hamburger" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>

      <ul className={`nav-links ${menuOpen ? 'open' : ''}`}>
        <li><Link to="/" className={isActive('/')} onClick={() => setMenuOpen(false)}>Home</Link></li>
        <li><Link to="/marketplace" className={isActive('/marketplace')} onClick={() => setMenuOpen(false)}>Marketplace</Link></li>
        {isLoggedIn && (
          <>
            <li><Link to="/dashboard" className={isActive('/dashboard')} onClick={() => setMenuOpen(false)}>Dashboard</Link></li>
            <li><Link to="/create" className={isActive('/create')} onClick={() => setMenuOpen(false)}>Create eMCP</Link></li>
          </>
        )}
        <li>
          {isLoggedIn ? (
            <button className="nav-auth-btn" onClick={() => { logout(); setMenuOpen(false); }}>
              Logout
            </button>
          ) : (
            <button className="nav-auth-btn" onClick={() => { onSignIn?.(); setMenuOpen(false); }}>
              Sign In
            </button>
          )}
        </li>
      </ul>
    </nav>
  );
}
