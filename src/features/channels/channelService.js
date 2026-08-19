

import { mockChannels } from './mockData';

// In-memory copy so create/edit/delete "persist" for the session
let channels = [...mockChannels];

const delay = (ms = 300) => new Promise((resolve) => setTimeout(resolve, ms));

export async function getChannels(communityId) {
  await delay();
  return [...channels];
}

export async function getChannel(channelId) {
  await delay();
  const channel = channels.find((c) => c.id === channelId);
  if (!channel) throw new Error(`Channel ${channelId} not found`);
  return channel;
}

export async function createChannel({ name, description, isPrivate, category }) {
  await delay();
  if (!name || !name.trim()) {
    throw new Error('Channel name is required');
  }
  const newChannel = {
    id: name.trim().toLowerCase().replace(/\s+/g, '-'),
    name: name.trim(),
    description: description || '',
    isPrivate: !!isPrivate,
    category: category || 'True Crime',
    lastMessage: null,
    lastMessageAuthor: null,
    hasUnread: false,
  };
  channels = [...channels, newChannel];
  return newChannel;
}

export async function updateChannel(channelId, updates) {
  await delay();
  const index = channels.findIndex((c) => c.id === channelId);
  if (index === -1) throw new Error(`Channel ${channelId} not found`);
  channels[index] = { ...channels[index], ...updates };
  return channels[index];
}

export async function deleteChannel(channelId) {
  await delay();
  channels = channels.filter((c) => c.id !== channelId);
  return true;
}
