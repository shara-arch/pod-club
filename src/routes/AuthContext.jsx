import React, {createContext, useContext, useState, useEffect, useCallback} from 'react';

const AuthContext = createContext(null);
const API_URL = '/api';

function getToken() {
  try { return localStorage.getItem('access_token'); } catch { return null; }
}
function getRefreshToken() {
  try { return localStorage.getItem('refresh_token'); } catch { return null; }
}
function saveTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}
function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

async function apiRequest(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (res.status === 204) return null;
  const body = await res.json().catch(() => null);
  if (!res.ok) throw new Error(body?.error || `Request failed (${res.status})`);
  return body;
}

export default function AuthProvider({children}) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = getToken();
    if (!token) { setLoading(false); return; }
    try {
      const user = await apiRequest('/auth/me');
      setCurrentUser(user);
    } catch {
      clearTokens();
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadUser(); }, [loadUser]);

  const signup = async (email, password, display_name) => {
    const data = await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, display_name }),
    });
    // Auto-login after register
    const loginData = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    saveTokens(loginData.access_token, loginData.refresh_token);
    setCurrentUser(loginData.user);
  };

  const login = async (email, password) => {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    saveTokens(data.access_token, data.refresh_token);
    setCurrentUser(data.user);
  };

  const adminLogin = async (email, password) => {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (data.user.role !== 'admin') {
      clearTokens();
      throw new Error('This account does not have admin privileges.');
    }
    saveTokens(data.access_token, data.refresh_token);
    setCurrentUser(data.user);
  };

  const logout = async () => {
    try { await apiRequest('/auth/logout', { method: 'POST' }); } catch {}
    clearTokens();
    setCurrentUser(null);
  };

  const updateProfile = async (updates) => {
    const data = await apiRequest('/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
    setCurrentUser(data);
  };

  return (
    <AuthContext.Provider value={{ currentUser, signup, login, adminLogin, logout, updateProfile, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
