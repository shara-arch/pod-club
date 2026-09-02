import { useState } from 'react';
import { Check, Headphones } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../routes/AuthContext';
import '../App.css';

export default function Profile() {
  const { currentUser, updateProfile, logout } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState(currentUser?.display_name || '');
  const [email, setEmail] = useState(currentUser?.email || '');
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const save = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await updateProfile({ display_name: name.trim() || 'PodClub member', email });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setError(err.message || 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  return <main className="profile-page">
    <section className="profile-panel">
      <header className="profile-header"><span className="profile-mark"><Headphones size={20} /></span><div><p className="eyebrow">ACCOUNT SETTINGS</p><h1>Your PodClub profile</h1><p>Set the name members see and control your account preferences.</p></div></header>
      <form onSubmit={save}>
        {error && <p className="text-sm text-red-400 mb-4">{error}</p>}
        <div className="profile-fields">
          <label className="profile-field"><span>Display name</span><input value={name} onChange={(event) => { setName(event.target.value); setSaved(false); }} placeholder="Choose a display name" autoComplete="nickname" /><small>Shown in your listening rooms and messages.</small></label>
          <label className="profile-field"><span>Email address</span><input value={email} onChange={(event) => { setEmail(event.target.value); setSaved(false); }} type="email" placeholder="you@example.com" autoComplete="email" /><small>Used only for account and invitation updates.</small></label>
        </div>
        <footer className="profile-actions">
          <button type="submit" className="gold-button" disabled={saving}>{saved && <Check size={16} />}{saving ? 'Saving…' : saved ? 'Settings saved' : 'Save settings'}</button>
          <button type="button" className="sign-out-button" onClick={() => { logout(); navigate('/login', { replace: true }); }}>Sign out</button>
        </footer>
      </form>
    </section>
  </main>;
}
