import { useState } from 'react';
import { Check, Headphones } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../routes/AuthContext';
import '../App.css';

const safeDisplayName = (username = '') => username.includes('@') ? '' : username;

export default function Profile() {
  const { currentUser, updateProfile, logout } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState(safeDisplayName(currentUser?.username));
  const [email, setEmail] = useState(currentUser?.email || '');
  const [notifications, setNotifications] = useState(true);
  const [saved, setSaved] = useState(false);
  const changed = () => setSaved(false);
  const save = () => { updateProfile({ username: name || 'PodClub member', email }); setSaved(true); };

  return <main className="profile-page">
    <section className="profile-panel">
      <header className="profile-header"><span className="profile-mark"><Headphones size={20} /></span><div><p className="eyebrow">ACCOUNT SETTINGS</p><h1>Your PodClub profile</h1><p>Set the name members see and control your account preferences.</p></div></header>
      <form onSubmit={(event) => { event.preventDefault(); save(); }}>
        <div className="profile-fields">
          <label className="profile-field"><span>Display name</span><input value={name} onChange={(event) => { setName(event.target.value); changed(); }} placeholder="Choose a display name" autoComplete="nickname" /><small>Shown in your listening rooms and messages.</small></label>
          <label className="profile-field"><span>Email address</span><input value={email} onChange={(event) => { setEmail(event.target.value); changed(); }} type="email" placeholder="you@example.com" autoComplete="email" /><small>Used only for account and invitation updates.</small></label>
        </div>
        <section className="preference-card"><div><h2>Community preferences</h2><p>Choose how PodClub should keep in touch.</p></div><label className="toggle-row"><span><b>Email notifications</b><small>Invites and room activity</small></span><input checked={notifications} onChange={(event) => { setNotifications(event.target.checked); changed(); }} type="checkbox" /></label></section>
        <footer className="profile-actions"><button type="submit" className="gold-button">{saved && <Check size={16} />}{saved ? 'Settings saved' : 'Save settings'}</button>{saved && <span className="save-note"><Check size={15} /> Your changes are saved.</span>}<button type="button" className="sign-out-button" onClick={() => { logout(); navigate('/login', { replace: true }); }}>Sign out</button></footer>
      </form>
    </section>
  </main>;
}
