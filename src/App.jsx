import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import { ChannelList, ChatRoom, CreateChannel, EditChannel, ThreadReply } from './features/channels';
import { clearActiveThread } from './features/channels/channelsSlice';
import { mockCommunity } from './features/channels/mockData';
import AuthProvider from './routes/AuthContext';
import ProtectedRoute from './routes/Protected';

function ChannelWorkspace() {
  const [view, setView] = useState('channels');
  const [channelId, setChannelId] = useState(null);
  const [threadId, setThreadId] = useState(null);
  const dispatch = useDispatch();

  const openChannel = (id) => { setChannelId(id); setView('chat'); };
  const returnToChannels = () => { setChannelId(null); setView('channels'); };
  const closeThread = () => { dispatch(clearActiveThread()); setThreadId(null); setView('chat'); };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#25201d_0,#090909_42%)] p-0 sm:p-4 lg:p-8">
      <section className="mx-auto min-h-screen w-full overflow-hidden border-0 border-pod-border bg-pod-bg shadow-2xl sm:min-h-[calc(100vh-2rem)] sm:max-w-[760px] sm:rounded-[18px] sm:border lg:min-h-[calc(100vh-4rem)]" aria-label={`${mockCommunity.name} channel workspace`}>
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

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><ChannelWorkspace /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
