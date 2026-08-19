// mockData.js
// Stand-in data shaped like what the real API will eventually return.
// Swap channelService.js / messageService.js to fetch() calls later —
// nothing that imports this file needs to change.

export const mockCommunity = {
  id: 'true-crime-circle',
  name: 'True Crime Circle',
  members: 12400,
  activeNow: 840,
  description:
    'Sifting through unsolved mysteries, cold cases, and podcast breakdowns together. Join voice channels to debate theories in real-time.',
};

export const mockChannels = [
  {
    id: 'general',
    name: 'general',
    description: 'Main discussion for the community',
    isPrivate: false,
    category: 'True Crime',
    lastMessage: "Check the timeline of the murder weapon...",
    lastMessageAuthor: 'Lexi',
    hasUnread: true,
  },
  {
    id: 'weekly-recommendations',
    name: 'weekly-recommendations',
    description: 'Share podcast episodes worth a listen',
    isPrivate: false,
    category: 'True Crime',
    lastMessage: 'Podcast Share: Dark Audio Archives Ep 42',
    lastMessageAuthor: null,
    hasUnread: false,
  },
  {
    id: 'case-file-theories',
    name: 'case-file-theories',
    description: 'Break down evidence and swap theories',
    isPrivate: false,
    category: 'True Crime',
    lastMessage: "He couldn't have been in Boston.",
    lastMessageAuthor: 'Liam',
    hasUnread: true,
  },
];

export const mockMessages = {
  general: [
    {
      id: 'm1',
      channelId: 'general',
      author: { id: 'u1', name: 'Leo Drake', avatar: null },
      content: 'Have you guys checked the neighborhood layout map yet? It changes everything.',
      timestamp: '2026-08-18T10:14:00Z',
      type: 'text',
      replyCount: 0,
    },
    {
      id: 'm2',
      channelId: 'general',
      author: { id: 'u2', name: 'Sarah Jenkins', avatar: null },
      content: 'Ep 42: The Midnight Alibi',
      subtitle: 'The Serial Killer Next Door',
      timestamp: '2026-08-18T10:16:00Z',
      type: 'episode-share',
      replyCount: 0,
    },
    {
      id: 'm3',
      channelId: 'general',
      author: { id: 'u1', name: 'Leo Drake', avatar: null },
      content: null,
      imageCaption: 'Neighborhood layout map',
      timestamp: '2026-08-18T10:18:00Z',
      type: 'image',
      replyCount: 3,
      threadRootId: 't1',
    },
  ],
};

export const mockThreads = {
  t1: {
    id: 't1',
    channelId: 'general',
    rootMessage: {
      id: 'tm0',
      author: { id: 'u3', name: "Liam O'Connor", avatar: null },
      content:
        'What do you think about the timeline in Episode 3? The witness claims they heard the scream at 11:15, but the phone logs put the call at 11:45. That is a massive 30-minute gap.',
      timestamp: '2026-08-17T16:30:00Z',
    },
    replies: [
      {
        id: 'tm1',
        author: { id: 'u4', name: 'Lexi Miller', avatar: null },
        content: "The alibi relies on that gap. I bet she was deleting the search history.",
        timestamp: '2026-08-18T09:55:00Z',
      },
      {
        id: 'tm2',
        author: { id: 'u5', name: 'Marc K.', avatar: null },
        content: "Exactly! The metadata doesn't lie.",
        timestamp: '2026-08-18T09:57:00Z',
      },
    ],
  },
};
