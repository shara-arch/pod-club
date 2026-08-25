import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { BrowserRouter, Navigate, Route, Routes, useLocation, Link } from 'react-router-dom';
import { Compass, Headphones, MessageSquare, Plus, Radio, ShieldCheck, UsersRound } from 'lucide-react';
import Login from './components/Login';
import { ChannelList, ChatRoom, CreateChannel, EditChannel, ThreadReply } from './features/channels';
import { clearActiveThread } from './features/channels/channelsSlice';
import { mockCommunity } from './features/channels/mockData';
import AuthProvider, { useAuth } from './routes/AuthContext';
import ProtectedRoute, { AdminRoute } from './routes/Protected';
import React from 'react'
import './App.css'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile';
import AdminDashboard from './pages/AdminDashboard';


function ChannelWorkspace() {
  const [view, setView] = useState('channels');
  const [channelId, setChannelId] = useState(null);
  const [threadId, setThreadId] = useState(null);
  const dispatch = useDispatch();
  const location = useLocation();

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    const inviteChannelId = query.get('invite');
    if (inviteChannelId) {
      setChannelId(inviteChannelId);
      setView('chat');
    }
  }, [location.search]);

  const openChannel = (id) => { setChannelId(id); setView('chat'); };
  const returnToChannels = () => { setChannelId(null); setView('channels'); };
  const closeThread = () => { dispatch(clearActiveThread()); setThreadId(null); setView('chat'); };

  return (
    <main className="channel-page">
      <aside className="channel-sidebar">
        <Link to="/dashboard" className="club-brand"><span className="brand-mark"><Headphones size={17} /></span>PodClub</Link>
        <button className="gold-button channel-new" onClick={() => setView('create')}><Plus size={16} /> New channel</button>
        <span className="channel-count">Create up to 5 private rooms</span>
        <nav className="channel-side-nav"><Link to="/dashboard"><Compass size={16} /> Discover rooms</Link><button className="active" onClick={returnToChannels}><MessageSquare size={16} /> Your channels</button></nav>
        <div className="channel-sidebar-note"><b>Invite-only rooms</b><p>Bring the people you actually want to talk with.</p></div>
        <Link to="/profile" className="channel-profile-link">Account settings →</Link>
      </aside>

      <section className="channel-workspace" aria-label={`${mockCommunity.name} channel workspace`}>
        <header className="channel-community-header">
          <div><span>YOUR PODCLUB COMMUNITY</span><h1>{mockCommunity.name}</h1><p>{mockCommunity.members.toLocaleString()} members · {mockCommunity.activeNow} listening now</p></div>
          <button className="outline-button" onClick={() => setView('create')}><Plus size={16} /> Create room</button>
        </header>
        {view === 'channels' && <ChannelList communityId={mockCommunity.id} onOpenChannel={openChannel} onCreateChannel={() => setView('create')} />}
        {view === 'create' && <CreateChannel communityId={mockCommunity.id} onCreated={(channel) => openChannel(channel.id)} onCancel={returnToChannels} />}
        {view === 'edit' && <EditChannel channelId={channelId} onSaved={() => setView('chat')} onCancel={() => setView('chat')} />}
        {view === 'chat' && channelId && <ChatRoom channelId={channelId} onBack={returnToChannels} onEditChannel={() => setView('edit')} onOpenThread={(id) => { setThreadId(id); setView('thread'); }} />}
        {view === 'thread' && threadId && <ThreadReply threadId={threadId} onClose={closeThread} />}
      </section>
    </main>
  );
}

function DashboardPage() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#161616_0,#0A0A0A_45%,#09090B_100%)]">
      <Navbar />
      <Dashboard />
    </main>
  );
}

function Landing() {
  const rooms = ['Lo-fi & Long Focus', 'Casefile Club', 'Afrobeats Deep Cuts'];
  return <main className="landing"><Navbar /><section className="landing-hero"><div className="hero-copy"><span className="hero-pill"><Radio size={14} /> Now with 5 listening rooms per member</span><h1>The room where a record <em>actually gets discussed.</em></h1><p>PodClub is a small, invite-only listening room for people who take music and podcasts seriously. Start a channel, bring the right five people, and talk about what you are hearing.</p><div className="hero-actions"><Link to="/register" className="gold-button">Start a channel</Link><Link to="/dashboard" className="outline-button">Explore live rooms</Link></div><small>Free while we are small. No algorithm, no feed, no ads.</small></div><div className="hero-visual"><div className="record"><Headphones size={62} /></div></div></section><section className="landing-section"><div className="section-title"><div><h2>Rooms open right now</h2><p>A look at what members are listening to together this week.</p></div><Link to="/dashboard">Join to listen in →</Link></div><div className="mini-room-grid">{rooms.map((room, index) => <div className="mini-room" key={room}><div className={`mini-art art-${index}`}><span>{['LO-FI', 'TRUE CRIME', 'AFROBEATS'][index]}</span></div><h3>{room}</h3><p>{['Background music for people who ship things.', 'Weekly episode breakdowns. Spoiler-tagged.', 'Beyond the singles and the usual credits.'][index]}</p><small>{index + 2} members · 31m ago</small></div>)}</div></section><section className="landing-section feature-section"><h2>Built small on purpose, so the conversation stays good.</h2><div className="feature-grid"><div><Radio /><h3>Five rooms, not fifty</h3><p>You can own five channels at a time. Keep only rooms worth showing up for.</p></div><div><UsersRound /><h3>Invite-only by default</h3><p>Every channel has one private link for the people whose taste you trust.</p></div><div><MessageSquare /><h3>Threads that hold a thought</h3><p>Reply directly, edit a bad take, and keep the conversation legible.</p></div><div><ShieldCheck /><h3>Moderation that answers</h3><p>Report a member and an admin sees the context, not just the complaint.</p></div></div></section><section className="landing-cta"><Headphones /><h2>Your five best rooms are waiting.</h2><p>Takes about thirty seconds to set up. Bring one friend and it already works.</p><Link to="/register" className="gold-button">Create your account</Link></section></main>;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Login initialMode="register" />} />
          <Route path="/admin/login" element={<Login admin />} />
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/channels" element={<ProtectedRoute><ChannelWorkspace /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
