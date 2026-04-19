import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL, fetchWithTimeout } from '../api/config';
import { showToast } from '../components/AlertToast';

export default function ProfilePage() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const res = await fetchWithTimeout(`${API_BASE_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setUser(data);
    } catch (err) {
      showToast('Failed to load profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setPasswords({ ...passwords, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (passwords.new !== passwords.confirm) {
      showToast('New passwords do not match', 'error');
      return;
    }
    if (passwords.new.length < 6) {
      showToast('Password must be at least 6 characters', 'error');
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('accessToken');
      await fetchWithTimeout(`${API_BASE_URL}/auth/change-password`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: passwords.current,
          new_password: passwords.new
        }),
      });
      showToast('Password updated successfully!', 'success');
      setPasswords({ current: '', new: '', confirm: '' });
    } catch (err) {
      showToast(err.message || 'Failed to update password', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading-spinner">Loading...</div>;

  return (
    <div className="profile-container">
      <div className="profile-card">
        <Link to="/marketplace" className="back-link">
          <i className="fas fa-arrow-left"></i> Back to Marketplace
        </Link>
        <div className="profile-header">
          <div className="profile-avatar">
            <i className="fas fa-user-circle"></i>
          </div>
          <h1>My Profile</h1>
          <p>Manage your account settings and security</p>
        </div>

        <div className="profile-section">
          <h2>Account Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Username</label>
              <div className="info-value">{user?.username}</div>
            </div>
            <div className="info-item">
              <label>Email Address</label>
              <div className="info-value">{user?.email}</div>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>Security</h2>
          <form onSubmit={handleSubmit} className="password-form">
            <div className="form-group">
              <label>Current Password</label>
              <div className="input-with-icon">
                <i className="fas fa-lock"></i>
                <input 
                  type="password" 
                  name="current" 
                  value={passwords.current}
                  onChange={handleChange}
                  placeholder="Enter current password" 
                  required 
                />
              </div>
            </div>
            <div className="form-group">
              <label>New Password</label>
              <div className="input-with-icon">
                <i className="fas fa-key"></i>
                <input 
                  type="password" 
                  name="new" 
                  value={passwords.new}
                  onChange={handleChange}
                  placeholder="Enter new password" 
                  required 
                />
              </div>
            </div>
            <div className="form-group">
              <label>Confirm New Password</label>
              <div className="input-with-icon">
                <i className="fas fa-check-double"></i>
                <input 
                  type="password" 
                  name="confirm" 
                  value={passwords.confirm}
                  onChange={handleChange}
                  placeholder="Confirm new password" 
                  required 
                />
              </div>
            </div>
            <button type="submit" className="save-btn" disabled={submitting}>
              {submitting ? 'UPDATING...' : 'Update Password'}
            </button>
          </form>
        </div>
      </div>

      <style>{`
        .profile-container {
          min-height: 100vh;
          padding: 100px 20px 50px;
          display: flex;
          justify-content: center;
          background: radial-gradient(circle at top right, #001f3f, #000);
        }
        .profile-card {
          width: 100%;
          max-width: 600px;
          background: rgba(255, 255, 255, 0.03);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 24px;
          padding: 40px;
          color: white;
          box-shadow: 0 20px 50px rgba(0,0,0,0.5);
          position: relative;
        }
        .back-link {
          position: absolute;
          top: 25px;
          left: 25px;
          color: #888;
          font-size: 13px;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: all 0.3s;
        }
        .back-link:hover {
          color: #4cc9f0;
          transform: translateX(-5px);
        }
        .profile-header {
          text-align: center;
          margin-bottom: 40px;
        }
        .profile-avatar {
          font-size: 64px;
          color: #4cc9f0;
          margin-bottom: 15px;
          filter: drop-shadow(0 0 10px rgba(76, 201, 240, 0.5));
        }
        .profile-header h1 {
          font-size: 28px;
          margin-bottom: 8px;
          letter-spacing: 1px;
        }
        .profile-header p {
          color: #aaa;
          font-size: 14px;
        }
        .profile-section {
          margin-bottom: 35px;
        }
        .profile-section h2 {
          font-size: 18px;
          margin-bottom: 20px;
          padding-bottom: 10px;
          border-bottom: 1px solid rgba(255,255,255,0.1);
          color: #4cc9f0;
        }
        .info-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }
        .info-item label {
          display: block;
          font-size: 12px;
          color: #888;
          margin-bottom: 5px;
          text-transform: uppercase;
        }
        .info-value {
          font-size: 16px;
          padding: 12px;
          background: rgba(255,255,255,0.05);
          border-radius: 12px;
          border: 1px solid rgba(255,255,255,0.05);
        }
        .form-group {
          margin-bottom: 20px;
        }
        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-size: 14px;
          color: #ccc;
        }
        .input-with-icon {
          position: relative;
        }
        .input-with-icon i {
          position: absolute;
          left: 15px;
          top: 50%;
          transform: translateY(-50%);
          color: #4cc9f0;
          font-size: 16px;
        }
        .input-with-icon input {
          width: 100%;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 12px;
          padding: 12px 12px 12px 45px;
          color: white;
          font-size: 15px;
          transition: 0.3s;
        }
        .input-with-icon input:focus {
          outline: none;
          border-color: #4cc9f0;
          background: rgba(255,255,255,0.1);
          box-shadow: 0 0 15px rgba(76, 201, 240, 0.2);
        }
        .save-btn {
          width: 100%;
          background: linear-gradient(45deg, #4361ee, #4cc9f0);
          border: none;
          border-radius: 12px;
          padding: 14px;
          color: white;
          font-weight: 600;
          font-size: 16px;
          cursor: pointer;
          transition: 0.3s;
          margin-top: 10px;
          text-transform: uppercase;
          letter-spacing: 1px;
        }
        .save-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 20px rgba(76, 201, 240, 0.4);
        }
        .save-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        @media (max-width: 480px) {
          .info-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}
