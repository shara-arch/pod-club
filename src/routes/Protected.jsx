import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

export default function ProtectedRoute({ children }) {
  const { currentUser } = useAuth();
  const location = useLocation();

  if (!currentUser) {
    // Redirect unauthenticated user to /login and save current location
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}