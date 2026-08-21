import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import { addMessage, loadChannel, loadMessages } from './channelsSlice';
import './channels.css';


export default function ChatRoom({ channelId, onOpenThread, onBack, onEditChannel }) {
  const dispatch = useDispatch();
  const { activeChannel: channel, messagesByChannel, status, error } = useSelector((state) => state.channels);
  const messages = messagesByChannel[channelId] || [];

  useEffect(() => {
    dispatch(loadChannel(channelId));
    dispatch(loadMessages(channelId));
  }, [channelId, dispatch]);

  async function handleSend(text) {
    await dispatch(addMessage({ channelId, content: text })).unwrap();
  }

  if (status === 'loading' && !channel) return <div className="pc-empty-state">Loading conversation…</div>;
  if (status === 'failed' && !channel) return <div className="pc-empty-state">Couldn't load messages: {error}</div>;
  if (!channel) return null;

  return (
    <div className="pc-screen">
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
        <button className="pc-chat__edit" type="button" onClick={onEditChannel}>Edit</button>
      </div>

      <div className="pc-chat__messages">
        {messages.length === 0 ? (
          <div className="pc-empty-state">No messages yet. Say something to get things started.</div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} onOpenThread={onOpenThread} />
          ))
        )}
      </div>

      <MessageInput placeholder={`Message #${channel.name}…`} onSend={handleSend} />
    </div>
  );
}
