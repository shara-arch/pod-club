import React from 'react';
import ChannelForm from './ChannelForm';
import { createChannel } from './channelService';
import './channels.css';

export default function CreateChannel({ communityId, onCreated, onCancel }) {
  async function handleSubmit(values) {
    const channel = await createChannel({ ...values, communityId });
    onCreated?.(channel);
  }

  return (
    <div className="pc-screen">
      <ChannelForm submitLabel="Create Channel" onSubmit={handleSubmit} onCancel={onCancel} />
    </div>
  );
}
