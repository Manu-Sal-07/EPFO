'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { fetchHealth, login, SystemHealth } from '@/lib/api';

const DEMO_USERS = [
  {
    role: 'Multi-Issue Citizen',
    name: 'Rajesh Kumar',
    email: 'multi@pfcompass.demo',
    desc: '2 UANs, Inoperative PF Account, Missing Exit Date',
    color: '#f59e0b',
  },
  {
    role: 'Claim-Ready Citizen',
    name: 'Ananya Sharma',
    email: 'healthy@pfcompass.demo',
    desc: 'Healthy Record, Fully Verified, Eligible for Withdrawal',
    color: '#10b981',
  },
  {
    role: 'Active-Correction Citizen',
    name: 'Vikram Patel',
    email: 'correction@pfcompass.demo',
    desc: 'In-flight Exit Date Correction CaseWise timeline',
    color: '#3b82f6',
  },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('multi@pfcompass.demo');
  const [password, setPassword] = useState('demo123456');
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If already logged in, go to dashboard
  useEffect(() => {
    const token = localStorage.getItem('pf_token');
    if (token) {
      router.push('/dashboard');
    }
  }, [router]);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unhealthy', environment: 'dev', database: false, redis: false, version: '0.1.0' }));
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await login(email, password);
      localStorage.setItem('pf_token', res.access_token);
      // Redirect to dashboard after successful login
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem', background: 'linear-gradient(135deg, #0b0f19 0%, #0f172a 50%, #1a0a2e 100%)' }}>
      <div style={{ maxWidth: '440px', width: '100%', background: 'var(--color-surface)', padding: '2.5rem', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)', boxShadow: 'var(--shadow-card)' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.025em', background: 'linear-gradient(135deg, #6366f1 0%, #a78bfa 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>PF COMPASS</h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Citizen-First EPFO Redesign</p>
        </div>

        {/* Health status badge */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--color-bg)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem', border: '1px solid var(--color-border)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Backend Status</span>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: health?.status === 'healthy' ? '#10b981' : '#f43f5e' }}>
            ● {health ? health.status.toUpperCase() : 'CHECKING...'}
          </span>
        </div>

        {/* Quick Demo Selector */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-dim)', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'block' }}>Select Demo Profile (all features available)</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {DEMO_USERS.map((user) => (
              <button
                key={user.email}
                type="button"
                onClick={() => { setEmail(user.email); setPassword('demo123456'); }}
                style={{
                  textAlign: 'left',
                  padding: '0.65rem 0.85rem',
                  borderRadius: 'var(--radius-md)',
                  border: email === user.email ? `1.5px solid ${user.color}` : '1px solid var(--color-border)',
                  background: email === user.email ? 'var(--color-surface-hover)' : 'transparent',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ fontSize: '0.825rem', fontWeight: 600, color: user.color }}>{user.role}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>{user.name} — {user.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem', display: 'block' }}>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: '100%', padding: '0.65rem 0.85rem', background: 'var(--color-bg)', border: '1px solid var(--color-border-bright)', borderRadius: 'var(--radius-sm)', color: '#fff', fontSize: '0.875rem' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem', display: 'block' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%', padding: '0.65rem 0.85rem', background: 'var(--color-bg)', border: '1px solid var(--color-border-bright)', borderRadius: 'var(--radius-sm)', color: '#fff', fontSize: '0.875rem' }}
            />
          </div>

          {error && <div style={{ fontSize: '0.8rem', color: '#f43f5e', background: 'rgba(244, 63, 94, 0.1)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>{error}</div>}

          <button
            type="submit"
            disabled={loading}
            style={{ marginTop: '0.5rem', width: '100%', padding: '0.75rem', background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', color: '#fff', fontWeight: 700, borderRadius: 'var(--radius-md)', fontSize: '0.875rem', cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1, transition: 'all 0.15s ease' }}
          >
            {loading ? 'Authenticating...' : 'Sign In to Portal →'}
          </button>
        </form>
      </div>
    </main>
  );
}
