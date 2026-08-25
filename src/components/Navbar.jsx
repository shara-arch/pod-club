import { Headphones } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../routes/AuthContext';

export default function Navbar() {
  const { logout, currentUser } = useAuth();
  const navigate = useNavigate();
  return <nav className="public-nav">
    <Link to="/" className="club-brand"><span className="brand-mark"><Headphones size={17} /></span>PodClub</Link>
    <div>{currentUser ? <><Link className="plain-link" to="/dashboard">My rooms</Link><button className="gold-button" onClick={() => { logout(); navigate('/'); }}>Sign out</button></> : <><Link className="plain-link" to="/login">Sign in</Link><Link className="gold-button" to="/register">Create account</Link></>}</div>
  </nav>;
}
