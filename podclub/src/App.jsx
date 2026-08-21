import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/channels" element={<div className="page"><h2>Channels (placeholder)</h2></div>} />
        <Route path="/search" element={<div className="page"><h2>Search (placeholder)</h2></div>} />
        <Route path="/activity" element={<div className="page"><h2>Activity (placeholder)</h2></div>} />
        <Route path="/profile" element={<div className="page"><h2>Profile (placeholder)</h2></div>} />
        <Route path="/login" element={<div className="page"><h2>Login (placeholder)</h2></div>} />
        <Route path="/register" element={<div className="page"><h2>Register (placeholder)</h2></div>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
