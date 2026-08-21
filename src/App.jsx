import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
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

  const openChannel = (id) => { setChannelId(id); setView('chat'); };
  const returnToChannels = () => { setChannelId(null); setView('channels'); };
  const closeThread = () => { dispatch(clearActiveThread()); setThreadId(null); setView('chat'); };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#161616_0,#0A0A0A_45%,#09090B_100%)] p-0 sm:p-4 lg:p-8">
      <Navbar />

      <section className="channel-workspace mx-auto min-h-screen w-full overflow-hidden border-0 border-pod-border bg-pod-bg shadow-2xl sm:min-h-[calc(100vh-2rem)] sm:max-w-[760px] sm:rounded-[18px] sm:border lg:min-h-[calc(100vh-4rem)]" aria-label={`${mockCommunity.name} channel workspace`}>
        <header className="border-b border-pod-border px-5 py-6 font-sans text-zinc-100">
          <span className="text-[11px] font-bold tracking-[0.08em] text-pod-accent uppercase">Pod Club community</span>
          <h1 className="my-1 text-2xl font-bold">{mockCommunity.name}</h1>
          <p className="m-0 text-[13px] text-zinc-400">{mockCommunity.members.toLocaleString()} members · {mockCommunity.activeNow} online</p>
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
  // Always show the login/signup card first on site entry. The Login component
  // itself will offer a "Continue as <user>" action when a session exists.
  return <Login />;
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
