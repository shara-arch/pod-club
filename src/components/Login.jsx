import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../routes/AuthContext';
import { AlertCircle, Headphones, Lock, Mail, User } from 'lucide-react';

export default function Login({ initialMode = 'login', admin = false }) {
  const [isSignUp, setIsSignUp] = useState(initialMode === 'register');
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, signup, adminLogin, currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || (admin ? '/admin' : '/dashboard');

  const passwordStrength = (pw) => {
    if (!pw) return 0;
    let score = 0;
    if (pw.length >= 8) score += 1;
    if (/[A-Z]/.test(pw)) score += 1;
    if (/[0-9]/.test(pw)) score += 1;
    if (/[^A-Za-z0-9]/.test(pw)) score += 1;
    return score;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (admin) {
        await adminLogin(email, password);
      } else if (isSignUp) {
        if (!displayName.trim()) throw new Error('Display name is required.');
        if (!email) throw new Error('Email is required for sign up.');
        if (password !== confirm) throw new Error('Passwords do not match.');
        if (password.length < 6) throw new Error('Password must be at least 6 characters.');
        await signup(email, password, displayName.trim());
      } else {
        if (!email) throw new Error('Email is required.');
        await login(email, password);
      }
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const strength = passwordStrength(password);

  return (
    <div className="relative min-h-screen w-full overflow-hidden flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-cover bg-center scale-105"
        style={{
          backgroundImage:
            "url('https://i.pinimg.com/1200x/8b/02/46/8b0246de71fd8cfb1d69703f8c922920.jpg')",
        }}
      />
      <div className="absolute inset-0 bg-black/60" />
      <div className="absolute inset-0 bg-gradient-to-br from-black/40 via-black/50 to-black/80" />

      <div className="relative z-10 w-full max-w-md">
        <div className="backdrop-blur-xl bg-[#161616]/90 border border-[#2a2a2a] rounded-2xl shadow-2xl shadow-black/50 overflow-hidden">
          <div className="px-8 pt-10 pb-6 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#e8935f] shadow-lg shadow-[#e8935f]/20 mb-4">
              <Headphones className="w-8 h-8 text-black" strokeWidth={2.5} />
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Pod Club
            </h1>
            <p className="text-white/70 mt-2 text-sm">
              {admin ? 'Moderation tools for community administrators' : isSignUp ? 'Create your account to join' : 'Welcome back, sign in to continue'}
            </p>
          </div>

          {currentUser && !admin && (
            <div className="mx-8 mb-4 px-4 py-3 rounded-lg bg-white/5 border border-white/6 text-sm text-white/80 flex flex-col items-center gap-3">
              <div>Signed in as <strong className="text-white">{currentUser.display_name || currentUser.email}</strong></div>
              <div className="flex gap-3">
                <button type="button" onClick={() => navigate(from, { replace: true })} className="px-4 py-2 rounded-md bg-[#e8935f] text-black font-medium">Continue</button>
                <button type="button" onClick={() => { logout(); setError(''); }} className="px-4 py-2 rounded-md border border-white/10 text-white bg-black/20">Switch account</button>
              </div>
            </div>
          )}

          {error && (
            <div className="mx-8 mb-4 flex items-center gap-2 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/40 text-red-300 text-sm animate-[fadeIn_0.2s_ease]">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="px-8 pb-8 space-y-5">
            {isSignUp && !admin && (
              <div className="space-y-2">
                <label htmlFor="dname" className="block text-sm font-medium text-[#e8935f]">Display Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#e8935f]/70" />
                  <input
                    id="dname"
                    type="text"
                    placeholder="What should we call you?"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    required
                    className="w-full pl-11 pr-4 py-3 rounded-lg bg-black/40 border border-[#2a2a2a] text-white placeholder-white/30 focus:outline-none focus:border-[#e8935f] focus:ring-2 focus:ring-[#e8935f]/20 transition-all"
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-[#e8935f]">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#e8935f]/70" />
                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-11 pr-4 py-3 rounded-lg bg-black/40 border border-[#2a2a2a] text-white placeholder-white/30 focus:outline-none focus:border-[#e8935f] focus:ring-2 focus:ring-[#e8935f]/20 transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="psw" className="block text-sm font-medium text-[#e8935f]">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#e8935f]/70" />
                <input
                  id="psw"
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-11 pr-4 py-3 rounded-lg bg-black/40 border border-[#2a2a2a] text-white placeholder-white/30 focus:outline-none focus:border-[#e8935f] focus:ring-2 focus:ring-[#e8935f]/20 transition-all"
                />
              </div>
            </div>

            {isSignUp && !admin && (
              <div className="space-y-2">
                <label htmlFor="confirm" className="block text-sm font-medium text-[#e8935f]">Confirm Password</label>
                <input id="confirm" type="password" placeholder="Repeat password" value={confirm} onChange={(e)=>setConfirm(e.target.value)} required className="w-full pl-4 pr-4 py-3 rounded-lg bg-black/40 border border-[#2a2a2a] text-white placeholder-white/30 focus:outline-none focus:border-[#e8935f] focus:ring-2 focus:ring-[#e8935f]/20 transition-all" />
                <div className="mt-2 flex gap-2 items-center">
                  <div className="h-2 w-24 bg-zinc-800 rounded-full overflow-hidden">
                    <div style={{width: `${(strength/4)*100}%`}} className={`h-2 bg-gradient-to-r from-amber-400 to-emerald-400`} />
                  </div>
                  <div className="text-xs text-zinc-400">Strength: {['Very weak','Weak','Fair','Good','Strong'][strength]}</div>
                </div>
              </div>
            )}

            <button type="submit" disabled={loading} className="w-full py-3 rounded-lg bg-[#e8935f] text-black font-semibold tracking-wide shadow-lg shadow-[#e8935f]/20 hover:bg-[#e8935f]/90 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-60">
              {loading ? (admin ? 'Signing in…' : isSignUp ? 'Creating account…' : 'Signing in…') : (admin ? 'Admin Log In' : isSignUp ? 'Sign Up' : 'Log In')}
            </button>

            {!admin && <div className="relative pt-2">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[#2a2a2a]" />
              </div>
              <div className="relative flex justify-center">
                <span className="px-3 bg-[#161616] text-xs text-white/40 uppercase tracking-wider">or</span>
              </div>
            </div>}

            {!admin && <button
              type="button"
              onClick={() => { setIsSignUp(!isSignUp); setError(''); }}
              className="w-full py-3 rounded-lg bg-black/40 border border-[#2a2a2a] text-[#e8935f] hover:bg-[#e8935f]/10 hover:border-[#e8935f]/40 transition-all text-sm font-medium"
            >
              {isSignUp ? 'Already have an account? Log In' : 'Need an account? Sign Up'}
            </button>}
            {admin && <p className="rounded-lg border border-[#e8935f]/20 bg-[#e8935f]/5 px-3 py-2 text-center text-xs text-white/55">Demo access: <span className="text-[#e8935f]">admin@podclub.com / podclub</span></p>}
          </form>

          <p className="text-center text-white/30 text-xs mt-6">
            Pod Club · Your stories, your tribe
          </p>
        </div>
      </div>
    </div>
  );
}
