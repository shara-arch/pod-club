import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../routes/AuthContext'

export default function Navbar() {
  const { logout, currentUser } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <nav className="navbar">
      <div className="nav-left">
        <Link to="/" className="logo">PodClub</Link>
      </div>
      <div className="nav-right">
        <Link to="/channels" className="cta">Channels</Link>
        <Link to="/dashboard" className="cta">Dashboard</Link>
        {!currentUser && <Link to="/login" className="cta">Login</Link>}
        {currentUser && currentUser.role === 'admin' && <Link to="/admin" className="cta">Admin</Link>}
        {currentUser && <button type="button" className="cta" onClick={handleLogout}>Log out</button>}
      </div>
    </nav>
  )
}
