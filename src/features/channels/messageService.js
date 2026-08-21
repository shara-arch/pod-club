const API_URL = '/api';
const CURRENT_USER = { id: 'me', name: 'You', avatar: null };
import { mockMessages, mockThreads } from './mockData';

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.status === 204 ? null : response.json();
}

export async function getMessages(channelId) {
  try {
    return await request(`/messages?channelId=${encodeURIComponent(channelId)}&_sort=timestamp&_order=asc`);
  } catch (err) {
    return mockMessages[channelId] || [];
  }
}

export function sendMessage(channelId, content) {
  if (!content?.trim()) return Promise.reject(new Error('Message cannot be empty'));
  const payload = { id: `m-${Date.now()}`, channelId, author: CURRENT_USER, content: content.trim(), timestamp: new Date().toISOString(), type: 'text', replyCount: 0 };
  return request('/messages', { method: 'POST', body: JSON.stringify(payload) }).catch(() => Promise.resolve(payload));
}

export function sendImageMessage(channelId, imageUrl, caption = 'Shared image') {
  const payload = { id: `m-${Date.now()}`, channelId, author: CURRENT_USER, imageUrl, imageCaption: caption, timestamp: new Date().toISOString(), type: 'image', replyCount: 0 };
  return request('/messages', { method: 'POST', body: JSON.stringify(payload) }).catch(() => Promise.resolve(payload));
}

export function updateMessage(messageId, content) {
  return request(`/messages/${messageId}`, { method: 'PATCH', body: JSON.stringify({ content: content.trim(), edited: true }) }).catch(() => Promise.resolve({ id: messageId, content }));
}

export function removeMessage(messageId) {
  return request(`/messages/${messageId}`, { method: 'DELETE' }).catch(() => Promise.resolve(null));
}

export async function getThread(threadId) {
  try {
    return await request(`/threads/${threadId}`);
  } catch (err) {
    return mockThreads[threadId] || null;
  }
}

export async function sendReply(threadId, content) {
  if (!content?.trim()) throw new Error('Reply cannot be empty');
  const newReply = { id: `tm-${Date.now()}`, author: CURRENT_USER, content: content.trim(), timestamp: new Date().toISOString() };
  try {
    const thread = await getThread(threadId);
    await request(`/threads/${threadId}`, { method: 'PATCH', body: JSON.stringify({ replies: [...(thread?.replies || []), newReply] }) });
    return newReply;
  } catch (err) {
    // fallback: return reply so UI can optimistically add it
    return Promise.resolve(newReply);
  }
}
