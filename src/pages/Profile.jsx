import { useState } from 'react';
import { useAuth } from '../routes/AuthContext';

export default function Profile() {
  const { currentUser } = useAuth();
  const [saved, setSaved] = useState(false);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#161616_0,#0A0A0A_45%,#09090B_100%)] px-4 py-10 sm:px-8">
      <section className="mx-auto max-w-2xl rounded-2xl border border-[#292929] bg-[#101010] p-6 shadow-2xl sm:p-8">
        <p className="text-xs font-bold tracking-[.14em] text-[#e8935f] uppercase">Account settings</p>
        <div className="mt-4 flex items-center gap-4 border-b border-[#292929] pb-6">
          <div className="grid size-14 place-items-center rounded-2xl bg-[#e8935f] text-xl font-bold text-black">{currentUser?.username?.slice(0, 1).toUpperCase()}</div>
          <div><h1 className="text-2xl font-bold text-white">{currentUser?.username}</h1><p className="text-sm text-zinc-400">{currentUser?.email || 'Add an email to keep your account secure.'}</p></div>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <label className="text-sm text-zinc-300">Display name<input defaultValue={currentUser?.username} className="mt-2 w-full rounded-xl border border-[#303030] bg-black/40 px-4 py-3 text-white outline-none focus:border-[#e8935f]" /></label>
          <label className="text-sm text-zinc-300">Email address<input defaultValue={currentUser?.email} placeholder="you@example.com" className="mt-2 w-full rounded-xl border border-[#303030] bg-black/40 px-4 py-3 text-white outline-none focus:border-[#e8935f]" /></label>
        </div>
        <div className="mt-7 rounded-xl border border-[#2a2a2a] bg-black/20 p-4"><h2 className="font-semibold text-white">Community preferences</h2><p className="mt-1 text-sm text-zinc-400">Control the invitations and activity updates you receive.</p><label className="mt-4 flex items-center justify-between text-sm text-zinc-200">Email notifications<input defaultChecked type="checkbox" className="accent-[#e8935f]" /></label></div>
        <button onClick={() => setSaved(true)} className="mt-6 rounded-xl bg-[#e8935f] px-5 py-3 text-sm font-bold text-black transition hover:brightness-110">{saved ? 'Settings saved' : 'Save settings'}</button>
      </section>
    </main>
  );
}
