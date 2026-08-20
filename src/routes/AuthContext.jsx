import React, {createContext, useContext, useState, useEffect} from 'react';

// Create a Context object to hold and share authentication state across components
const AuthContext = createContext(null);
export default function AuthProvider( {children}) {
    // Store currently authenticated user state(load from localStorage on initial render)
  const [currentUser, setCurrentUser] = useState(() => {
    return JSON.parse(localStorage.getItem('activeUser')) || null;
    // Store mock database of registered users; load from localStorage on initial render
  const [users, setUsers] = useState(() => {
    return JSON.parse(localStorage.getItem('usersDB')) || [];
    // Sync active user session to localStorage or remove it on logout/expiration
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('activeUser', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('activeUser');
    }
  }, [currentUser]);
  // Registers a new user if the username is unique and automatically logs them in
  const signup = (username, password) => {
    const userExists = users.some((u) => u.username === username);
    if (userExists) {
      throw new Error('Username already exists.');
    }
    const newUser = { username, password };
    setUsers((prev) => [...prev, newUser]);
    setCurrentUser({ username }); // Log in user automatically after successful registration
  };
  });
  });
}