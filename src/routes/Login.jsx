import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/AuthContext';
import { AlertCircle, Headphones, Lock, User } from 'lucide-react';

export default function Login() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isSignUp) {
        signup(username, password);
      } else {
        login(username, password);
      }
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden flex items-center justify-center p-4">
      {/* Background image */}
      <div
        className="absolute inset-0 bg-cover bg-center scale-105"
        style={{
          backgroundImage:
            "url('https://i.pinimg.com/1200x/8b/02/46/8b0246de71fd8cfb1d69703f8c922920.jpg')",
        }}
      />
      {/* Dark overlay with orange tint */}
      <div className="absolute inset-0 bg-black/80" />
      <div className="absolute inset-0 bg-gradient-to-br from-orange-950/40 via-black/60 to-black/90" />

      {/* Login card */}
      <div className="relative z-10 w-full max-w-md">
        <div className="backdrop-blur-xl bg-black/60 border border-orange-500/30 rounded-2xl shadow-2xl shadow-orange-500/10 overflow-hidden">
          {/* Header */}
          <div className="px-8 pt-10 pb-6 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 shadow-lg shadow-orange-500/30 mb-4">
              <Headphones className="w-8 h-8 text-black" strokeWidth={2.5} />
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Pod Club
            </h1>
            <p className="text-orange-200/70 mt-2 text-sm">
              {isSignUp ? 'Create your account to join' : 'Welcome back, sign in to continue'}
            </p>
          </div>

          {/* Error banner */}
          {error && (
            <div className="mx-8 mb-4 flex items-center gap-2 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/40 text-red-300 text-sm animate-[fadeIn_0.2s_ease]">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="px-8 pb-8 space-y-5">
            <div className="space-y-2">
              <label
                htmlFor="uname"
                className="block text-sm font-medium text-orange-200"
              >
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-orange-400/60" />
                <input
                  id="uname"
                  type="text"
                  placeholder="Enter username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="w-full pl-11 pr-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label
                htmlFor="psw"
                className="block text-sm font-medium text-orange-200"
              >
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-orange-400/60" />
                <input
                  id="psw"
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-11 pr-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-lg bg-gradient-to-r from-orange-500 to-orange-600 text-black font-semibold tracking-wide shadow-lg shadow-orange-500/30 hover:shadow-orange-500/50 hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              {isSignUp ? 'Sign Up' : 'Log In'}
            </button>

            <div className="relative pt-2">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10" />
              </div>
              <div className="relative flex justify-center">
                <span className="px-3 bg-black/60 text-xs text-white/40 uppercase tracking-wider">
                  or
                </span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError('');
              }}
              className="w-full py-3 rounded-lg bg-white/5 border border-white/10 text-orange-300 hover:bg-orange-500/10 hover:border-orange-500/40 transition-all text-sm font-medium"
            >
              {isSignUp
                ? 'Already have an account? Log In'
                : 'Need an account? Sign Up'}
            </button>
          </form>
        </div>

        <p className="text-center text-white/30 text-xs mt-6">
          Pod Club · Your stories, your tribe
        </p>
      </div>
    </div>
  );
}
