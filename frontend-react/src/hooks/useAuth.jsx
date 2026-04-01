import { useState, createContext, useContext } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('accessToken'));
  const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail'));

  const login = (accessToken, email) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('userEmail', email);
    setToken(accessToken);
    setUserEmail(email);
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userEmail');
    setToken(null);
    setUserEmail(null);
  };

  return (
    <AuthContext.Provider value={{ token, userEmail, isLoggedIn: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
