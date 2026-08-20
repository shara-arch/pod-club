import React, {createContext, useContext, useState, useEffect} from 'react';

// Create a Context object to hold and share authentication state across components
const AuthContext = createContext(null);
export default function AuthProvider( {children}) {
    // Store currently authenticated user state(load from localStorage on initial render)
  const [currentUser, setCurrentUser] = useState(() => {
    return JSON.parse(localStorage.getItem('activeUser')) || null;
  });
}