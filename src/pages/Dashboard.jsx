import { useEffect, useMemo, useState } from 'react';
import { Headphones, MessageCircle, Plus, Search, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../routes/AuthContext';

const FALLBACK_PODCASTS = [
  { id: 'lofi', title: 'Lo-fi & Long Focus', artist: 'The Daily Focus', genre: 'LO-FI', artwork: 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=800&q=85', description: 'Background music for people who ship things.' },
  { id: 'crime', title: 'Casefile Club', artist: 'Casefile Presents', genre: 'TRUE CRIME', artwork: 'https://images.unsplash.com/photo-1516575334481-f85287c2c82d?auto=format&fit=crop&w=800&q=85', description: 'Weekly episode breakdowns and careful theories.' },
  { id: 'afro', title: 'Afrobeats Deep Cuts', artist: 'Culture Frequency', genre: 'AFROBEATS', artwork: 'https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?auto=format&fit=crop&w=800&q=85', description: 'Album tracks, B-sides and the people behind them.' },
  { id: 'jazz', title: 'Sunday Morning Jazz', artist: 'Blue Note Sessions', genre: 'JAZZ', artwork: 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=800&q=85', description: 'Slow records and slower conversation.' },
  { id: 'amapiano', title: 'Amapiano After Hours', artist: 'Night Shift Radio', genre: 'AMAPIANO', artwork: 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=800&q=85', description: 'Log-drum discoveries for the late night.' },
];

const toRoom = (result, index) => ({ id: result.collectionId || result.trackId || index, title: result.collectionName || result.trackName, artist: result.artistName, genre: result.primaryGenreName?.toUpperCase() || 'PODCAST', artwork: (result.artworkUrl600 || result.artworkUrl100 || '').replace('100x100', '600x600'), description: result.collectionName ? `A listening room for fans of ${result.collectionName}.` : 'A small room for thoughtful listening.' });

export default function Dashboard() {
  const { currentUser } = useAuth();
  const [podcasts, setPodcasts] = useState(FALLBACK_PODCASTS);
  const [filter, setFilter] = useState('All topics');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    fetch('https://itunes.apple.com/search?term=music+podcasts&media=podcast&entity=podcast&limit=12', { signal: controller.signal })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error('Podcast API unavailable')))
      .then((data) => { const liveRooms = data.results.filter((item) => item.artworkUrl600 || item.artworkUrl100).slice(0, 8).map(toRoom); if (liveRooms.length) setPodcasts(liveRooms); })
      .catch(() => {}).finally(() => setLoading(false));
    return () => controller.abort();
  }, []);
  const topics = ['All topics', 'Music', 'True Crime', 'Society', 'Culture'];
  const rooms = useMemo(() => podcasts.filter((room) => (filter === 'All topics' || room.genre.includes(filter.toUpperCase())) && `${room.title} ${room.artist} ${room.genre}`.toLowerCase().includes(query.toLowerCase())), [podcasts, filter, query]);
  const firstName = currentUser?.username || 'there';
  return <div className="club-shell">
    <aside className="club-sidebar"><Link to="/dashboard" className="club-brand"><span className="brand-mark"><Headphones size={17} /></span>PodClub</Link><Link to="/channels" className="gold-button sidebar-create"><Plus size={16} /> New channel</Link><span className="channel-count">0 of 5 channels used</span><nav className="club-nav"><a className="active" href="#discover"><Search size={16} /> Discover rooms</a></nav><p className="sidebar-label">YOUR ROOMS</p><p className="sidebar-empty">No rooms yet. Create one, or accept an invite link from a friend.</p><Link to="/profile" className="club-user"><span>{firstName.slice(0, 2).toUpperCase()}</span><div><b>{firstName}</b><small>@{firstName.toLowerCase()}</small></div></Link></aside>
    <main className="club-content" id="discover"><div className="welcome-row"><div><p className="eyebrow">Tuesday, August 25</p><h1>Good to see you, {firstName}</h1><p className="lede">Find a great listen, then bring the conversation to your people.</p></div><Link to="/channels" className="gold-button"><Plus size={16} /> New channel</Link></div><section className="slots"><div><b>Channel slots</b><span>0 / 5</span></div><div className="slot-lines">{Array.from({ length: 5 }).map((_, index) => <i key={index} />)}</div></section><section className="discover-head"><h2>Discover rooms</h2><p>Every room on PodClub is invite-only. Find something worth hearing and ask the host for a link.</p></section><label className="room-search"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search podcasts, topics or hosts" /></label><div className="topic-row">{topics.map((topic) => <button className={filter === topic ? 'selected' : ''} onClick={() => setFilter(topic)} key={topic}>{topic}</button>)}</div><div className="room-result"><p>{loading ? 'FINDING ROOMS' : `${rooms.length} ROOMS`}</p></div><div className="room-grid">{rooms.map((room, index) => <article className="room-card" key={room.id}><div className="room-art" style={{ backgroundImage: `linear-gradient(0deg, rgba(0,0,0,.62), transparent 60%), url(${room.artwork})` }}><span>{room.genre}</span><Headphones size={16} /></div><div className="room-body"><h3>{room.title}</h3><p>{room.description}</p><div className="room-stats"><span><Users size={14} /> {2 + (index % 4)}</span><span><MessageCircle size={14} /> {2 + (index % 6)}</span><time>28m ago</time></div><footer>Hosted by {room.artist}<button>Invite only</button></footer></div></article>)}</div></main>
  </div>;
}
