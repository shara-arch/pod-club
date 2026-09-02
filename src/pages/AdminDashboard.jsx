import { useState, useEffect } from 'react';
import { useAuth } from '../routes/AuthContext';

const API_URL = '/api';

function authHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  try {
    const token = localStorage.getItem('access_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
  } catch {}
  return headers;
}

async function apiGet(path) {
  const res = await fetch(`${API_URL}${path}`, { headers: authHeaders() });
  if (!res.ok) throw new Error('API error');
  return res.json();
}

async function apiPatch(path) {
  const res = await fetch(`${API_URL}${path}`, { method: 'PATCH', headers: authHeaders() });
  if (!res.ok) throw new Error('API error');
  return res.json();
}

export default function AdminDashboard() {
  const { currentUser } = useAuth();
  const [stats, setStats] = useState(null);
  const [reports, setReports] = useState([]);
  const [channels, setChannels] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const [s, r, c] = await Promise.all([
          apiGet('/admin/stats'),
          apiGet('/admin/reports').catch(() => []),
          apiGet('/admin/channels').catch(() => []),
        ]);
        setStats(s);
        setReports(Array.isArray(r) ? r : r.data || []);
        setChannels(Array.isArray(c) ? c : c.data || []);
      } catch (e) {
        setError('Could not load admin data. You may need admin privileges.');
      }
    }
    load();
  }, []);

  async function handleBan(userId) {
    try {
      await apiPatch(`/admin/users/${userId}/ban`);
      setReports((items) => items.map((r) => r.reportedUser?.id === userId ? { ...r, reportedUser: { ...r.reportedUser, isBanned: true } } : r));
    } catch (e) {
      window.alert('Failed to ban user');
    }
  }

  async function handleUnban(userId) {
    try {
      await apiPatch(`/admin/users/${userId}/unban`);
      setReports((items) => items.map((r) => r.reportedUser?.id === userId ? { ...r, reportedUser: { ...r.reportedUser, isBanned: false } } : r));
    } catch (e) {
      window.alert('Failed to unban user');
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#161616_0,#0A0A0A_45%,#09090B_100%)] px-4 py-10 sm:px-8">
      <section className="mx-auto max-w-5xl">
        <div className="mb-7">
          <p className="text-xs font-bold tracking-[.14em] text-[#e8935f] uppercase">Admin console</p>
          <h1 className="mt-2 text-3xl font-bold text-white">Community moderation</h1>
          <p className="mt-2 text-sm text-zinc-400">Review channels, reports, and member access from one place.</p>
          <div className="mt-4 rounded-md bg-white/3 px-4 py-3 inline-block">
            <span className="text-sm text-zinc-300">Signed in as </span>
            <strong className="text-white">{currentUser?.display_name || currentUser?.email || 'Admin'}</strong>
          </div>
        </div>

        {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

        <div className="grid gap-4 sm:grid-cols-3">
          <Stat label="Total users" value={stats?.total_users ?? '—'} />
          <Stat label="Open reports" value={stats?.open_reports ?? '—'} />
          <Stat label="Banned users" value={stats?.banned_users ?? '—'} />
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[.75fr_1.25fr]">
          <section className="rounded-2xl border border-[#292929] bg-[#101010] p-5">
            <div className="flex items-center justify-between">
              <h2 className="font-bold text-white">Channels</h2>
              <span className="text-xs text-zinc-500">{channels.length} total</span>
            </div>
            <div className="mt-4 space-y-2">
              {channels.map((ch) => (
                <div className="flex items-center justify-between rounded-xl bg-white/[.03] px-3 py-3" key={ch.id}>
                  <span className="text-sm text-zinc-200"># {ch.name}</span>
                  <span className="text-xs text-zinc-500">{ch.memberCount} members</span>
                </div>
              ))}
              {channels.length === 0 && <p className="text-sm text-zinc-500">No channels yet.</p>}
            </div>
          </section>

          <section className="overflow-hidden rounded-2xl border border-[#292929] bg-[#101010]">
            <div className="border-b border-[#292929] p-5">
              <h2 className="font-bold text-white">Reported users</h2>
              <p className="mt-1 text-sm text-zinc-400">Actions are sent to the backend.</p>
            </div>

            <div className="divide-y divide-[#292929]">
              {reports.map((report) => (
                <div key={report.id} className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="flex gap-2">
                      <strong className="text-sm text-white">{report.reportedUser?.name || 'Unknown'}</strong>
                      <span className="rounded-full bg-[#e8935f]/10 px-2 py-0.5 text-[10px] font-bold text-[#e8935f]">{report.status}</span>
                    </div>
                    <p className="mt-1 text-xs text-zinc-400">{report.reason}</p>
                  </div>
                  <div className="flex gap-2">
                    {report.reportedUser?.isBanned ? (
                      <button onClick={() => handleUnban(report.reportedUser.id)} className="rounded-lg px-3 py-2 text-xs font-bold bg-emerald-400/15 text-emerald-300">Unban</button>
                    ) : (
                      <button onClick={() => handleBan(report.reportedUser.id)} className="rounded-lg px-3 py-2 text-xs font-bold bg-red-400/15 text-red-300">Ban user</button>
                    )}
                  </div>
                </div>
              ))}
              {reports.length === 0 && <div className="p-6 text-center text-sm text-zinc-400">No reports.</div>}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

function Stat({ label, value }) { return <div className="rounded-2xl border border-[#292929] bg-[#101010] p-5"><p className="text-sm text-zinc-400">{label}</p><p className="mt-2 text-3xl font-bold text-[#e8935f]">{value}</p></div>; }
