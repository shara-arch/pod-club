

import { mockMessages, mockThreads } from './mockData';

let messagesByChannel = JSON.parse(JSON.stringify(mockMessages));
let threads = JSON.parse(JSON.stringify(mockThreads));

const delay = (ms = 300) => new Promise((resolve) => setTimeout(resolve, ms));

// Replace with real logged-in user once auth exists
const CURRENT_USER = { id: 'me', name: 'You', avatar: null };

export async function getMessages(channelId) {
  await delay();
  return messagesByChannel[channelId] ? [...messagesByChannel[channelId]] : [];
}

export async function sendMessage(channelId, content) {
  await delay();
  if (!content || !content.trim()) {
    throw new Error('Message cannot be empty');
  }
  const newMessage = {
    id: `m-${Date.now()}`,
    channelId,
    author: CURRENT_USER,
    content: content.trim(),
    timestamp: new Date().toISOString(),
    type: 'text',
    replyCount: 0,
  };
  messagesByChannel[channelId] = [...(messagesByChannel[channelId] || []), newMessage];
  return newMessage;
}

export async function getThread(threadId) {
  await delay();
  const thread = threads[threadId];
  if (!thread) throw new Error(`Thread ${threadId} not found`);
  return thread;
}

export async function sendReply(threadId, content) {
  await delay();
  if (!content || !content.trim()) {
    throw new Error('Reply cannot be empty');
  }
  const newReply = {
    id: `tm-${Date.now()}`,
    author: CURRENT_USER,
    content: content.trim(),
    timestamp: new Date().toISOString(),
  };
  if (!threads[threadId]) throw new Error(`Thread ${threadId} not found`);
  threads[threadId] = {
    ...threads[threadId],
    replies: [...threads[threadId].replies, newReply],
  };
  return newReply;
}
