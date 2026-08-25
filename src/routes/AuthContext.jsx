import React, {createContext, useContext, useState, useEffect} from 'react';

// Create a Context object to hold and share authentication state across components
const AuthContext = createContext(null);
const ADMIN_ACCOUNT = { username: 'admin', password: 'podclub', email: 'admin@podclub.local', role: 'admin' };
export default function AuthProvider( {children}) {
    // Store currently authenticated user state(load from localStorage on initial render)
  const [currentUser, setCurrentUser] = useState(() => {
    return JSON.parse(localStorage.getItem('activeUser')) || null;
  })
    // Store mock database of registered users; load from localStorage on initial render
  const [users, setUsers] = useState(() => {
    try {
      const stored = JSON.parse(localStorage.getItem('usersDB')) || [];
      // Ensure a demo admin account exists in the users DB for convenience (frontend-only)
      const hasAdmin = stored.some((u) => u.username === ADMIN_ACCOUNT.username);
      if (!hasAdmin) {
        const withAdmin = [ { ...ADMIN_ACCOUNT, password: typeof window !== 'undefined' ? window.btoa(ADMIN_ACCOUNT.password) : Buffer.from(ADMIN_ACCOUNT.password).toString('base64') }, ...stored ];
        localStorage.setItem('usersDB', JSON.stringify(withAdmin));
        return withAdmin;
      }
      return stored;
    } catch (e) {
      return [ { ...ADMIN_ACCOUNT, password: typeof window !== 'undefined' ? window.btoa(ADMIN_ACCOUNT.password) : Buffer.from(ADMIN_ACCOUNT.password).toString('base64') } ];
    }
  })
    // Sync active user session to localStorage or remove it on logout/expiration
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('activeUser', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('activeUser');
    }
  }, [currentUser]);
  // Registers a new user if the username is unique and automatically logs them in
  // Very small client-side hash to avoid storing raw plain-text passwords (not production secure)
  const hashPassword = (pw) => {
    try {
      return typeof window !== 'undefined' ? window.btoa(pw) : Buffer.from(pw, 'utf-8').toString('base64');
    } catch (e) {
      return pw;
    }
  };

  const signup = (username, password, email) => {
    const userExists = users.some((u) => u.username === username);
    if (userExists) {
      throw new Error('Username already exists.');
    }
    const hashed = hashPassword(password);
    const newUser = { username, password: hashed, email: email || '', role: 'member' };
    const updated = [...users, newUser];
    setUsers(updated);
    localStorage.setItem('usersDB', JSON.stringify(updated));
    setCurrentUser({ username, email: email || '', role: 'member' }); // Log in user automatically after successful registration
  };
  // Validates credentials against stored users and updates current session state
  const login = (username, password) => {
    const user = users.find((u) => u.username === username);
    if (!user) {
      throw new Error('Username not found.');
    }
    const hashed = hashPassword(password);
    // Support legacy plain text entries by checking either
    if (user.password !== hashed && user.password !== password) {
      throw new Error('Incorrect password.');
    }
    setCurrentUser({ username, email: user.email || '', role: user.role || 'member' });
  };
  const adminLogin = (username, password) => {
    if (username !== ADMIN_ACCOUNT.username || password !== ADMIN_ACCOUNT.password) {
      throw new Error('Use the demo admin credentials: admin / podclub.');
    }
    setCurrentUser(ADMIN_ACCOUNT);
  };
  // Clears active user session to trigger logout across the app
  const logout = () => {
    setCurrentUser(null);
  }; 
  const updateProfile = ({ username, email }) => {
    const updatedUser = {
      ...currentUser,
      username: username?.trim() || currentUser.username,
      email: email?.trim() || '',
    };
    setCurrentUser(updatedUser);
    const updatedUsers = users.map((user) => user.username === currentUser.username ? { ...user, ...updatedUser } : user);
    setUsers(updatedUsers);
    localStorage.setItem('usersDB', JSON.stringify(updatedUsers));
  };
  return (
    // Expose authentication state and handler methods to child components
    <AuthContext.Provider value={{ currentUser, signup, login, adminLogin, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
  }
  // Custom hook for convenient consumption of AuthContext values in descendant components
export const useAuth = () => useContext(AuthContext);
