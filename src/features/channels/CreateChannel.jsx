import React from 'react';
import { useDispatch } from 'react-redux';
import ChannelForm from './ChannelForm';
import { addChannel } from './channelsSlice';
import './channels.css';

export default function CreateChannel({ communityId, onCreated, onCancel }) {
  const dispatch = useDispatch();

  async function handleSubmit(values) {
    const channel = await dispatch(addChannel({ ...values, communityId })).unwrap();
    onCreated?.(channel);
  }

  return (
    <div className="pc-screen">
      <div className="pc-page-header">
        <button className="pc-icon-button" onClick={onCancel} type="button" aria-label="Back to channels">←</button>
        <div><h2>Create a channel</h2><p>Start a focused conversation for your community.</p></div>
      </div>
      <ChannelForm submitLabel="Create Channel" onSubmit={handleSubmit} onCancel={onCancel} />
    </div>
  );
}
