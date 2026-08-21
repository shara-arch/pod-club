import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MessageInput from './MessageInput';
import { addReply, loadThread } from './channelsSlice';
import './channels.css';

function formatWhen(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const sameDay = date.toDateString() === now.toDateString();
  const time = date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  return sameDay ? time : `${date.toLocaleDateString([], { weekday: 'long' })} at ${time}`;
}

export default function ThreadReply({ threadId, onClose }) {
  const dispatch = useDispatch();
  const { activeThread: thread, status, error } = useSelector((state) => state.channels);

  useEffect(() => {
    dispatch(loadThread(threadId));
  }, [threadId, dispatch]);

  async function handleReply(text) {
    await dispatch(addReply({ threadId, content: text })).unwrap();
  }

  if (status === 'loading' && !thread) return <div className="pc-empty-state">Loading thread…</div>;
  if (status === 'failed' && !thread) return <div className="pc-empty-state">Couldn't load thread: {error}</div>;
  if (!thread) return null;

  const { rootMessage, replies } = thread;

  return (
    <div className="pc-screen">
      <div className="pc-chat__header">
        {onClose && (
          <button onClick={onClose} aria-label="Close" style={{ background: 'none', border: 'none', color: 'inherit', fontSize: 18, cursor: 'pointer' }}>
            ✕
          </button>
        )}
        <p className="pc-chat__header-title">Thread</p>
      </div>

      <div className="pc-thread__root">
        <div className="pc-message__meta">
          <span className="pc-message__author">{rootMessage.author.name}</span>
          <span className="pc-message__time">{formatWhen(rootMessage.timestamp)}</span>
        </div>
        <p className="pc-message__text">{rootMessage.content}</p>
        <p className="pc-thread__reply-count">
          {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
        </p>
      </div>

      <div className="pc-thread__replies">
        {replies.map((reply) => (
          <div className="pc-message" key={reply.id}>
            <div className="pc-message__avatar">{reply.author.name[0]}</div>
            <div className="pc-message__body">
              <div className="pc-message__meta">
                <span className="pc-message__author">{reply.author.name}</span>
                <span className="pc-message__time">{formatWhen(reply.timestamp)}</span>
              </div>
              <p className="pc-message__text">{reply.content}</p>
            </div>
          </div>
        ))}
      </div>

      <MessageInput placeholder="Reply to thread…" onSend={handleReply} />
    </div>
  );
}
