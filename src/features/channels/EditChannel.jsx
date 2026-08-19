import React, { useEffect, useState } from 'react';
import ChannelForm from './ChannelForm';
import { getChannel, updateChannel } from './channelService';
import './channels.css';

// Props:
//   channelId - which channel to edit
//   onSaved(channel) - called after a successful update
//   onCancel()        - called when the user backs out
export default function EditChannel({ channelId, onSaved, onCancel }) {
  const [channel, setChannel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getChannel(channelId)
      .then((data) => {
        if (!cancelled) setChannel(data);
      })
      .catch((err) => {
        if (!cancelled) setLoadError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [channelId]);

  async function handleSubmit(values) {
    const updated = await updateChannel(channelId, values);
    onSaved?.(updated);
  }

  if (loading) return <div className="pc-empty-state">Loading channel…</div>;
  if (loadError) return <div className="pc-empty-state">Couldn't load channel: {loadError}</div>;

  return (
    <div className="pc-screen">
      <ChannelForm initialValues={channel} submitLabel="Save Changes" onSubmit={handleSubmit} onCancel={onCancel} />
    </div>
  );
}
