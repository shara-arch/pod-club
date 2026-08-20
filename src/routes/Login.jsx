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
  return(
    <>
    <h1>Welcome to Pod Club</h1>
    <form onSubmit={handleSubmit}>
     {/* Display validation error message if authentication fails */}
        {error && <div className="error-banner">{error}</div>}

        <div className="container">
          <label htmlFor="uname"><b>Username</b></label>
          <input
            id="uname"
            type="text"
            placeholder="Enter Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label htmlFor="psw"><b>Password</b></label>
          <input
            id="psw"
            type="password"
            placeholder="Enter Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit">{isSignUp ? 'Sign Up' : 'Login'}</button>
        </div>

        <div className="container" style={{ backgroundColor: '#f1f1f1' }}>
          <button 
            type="button" 
            className="toggle-btn"
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError('');
            }}
          >
            {isSignUp ? 'Already have an account? Log In' : 'Need an account? Sign Up'}
          </button>
        </div>
    </form>
    </>
  )
}