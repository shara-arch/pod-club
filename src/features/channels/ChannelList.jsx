import React, { useEffect, useState } from 'react';
import { getChannels } from './channelService';
import './channels.css';


export default function ChannelList({ communityId, onOpenChannel, onCreateChannel }) {
  const [channels, setChannels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getChannels(communityId)
      .then((data) => {
        if (!cancelled) setChannels(data);
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
  }, [communityId]);

  if (loading) {
    return <div className="pc-empty-state">Loading channels…</div>;
  }

  if (error) {
    return <div className="pc-empty-state">Couldn't load channels: {error}</div>;
  }

  return (
    <div className="pc-screen pc-channel-list">
      <div className="pc-channel-list__header">
        <h1 className="pc-channel-list__title">Channels</h1>
        <p className="pc-channel-list__subtitle">Text &amp; discuss</p>
      </div>

      {channels.length === 0 ? (
        <div className="pc-empty-state">No channels yet. Create the first one.</div>
      ) : (
        <div className="pc-channel-list__items">
          {channels.map((channel) => (
            <div
              key={channel.id}
              className="pc-channel-item"
              onClick={() => onOpenChannel?.(channel.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && onOpenChannel?.(channel.id)}
            >
              <span className="pc-channel-item__icon">{channel.isPrivate ? '🔒' : '#'}</span>
              <div className="pc-channel-item__body">
                <p className="pc-channel-item__name">{channel.name}</p>
                <p className="pc-channel-item__preview">
                  {channel.lastMessageAuthor && <strong>{channel.lastMessageAuthor}: </strong>}
                  {channel.lastMessage || channel.description}
                </p>
              </div>
              {channel.hasUnread && <span className="pc-channel-item__unread" />}
            </div>
          ))}
        </div>
      )}

      <button className="pc-channel-list__create-btn" onClick={() => onCreateChannel?.()}>
        + Create Channel
      </button>
    </div>
  );
}
