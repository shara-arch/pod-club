const API_URL = '/api';
const CURRENT_USER = { id: 'me', name: 'You', avatar: null };

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.status === 204 ? null : response.json();
}

export function getMessages(channelId) {
  return request(`/messages?channelId=${encodeURIComponent(channelId)}&_sort=timestamp&_order=asc`);
}

export function sendMessage(channelId, content) {
  if (!content?.trim()) return Promise.reject(new Error('Message cannot be empty'));
  return request('/messages', {
    method: 'POST',
    body: JSON.stringify({ id: `m-${Date.now()}`, channelId, author: CURRENT_USER, content: content.trim(), timestamp: new Date().toISOString(), type: 'text', replyCount: 0 }),
  });
}

export function sendImageMessage(channelId, imageUrl, caption = 'Shared image') {
  return request('/messages', {
    method: 'POST',
    body: JSON.stringify({ id: `m-${Date.now()}`, channelId, author: CURRENT_USER, imageUrl, imageCaption: caption, timestamp: new Date().toISOString(), type: 'image', replyCount: 0 }),
  });
}

export function updateMessage(messageId, content) {
  return request(`/messages/${messageId}`, { method: 'PATCH', body: JSON.stringify({ content: content.trim(), edited: true }) });
}

export function removeMessage(messageId) {
  return request(`/messages/${messageId}`, { method: 'DELETE' });
}

export function getThread(threadId) {
  return request(`/threads/${threadId}`);
}

export async function sendReply(threadId, content) {
  if (!content?.trim()) throw new Error('Reply cannot be empty');
  const thread = await getThread(threadId);
  const newReply = { id: `tm-${Date.now()}`, author: CURRENT_USER, content: content.trim(), timestamp: new Date().toISOString() };
  await request(`/threads/${threadId}`, { method: 'PATCH', body: JSON.stringify({ replies: [...thread.replies, newReply] }) });
  return newReply;
}
