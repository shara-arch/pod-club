const API_URL = '/api';
import { mockChannels } from './mockData';

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.status === 204 ? null : response.json();
}

export async function getChannels(communityId) {
  try {
    return await request(`/channels?communityId=${encodeURIComponent(communityId)}`);
  } catch (err) {
    // Fallback to local mock data when API not available
    return mockChannels.filter((c) => !communityId || c.communityId === communityId || c.communityId == null);
  }
}

export async function getChannel(channelId) {
  try {
    return await request(`/channels/${channelId}`);
  } catch (err) {
    return mockChannels.find((c) => c.id === channelId) || null;
  }
}

export function createChannel({ name, description, isPrivate, category, communityId }) {
  if (!name?.trim()) return Promise.reject(new Error('Channel name is required'));
  const slug = name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  // Try API, but if it fails return a locally-constructed channel object so UI can continue
  const payload = { id: `${slug}-${Date.now()}`, name: name.trim(), description: description || '', isPrivate: Boolean(isPrivate), category: category || 'True Crime', communityId, lastMessage: null, lastMessageAuthor: null, hasUnread: false };
  return request('/channels', { method: 'POST', body: JSON.stringify(payload) }).catch(() => Promise.resolve(payload));
}

export function updateChannel(channelId, updates) {
  return request(`/channels/${channelId}`, { method: 'PATCH', body: JSON.stringify(updates) }).catch(() => Promise.resolve({ id: channelId, ...updates }));
}

export function deleteChannel(channelId) {
  return request(`/channels/${channelId}`, { method: 'DELETE' }).catch(() => Promise.resolve(null));
}
