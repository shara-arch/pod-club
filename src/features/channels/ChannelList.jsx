import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { loadChannels } from './channelsSlice';
import './channels.css';


export default function ChannelList({ communityId, onOpenChannel, onCreateChannel }) {
  const dispatch = useDispatch();
  const { list: channels, status, error } = useSelector((state) => state.channels);

  useEffect(() => {
    dispatch(loadChannels(communityId));
  }, [communityId, dispatch]);

  if (status === 'loading' && channels.length === 0) {
    return <div className="pc-empty-state">Loading channels…</div>;
  }

  if (status === 'failed' && channels.length === 0) {
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
          {channels.map((channel) => {
            const featuredNames = ['general', 'weekly-recommendations', 'case-file-theories'];
            const isFeatured = featuredNames.includes(channel.name);
            return (
              <div
                key={channel.id}
                className={`pc-channel-item ${isFeatured ? 'pc-channel-item--featured' : ''}`}
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
            );
          })}
        </div>
      )}

      <button className="pc-channel-list__create-btn" disabled={channels.length >= 5} onClick={() => onCreateChannel?.()}>
        {channels.length >= 5 ? 'Channel limit reached (5)' : '+ Create Channel'}
      </button>
      <p className="px-5 pb-5 text-center text-xs text-zinc-500">You can create up to five channels. Invitations let members join private channels.</p>
    </div>
  );
}
