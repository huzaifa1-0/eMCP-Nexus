import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api/config';

export default function ConnectionStatus() {
  const [status, setStatus] = useState('connecting');
  const [message, setMessage] = useState('Checking connection...');
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    checkConnection();
  }, []);

  async function checkConnection() {
    setStatus('connecting');
    setMessage('Checking backend connection...');
    setHidden(false);

    try {
      let res;
      try {
        res = await fetch(`${API_BASE_URL}/health`);
      } catch {
        res = await fetch(`${API_BASE_URL}`);
      }

      if (res.ok) {
        setStatus('connected');
        setMessage('Connected to backend');
        setTimeout(() => setHidden(true), 3000);
      } else {
        throw new Error(`Server returned ${res.status}`);
      }
    } catch (err) {
      setStatus('disconnected');
      setMessage(`Connection error`);
    }
  }

  if (hidden) return null;

  return (
    <div className={`connection-status ${status}`}>
      {status === 'connecting' ? (
        <div className="connection-spinner" />
      ) : (
        <i className={`fas fa-${status === 'connected' ? 'check-circle' : 'exclamation-circle'}`} />
      )}
      <span>{message}</span>
    </div>
  );
}
