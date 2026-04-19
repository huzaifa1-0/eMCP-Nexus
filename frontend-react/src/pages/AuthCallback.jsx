import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { showToast } from '../components/AlertToast';

export default function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get('token');
    const email = params.get('email');
    const error = params.get('error');

    console.log("Auth Callback Params:", { hasToken: !!token, email, error });

    if (error) {
      console.error("Auth Error from Backend:", error);
      showToast(error, 'error');
      navigate('/');
      return;
    }

    if (token && email) {
      console.log("Login successful, saving credentials...");
      login(token, email);
      showToast('Successfully logged in with GitHub!', 'success');
      navigate('/marketplace');
    } else {
      console.error("Missing token or email in URL");
      showToast('Authentication failed. No token received.', 'error');
      navigate('/');
    }
  }, [location, login, navigate]);

  return (
    <div className="callback-container" style={{ 
      display: 'flex', 
      flexDirection: 'column',
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      background: 'linear-gradient(to bottom, #000, #001f3f)',
      color: '#fff'
    }}>
      <div className="loader" style={{
        width: '50px',
        height: '50px',
        border: '5px solid rgba(76, 201, 240, 0.2)',
        borderTop: '5px solid #4cc9f0',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        marginBottom: '20px'
      }}></div>
      <p style={{ fontSize: '18px', fontWeight: '500', letterSpacing: '1px' }}>Completing login...</p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
