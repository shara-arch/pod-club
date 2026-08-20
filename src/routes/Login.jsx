import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
export default function Login(){
  const [isSignUp, setIsSignUp] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

    // Redirect target after login (defaults to dashboard)
  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(''); // Reset previous error

    try {
      if (isSignUp) {
        signup(username, password);
      } else {
        login(username, password);
      }
      // Navigate to protected page upon success
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message); // Display error ("Incorrect password.")
    }
  };
}