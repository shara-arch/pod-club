import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import { addImageMessage, addMessage, loadChannel, loadMessages, removeChannel } from './channelsSlice';
import './channels.css';


export default function ChatRoom({ channelId, onOpenThread, onBack, onEditChannel }) {
  const dispatch = useDispatch();
  const { activeChannel: channel, messagesByChannel, status, error } = useSelector((state) => state.channels);
  const messages = messagesByChannel[channelId] || [];
  const bannedUsers = JSON.parse(localStorage.getItem('bannedUsers') || '[]');

  const featuredNames = ['general', 'weekly-recommendations', 'case-file-theories'];
  const isFeatured = channel && featuredNames.includes(channel.name);

  useEffect(() => {
    dispatch(loadChannel(channelId));
    dispatch(loadMessages(channelId));
  }, [channelId, dispatch]);

  async function handleSend(text) {
    await dispatch(addMessage({ channelId, content: text })).unwrap();
  }
  async function handleSendImage(imageUrl, caption) { await dispatch(addImageMessage({ channelId, imageUrl, caption })).unwrap(); }
  async function handleDeleteChannel() {
    if (!window.confirm('Delete this channel? This cannot be undone.')) return;
    await dispatch(removeChannel(channelId)).unwrap();
    onBack?.();
  }
  async function handleInvite() {
    const url = `${window.location.origin}/channels?invite=${channelId}`;
    await navigator.clipboard?.writeText(url);
    window.alert('Invitation link copied. Share it with members to join this channel.');
  }

  if (status === 'loading' && !channel) return <div className="pc-empty-state">Loading conversation…</div>;
  if (status === 'failed' && !channel) return <div className="pc-empty-state">Couldn't load messages: {error}</div>;
  if (!channel) return null;

  return (
    <div className={`pc-screen ${isFeatured ? 'pc-screen--featured' : ''}`}>
      <div className="pc-chat__header">
        {onBack && (
          <button onClick={onBack} aria-label="Back" style={{ background: 'none', border: 'none', color: 'inherit', fontSize: 18, cursor: 'pointer' }}>
            ←
          </button>
        )}
        <div>
          <p className="pc-chat__header-title">#{channel.name}</p>
          <p className="pc-chat__header-subtitle">{channel.description}</p>
        </div>
        <div className="ml-auto flex gap-2"><button className="pc-chat__edit" type="button" onClick={handleInvite}>Invite</button><button className="pc-chat__edit" type="button" onClick={onEditChannel}>Edit</button><button className="pc-chat__edit text-red-300" type="button" onClick={handleDeleteChannel}>Delete</button></div>
      </div>

      <div className="pc-chat__messages">
        {messages.length === 0 ? (
          <div className="pc-empty-state">No messages yet. Say something to get things started.</div>
        ) : (
          messages
            .filter((message) => !bannedUsers.includes(message.author?.name))
            .map((message) => (
              <MessageBubble key={message.id} message={message} onOpenThread={onOpenThread} channelName={channel.name} />
            ))
        )}
      </div>

      <MessageInput placeholder={`Message #${channel.name}…`} onSend={handleSend} onSendImage={handleSendImage} />
    </div>
  );
}
