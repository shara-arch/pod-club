const API_URL = '/api';

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.status === 204 ? null : response.json();
}

export function getChannels(communityId) {
  return request(`/channels?communityId=${encodeURIComponent(communityId)}`);
}

export function getChannel(channelId) {
  return request(`/channels/${channelId}`);
}

export function createChannel({ name, description, isPrivate, category, communityId }) {
  if (!name?.trim()) return Promise.reject(new Error('Channel name is required'));
  const slug = name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  return request('/channels', {
    method: 'POST',
    body: JSON.stringify({
      id: `${slug}-${Date.now()}`, name: name.trim(), description: description || '',
      isPrivate: Boolean(isPrivate), category: category || 'True Crime', communityId,
      lastMessage: null, lastMessageAuthor: null, hasUnread: false,
    }),
  });
}

export function updateChannel(channelId, updates) {
  return request(`/channels/${channelId}`, { method: 'PATCH', body: JSON.stringify(updates) });
}

export function deleteChannel(channelId) {
  return request(`/channels/${channelId}`, { method: 'DELETE' });
}
