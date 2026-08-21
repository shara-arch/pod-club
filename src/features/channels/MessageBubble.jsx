import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useAuth } from '../../routes/AuthContext';
import { deleteMessage, editMessage } from './channelsSlice';
import './channels.css';

function initials(name = '') {
  return name
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}


export default function MessageBubble({ message, onOpenThread, channelName = 'general' }) {
  const dispatch = useDispatch();
  const { currentUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(message.content || '');
  const [reported, setReported] = useState(false);
  const isOwn = message.author?.id === 'me' || message.author?.name === 'You';

  async function saveEdit() { if (draft.trim()) { await dispatch(editMessage({ messageId: message.id, content: draft })).unwrap(); setEditing(false); } }

  function handleReport() {
    if (reported) return;

    const report = {
      id: Date.now(),
      user: message.author?.name || 'Unknown user',
      channel: `#${channelName}`,
      reason: 'Abusive or offensive content',
      status: 'Open',
      banned: false,
      reporter: currentUser?.username || 'Anonymous',
      createdAt: new Date().toISOString(),
    };

    try {
      const existing = JSON.parse(localStorage.getItem('adminReports') || '[]');
      const next = [report, ...existing];
      localStorage.setItem('adminReports', JSON.stringify(next));
      setReported(true);
      window.alert('Report sent to the admin moderation queue.');
    } catch (e) {
      setReported(true);
      window.alert('Report submitted locally.');
    }
  }

  return (
    <div className="pc-message">
      <div className="pc-message__avatar">{initials(message.author.name)}</div>
      <div className="pc-message__body">
        <div className="pc-message__meta">
          <span className="pc-message__author">{message.author.name}</span>
          <span className="pc-message__time">{formatTime(message.timestamp)}</span>
        </div>

        {message.type === 'text' && (editing ? <div className="mt-1 flex gap-2"><input value={draft} onChange={(event) => setDraft(event.target.value)} className="min-w-0 flex-1 rounded-md border border-pod-accent bg-black/30 px-2 py-1 text-sm text-white" /><button onClick={saveEdit} className="text-xs text-pod-accent">Save</button></div> : <p className="pc-message__text">{message.content} {message.edited && <span className="text-xs text-zinc-500">(edited)</span>}</p>)}

        {message.type === 'episode-share' && (
          <div className="pc-message__card">
            <div className="pc-message__card-thumb" />
            <div>
              <p className="pc-message__card-title">{message.content}</p>
              <p className="pc-message__card-subtitle">{message.subtitle}</p>
            </div>
          </div>
        )}

        {message.type === 'image' && (
          message.imageUrl ? <img className="mt-1 max-h-64 rounded-lg border border-pod-border object-cover" src={message.imageUrl} alt={message.imageCaption || 'Shared image'} /> : <div className="pc-message__image-caption">{message.imageCaption || 'Image'}</div>
        )}

        <div className="mt-2 flex gap-3 text-xs"><button onClick={handleReport} className="text-zinc-500 hover:text-red-300">{reported ? 'Reported' : 'Report'}</button>{isOwn && <><button onClick={() => setEditing(true)} className="text-zinc-500 hover:text-pod-accent">Edit</button><button onClick={() => dispatch(deleteMessage(message.id))} className="text-zinc-500 hover:text-red-300">Delete</button></>}</div>

        {message.replyCount > 0 && (
          <button className="pc-message__thread-link" onClick={() => onOpenThread?.(message.threadRootId)}>
            {message.replyCount} {message.replyCount === 1 ? 'reply' : 'replies'} →
          </button>
        )}
      </div>
    </div>
  );
}
