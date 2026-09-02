const API_URL = '/api';
import { mockMessages, mockThreads } from './mockData';

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

export async function getMessages(channelId) {
  try {
    const res = await request(`/messages?channelId=${encodeURIComponent(channelId)}`);
    return res.data || res;
  } catch (err) {
    return mockMessages[channelId] || [];
  }
}

export function sendMessage(channelId, content) {
  if (!content?.trim()) return Promise.reject(new Error('Message cannot be empty'));
  return request('/messages', {
    method: 'POST',
    body: JSON.stringify({
      channel_id: channelId,
      content: content.trim(),
      type: 'text',
    }),
  });
}

export function sendImageMessage(channelId, imageUrl, caption = 'Shared image') {
  return request('/messages', {
    method: 'POST',
    body: JSON.stringify({
      channel_id: channelId,
      content: caption,
      type: 'image',
      image_url: imageUrl,
      image_caption: caption,
    }),
  });
}

export function updateMessage(messageId, content) {
  return request(`/messages/${messageId}`, {
    method: 'PATCH',
    body: JSON.stringify({ content: content.trim() }),
  });
}

export function removeMessage(messageId) {
  return request(`/messages/${messageId}`, { method: 'DELETE' });
}

export async function getThread(threadId) {
  try {
    return await request(`/messages/${threadId}/thread`);
  } catch (err) {
    return mockThreads[threadId] || null;
  }
}

export async function sendReply(threadId, content) {
  if (!content?.trim()) throw new Error('Reply cannot be empty');
  try {
    const thread = await getThread(threadId);
    const newReply = await request('/messages', {
      method: 'POST',
      body: JSON.stringify({
        channel_id: thread.channelId,
        content: content.trim(),
        parent_id: threadId,
      }),
    });
    return newReply;
  } catch (err) {
    const fallback = { id: `tm-${Date.now()}`, author: { id: 'me', name: 'You' }, content: content.trim(), timestamp: new Date().toISOString() };
    return Promise.resolve(fallback);
  }
}
