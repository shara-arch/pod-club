const API_URL = '/api';
import { mockChannels } from './mockData';

function getHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  try {
    const token = localStorage.getItem('access_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
  } catch {}
  return headers;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, { headers: getHeaders(), ...options });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.error || `Request failed (${response.status})`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export async function getChannels() {
  try {
    const res = await request('/channels');
    return res.data || res;
  } catch (err) {
    return mockChannels;
  }
}

export async function getChannel(channelId) {
  try {
    return await request(`/channels/${channelId}`);
  } catch (err) {
    return mockChannels.find((c) => c.id === channelId) || null;
  }
}

export function createChannel({ name, description, isPrivate, category }) {
  if (!name?.trim()) return Promise.reject(new Error('Channel name is required'));
  const slug = name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  return request('/channels', {
    method: 'POST',
    body: JSON.stringify({
      id: slug,
      name: name.trim(),
      description: description || '',
      is_private: Boolean(isPrivate),
      category: category || 'True Crime',
    }),
  });
}

export function updateChannel(channelId, updates) {
  const payload = {};
  if (updates.name !== undefined) payload.name = updates.name;
  if (updates.description !== undefined) payload.description = updates.description;
  if (updates.category !== undefined) payload.category = updates.category;
  if (updates.isPrivate !== undefined) payload.is_private = updates.isPrivate;
  return request(`/channels/${channelId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function deleteChannel(channelId) {
  return request(`/channels/${channelId}`, { method: 'DELETE' });
}
