import { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';

let toastId = 0;
let listeners = [];
let toasts = [];

function notifyListeners() {
  listeners.forEach(fn => fn([...toasts]));
}

export function showToast(message, type = 'info', duration = 4000) {
  const id = ++toastId;
  toasts = [...toasts, { id, message, type, exiting: false }];
  notifyListeners();

  setTimeout(() => {
    toasts = toasts.map(t => t.id === id ? { ...t, exiting: true } : t);
    notifyListeners();
    setTimeout(() => {
      toasts = toasts.filter(t => t.id !== id);
      notifyListeners();
    }, 400);
  }, duration);
}

export default function AlertToast() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    listeners.push(setItems);
    return () => { listeners = listeners.filter(fn => fn !== setItems); };
  }, []);

  if (items.length === 0) return null;

  return createPortal(
    <div className="toast-container">
      {items.map(t => (
        <div key={t.id} className={`toast ${t.type} ${t.exiting ? 'exiting' : ''}`}>
          <i className={`fas fa-${t.type === 'error' ? 'exclamation-triangle' : t.type === 'success' ? 'check-circle' : 'info-circle'}`}
             style={{ color: t.type === 'error' ? '#ff4d4d' : t.type === 'success' ? '#2ecc71' : '#4cc9f0' }} />
          <span>{t.message}</span>
        </div>
      ))}
    </div>,
    document.body
  );
}
