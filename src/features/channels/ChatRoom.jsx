import React, { useEffect, useState } from 'react';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import { getMessages, sendMessage } from './messageService';
import { getChannel } from './channelService';
import './channels.css';

// Props:
//   channelId - which channel's messages to show
//   onOpenThread(threadRootId) - navigate to ThreadReply
//   onBack()                    - navigate back to ChannelList
export default function ChatRoom({ channelId, onOpenThread, onBack }) {
  const [channel, setChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([getChannel(channelId), getMessages(channelId)])
      .then(([channelData, messageData]) => {
        if (cancelled) return;
        setChannel(channelData);
        setMessages(messageData);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [channelId]);

  async function handleSend(text) {
    const newMessage = await sendMessage(channelId, text);
    setMessages((prev) => [...prev, newMessage]);
  }

  if (loading) return <div className="pc-empty-state">Loading conversation…</div>;
  if (error) return <div className="pc-empty-state">Couldn't load messages: {error}</div>;

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
