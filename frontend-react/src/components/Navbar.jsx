import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { showToast } from './AlertToast';

export default function Navbar({ onSignIn }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const { isLoggedIn, userEmail, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <Link to={isLoggedIn ? "/marketplace" : "/"} className="logo">
        ⚡ <span>eMCP</span> Nexus
      </Link>

      <button className="hamburger" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>

      <ul className={`nav-links ${menuOpen ? 'open' : ''}`}>
        {!isLoggedIn && (
          <li>
            <Link to="/" className={isActive('/')} onClick={() => setMenuOpen(false)}>Home</Link>
          </li>
        )}
        
        <li>
          <Link 
            to="/marketplace" 
            className={isActive('/marketplace')} 
            onClick={(e) => {
              if (!isLoggedIn) {
                e.preventDefault();
                setMenuOpen(false);
                showToast('Please sign in to access the Marketplace', 'info');
                if (onSignIn) onSignIn();
              } else {
                setMenuOpen(false);
              }
            }}
          >
            Marketplace
          </Link>
        </li>

        {isLoggedIn && (
          <>
            <li>
              <Link to="/dashboard" className={isActive('/dashboard')} onClick={() => setMenuOpen(false)}>
                Dashboard
              </Link>
            </li>
            <li>
              <Link to="/create" className={isActive('/create')} onClick={() => setMenuOpen(false)}>
                Create MCP
              </Link>
            </li>
            
            {/* Mobile-only profile links */}
            <li className="mobile-only-profile">
              <div className="mobile-profile-header">
                <div className="avatar-circle small">{userEmail?.charAt(0).toUpperCase()}</div>
                <span>{userEmail}</span>
              </div>
              <div className="mobile-profile-actions">
                <Link to="/profile" className="mobile-nav-item" onClick={() => setMenuOpen(false)}>
                  <i className="fas fa-user"></i> Profile
                </Link>
                <button className="mobile-nav-item logout" onClick={() => { logout(); setMenuOpen(false); }}>
                  <i className="fas fa-sign-out-alt"></i> Logout
                </button>
              </div>
            </li>

            {/* Desktop-only profile dropdown */}
            <li className="desktop-only">
              <div className="profile-dropdown-container">
                <button 
                  className="profile-trigger" 
                  onClick={() => setProfileOpen(!profileOpen)}
                  title={userEmail}
                >
                  <div className="avatar-circle">
                    {userEmail?.charAt(0).toUpperCase()}
                  </div>
                  <i className={`fas fa-chevron-down ${profileOpen ? 'rotate' : ''}`}></i>
                </button>
                
                {profileOpen && (
                  <div className="profile-dropdown">
                    <div className="dropdown-header">
                      <p className="user-email">{userEmail}</p>
                    </div>
                    <Link to="/profile" className="dropdown-item" onClick={() => setProfileOpen(false)}>
                      <i className="fas fa-user"></i> My Profile
                    </Link>
                    <button className="dropdown-item logout" onClick={() => { logout(); setProfileOpen(false); }}>
                      <i className="fas fa-sign-out-alt"></i> Logout
                    </button>
                  </div>
                )}
              </div>
            </li>
          </>
        )}

        {!isLoggedIn && (
          <li>
            <button className="nav-auth-btn" onClick={() => { onSignIn?.(); setMenuOpen(false); }}>
              Sign In
            </button>
          </li>
        )}
      </ul>
    </nav>
  );
}
