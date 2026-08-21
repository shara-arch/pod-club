import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ChannelForm from './ChannelForm';
import { loadChannel, saveChannel } from './channelsSlice';
import './channels.css';


export default function EditChannel({ channelId, onSaved, onCancel }) {
  const dispatch = useDispatch();
  const { activeChannel: channel, status, error } = useSelector((state) => state.channels);

  useEffect(() => {
    dispatch(loadChannel(channelId));
  }, [channelId, dispatch]);

  async function handleSubmit(values) {
    const updated = await dispatch(saveChannel({ channelId, values })).unwrap();
    onSaved?.(updated);
  }

  if (status === 'loading' && !channel) return <div className="pc-empty-state">Loading channel…</div>;
  if (status === 'failed' && !channel) return <div className="pc-empty-state">Couldn't load channel: {error}</div>;

  return (
    <div className="pc-screen">
      <div className="pc-page-header">
        <button className="pc-icon-button" onClick={onCancel} type="button" aria-label="Back to chat">←</button>
        <div><h2>Edit channel</h2><p>Update the channel details and visibility.</p></div>
      </div>
      <ChannelForm initialValues={channel} submitLabel="Save Changes" onSubmit={handleSubmit} onCancel={onCancel} />
    </div>
  );
}
