import React from 'react'
import { Link } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-left">
        <Link to="/" className="logo">PodClub</Link>
      </div>
      <div className="nav-right">
        <Link to="/channels">Channels</Link>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/login">Login</Link>
        <Link to="/register" className="cta">Register</Link>
      </div>
    </nav>
  )
}
