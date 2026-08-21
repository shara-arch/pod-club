import React from 'react'
import { NavLink } from 'react-router-dom'

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      <NavLink to="/" className="nav-item">🏠<span>Home</span></NavLink>
      <NavLink to="/search" className="nav-item">🔍<span>Search</span></NavLink>
      <NavLink to="/channels" className="nav-item"><span>Channels</span></NavLink>
      <NavLink to="/activity" className="nav-item"><span>Activity</span></NavLink>
      <NavLink to="/profile" className="nav-item"><span>Profile</span></NavLink>
    </nav>
  )
}
