import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

export default function ProtectedRoute({ children }) {
  const { currentUser, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center"><p className="text-zinc-400 text-sm">Loading…</p></div>;
  }

  if (!currentUser) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

export function AdminRoute({ children }) {
  const { currentUser, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center"><p className="text-zinc-400 text-sm">Loading…</p></div>;
  }

  if (!currentUser) return <Navigate to="/admin/login" state={{ from: location }} replace />;
  if (currentUser.role !== 'admin') return <Navigate to="/dashboard" replace />;
  return children;
}
