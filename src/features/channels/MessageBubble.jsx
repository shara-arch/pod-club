import React from 'react';
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


export default function MessageBubble({ message, onOpenThread }) {
  return (
    <div className="pc-message">
      <div className="pc-message__avatar">{initials(message.author.name)}</div>
      <div className="pc-message__body">
        <div className="pc-message__meta">
          <span className="pc-message__author">{message.author.name}</span>
          <span className="pc-message__time">{formatTime(message.timestamp)}</span>
        </div>

        {message.type === 'text' && <p className="pc-message__text">{message.content}</p>}

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
          <div className="pc-message__image-caption">{message.imageCaption || 'Image'}</div>
        )}

        {message.replyCount > 0 && (
          <button className="pc-message__thread-link" onClick={() => onOpenThread?.(message.threadRootId)}>
            {message.replyCount} {message.replyCount === 1 ? 'reply' : 'replies'} →
          </button>
        )}
      </div>
    </div>
  );
}
