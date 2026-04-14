import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL, fetchWithTimeout } from '../api/config';
import { useAuth } from '../hooks/useAuth';

export default function AuthModal({ isOpen, onClose }) {
  const [activeForm, setActiveForm] = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  if (!isOpen) return null;

  const switchForm = (form) => {
    setActiveForm(form);
    setError('');
    setSuccess('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const form = e.target;
    const email = form.email.value;
    const password = form.password.value;

    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const res = await fetchWithTimeout(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      login(data.access_token, email);
      setSuccess('Login successful! Redirecting...');
      setTimeout(() => {
        onClose();
        navigate('/marketplace');
      }, 1200);
    } catch (err) {
      let msg = err.message;
      if (msg.includes('401') || msg.includes('Incorrect')) msg = 'Invalid email or password';
      else if (msg.includes('Network') || msg.includes('fetch')) msg = 'Cannot connect to server';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const form = e.target;
    const username = form.username.value;
    const email = form.email.value;
    const password = form.password.value;
    const confirm = form.confirm.value;

    if (!username || !email || !password) {
      setError('Please fill in all fields');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await fetchWithTimeout(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });
      setSuccess('Account created successfully!');
      setTimeout(() => switchForm('login'), 1500);
    } catch (err) {
      let msg = err.message;
      if (msg.includes('already registered')) msg = 'Email already registered';
      else if (msg.includes('Network')) msg = 'Cannot connect to server';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setSuccess('');
    setError('');
    setSuccess('Reset instructions sent! Check your email.');
  };

  const handleGithubLogin = () => {
    // Redirect to backend OAuth route
    window.location.href = `${API_BASE_URL}/auth/github/login`;
  };

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-content">
        <button className="close-modal" onClick={onClose}>&times;</button>

        {/* LOGIN */}
        {activeForm === 'login' && (
          <form onSubmit={handleLogin}>
            <div className="auth-header">
              <div className="modal-logo"><i className="fas fa-dna"></i></div>
              <h1>Login</h1>
              <p>Access your eMCP Nexus account to continue</p>
            </div>

            <div className="form-group">
              <label>Email</label>
              <div className="input-with-icon">
                <i className="fas fa-envelope"></i>
                <input type="email" name="email" className="form-control" placeholder="Enter your email" required />
              </div>
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="input-with-icon">
                <i className="fas fa-lock"></i>
                <input type="password" name="password" className="form-control" placeholder="Enter your password" required />
              </div>
            </div>

            <div className="additional-options">
              <label className="remember-me">
                <input type="checkbox" /> Remember me
              </label>
              <button type="button" className="forgot-password" onClick={() => switchForm('forgot')}>
                Forgot password?
              </button>
            </div>

            <button type="submit" className="auth-btn" disabled={loading}>
              {loading ? 'LOGGING IN...' : 'Log In'}
            </button>

            <div className="auth-divider">Sign in with</div>

            <div className="social-auth-icons">
              <button type="button" className="social-icon-btn github" title="Login with GitHub" onClick={handleGithubLogin}>
                <i className="fab fa-github"></i>
              </button>
            </div>

            {error && <div className="message error-message"><i className="fas fa-exclamation-circle"></i> {error}</div>}
            {success && <div className="message success-message"><i className="fas fa-check-circle"></i> {success}</div>}

            <div className="alternate-option">
              <button type="button" className="auth-link" onClick={() => switchForm('register')}>
                <i className="fas fa-user-plus"></i> Create account
              </button>
            </div>

            <div className="modal-footer-text">Powered by <span>eMCP Nexus</span></div>
          </form>
        )}

        {/* REGISTER */}
        {activeForm === 'register' && (
          <form onSubmit={handleRegister}>
            <div className="auth-header">
              <div className="modal-logo"><i className="fas fa-dna"></i></div>
              <h1>Create Account</h1>
              <p>Join the eMCP Nexus Community Today</p>
            </div>

            <div className="form-group">
              <label>Username</label>
              <div className="input-with-icon">
                <i className="fas fa-user"></i>
                <input type="text" name="username" className="form-control" placeholder="Choose a username" required />
              </div>
            </div>

            <div className="form-group">
              <label>Email Address</label>
              <div className="input-with-icon">
                <i className="fas fa-envelope"></i>
                <input type="email" name="email" className="form-control" placeholder="Enter your email" required />
              </div>
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="input-with-icon">
                <i className="fas fa-lock"></i>
                <input type="password" name="password" className="form-control" placeholder="Create a password" required />
              </div>
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <div className="input-with-icon">
                <i className="fas fa-lock"></i>
                <input type="password" name="confirm" className="form-control" placeholder="Confirm your password" required />
              </div>
            </div>

            <button type="submit" className="auth-btn" disabled={loading}>
              {loading ? 'CREATING ACCOUNT...' : 'Create Account'}
            </button>

            <div className="auth-divider">Sign up with</div>

            <div className="social-auth-icons">
              <button type="button" className="social-icon-btn github" title="Login with GitHub" onClick={handleGithubLogin}>
                <i className="fab fa-github"></i>
              </button>
            </div>

            {error && <div className="message error-message"><i className="fas fa-exclamation-circle"></i> {error}</div>}
            {success && <div className="message success-message"><i className="fas fa-check-circle"></i> {success}</div>}

            <div className="alternate-option">
              <button type="button" className="back-to-login" onClick={() => switchForm('login')}>
                <i className="fas fa-arrow-left"></i> Back to login
              </button>
            </div>
          </form>
        )}

        {/* FORGOT PASSWORD */}
        {activeForm === 'forgot' && (
          <form onSubmit={handleForgotPassword}>
            <div className="auth-header">
              <div className="modal-logo"><i className="fas fa-dna"></i></div>
              <h1>Reset Password</h1>
              <p>Enter your email to reset your password</p>
            </div>

            <div className="form-group">
              <label>Email Address</label>
              <div className="input-with-icon">
                <i className="fas fa-envelope"></i>
                <input type="email" name="email" className="form-control" placeholder="Enter your email" required />
              </div>
            </div>

            <button type="submit" className="auth-btn">Send Reset Link</button>

            {success && <div className="message success-message"><i className="fas fa-check-circle"></i> {success}</div>}

            <div className="alternate-option">
              <button type="button" className="back-to-login" onClick={() => switchForm('login')}>
                <i className="fas fa-arrow-left"></i> Back to login
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
