import { useState, useEffect } from 'react';
import { useAuth } from '../routes/AuthContext';

const initialReports = [
  { id: 1, user: 'Alex Morgan', channel: '#general', reason: 'Abusive language', status: 'Open', banned: false },
  { id: 2, user: 'Riley West', channel: '#case-file-theories', reason: 'Spam links', status: 'Reviewed', banned: false },
  { id: 3, user: 'Jordan Lee', channel: '#weekly-recommendations', reason: 'Harassment', status: 'Open', banned: true },
];
const channels = ['general', 'weekly-recommendations', 'case-file-theories', 'aj morning'];

export default function AdminDashboard() {
  const { currentUser } = useAuth();

  // Load reports from localStorage so admin actions persist across reloads in this demo
  const [reports, setReports] = useState(() => {
    try {
      const saved = localStorage.getItem('adminReports');
      return saved ? JSON.parse(saved) : initialReports;
    } catch (e) {
      return initialReports;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('adminReports', JSON.stringify(reports));
    } catch (e) {
      // ignore storage errors
    }
  }, [reports]);

  const toggleBan = (id) => {
    setReports((items) => items.map((item) => item.id === id ? { ...item, banned: !item.banned, status: 'Reviewed' } : item));
  };

  const deleteReport = (id) => {
    setReports((items) => items.filter((item) => item.id !== id));
  };

  const banUser = (username) => {
    // mark all reports for that user as banned
    setReports((items) => items.map((item) => item.user === username ? { ...item, banned: true, status: 'Reviewed' } : item));
    // persist a simple bannedUsers list (frontend-only)
    try {
      const banned = JSON.parse(localStorage.getItem('bannedUsers') || '[]');
      if (!banned.includes(username)) {
        banned.push(username);
        localStorage.setItem('bannedUsers', JSON.stringify(banned));
      }
    } catch (e) {
      // ignore
    }
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#161616_0,#0A0A0A_45%,#09090B_100%)] px-4 py-10 sm:px-8">
      <section className="mx-auto max-w-5xl">
        <div className="mb-7">
          <p className="text-xs font-bold tracking-[.14em] text-[#e8935f] uppercase">Admin console</p>
          <h1 className="mt-2 text-3xl font-bold text-white">Community moderation</h1>
          <p className="mt-2 text-sm text-zinc-400">Review channels, reports, and member access from one place.</p>
          {/* Welcome the currently authenticated admin */}
          <div className="mt-4 rounded-md bg-white/3 px-4 py-3 inline-block">
            <span className="text-sm text-zinc-300">Signed in as </span>
            <strong className="text-white">{currentUser?.username || 'Admin'}</strong>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <Stat label="Active channels" value={channels.length} />
          <Stat label="Open reports" value={reports.filter((report) => report.status === 'Open').length} />
          <Stat label="Banned members" value={reports.filter((report) => report.banned).length} />
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[.75fr_1.25fr]">
          <section className="rounded-2xl border border-[#292929] bg-[#101010] p-5">
            <div className="flex items-center justify-between">
              <h2 className="font-bold text-white">Channels</h2>
              <span className="text-xs text-zinc-500">All created</span>
            </div>
            <div className="mt-4 space-y-2">
              {channels.map((channel) => (
                <div className="flex items-center justify-between rounded-xl bg-white/[.03] px-3 py-3" key={channel}>
                  <span className="text-sm text-zinc-200"># {channel}</span>
                  <button className="text-xs text-[#e8935f]">Review</button>
                </div>
              ))}
            </div>
          </section>

          <section className="overflow-hidden rounded-2xl border border-[#292929] bg-[#101010]">
            <div className="border-b border-[#292929] p-5">
              <h2 className="font-bold text-white">Reported users</h2>
              <p className="mt-1 text-sm text-zinc-400">Actions update this frontend moderation queue.</p>
            </div>

            <div className="divide-y divide-[#292929]">
              {reports.map((report) => (
                <div key={report.id} className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="flex gap-2">
                      <strong className="text-sm text-white">{report.user}</strong>
                      <span className="rounded-full bg-[#e8935f]/10 px-2 py-0.5 text-[10px] font-bold text-[#e8935f]">{report.status}</span>
                    </div>
                    <p className="mt-1 text-xs text-zinc-400">{report.reason} · {report.channel}</p>
                  </div>

                  <div className="flex gap-2">
                    <button onClick={() => toggleBan(report.id)} className={`rounded-lg px-3 py-2 text-xs font-bold ${report.banned ? 'bg-emerald-400/15 text-emerald-300' : 'bg-red-400/15 text-red-300'}`}>
                      {report.banned ? 'Unban user' : 'Ban user'}
                    </button>
                    <button onClick={() => banUser(report.user)} className="rounded-lg px-3 py-2 text-xs font-bold bg-[#e8935f]/10 text-[#e8935f]">Ban user (global)</button>
                    <button onClick={() => deleteReport(report.id)} className="rounded-lg px-3 py-2 text-xs font-bold bg-black/40 border border-white/6 text-white">Delete report</button>
                  </div>
                </div>
              ))}

              {reports.length === 0 && (
                <div className="p-6 text-center text-sm text-zinc-400">No reports — the moderation queue is empty.</div>
              )}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

function Stat({ label, value }) { return <div className="rounded-2xl border border-[#292929] bg-[#101010] p-5"><p className="text-sm text-zinc-400">{label}</p><p className="mt-2 text-3xl font-bold text-[#e8935f]">{value}</p></div>; }
