'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { fetchProfile, fetchHealth, CitizenProfile, SystemHealth } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<CitizenProfile | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('pf_token');
    if (!token) {
      router.push('/');
      return;
    }

    Promise.all([
      fetchProfile(token).catch(() => null),
      fetchHealth().catch(() => null),
    ]).then(([prof, h]) => {
      if (!prof) {
        localStorage.removeItem('pf_token');
        router.push('/');
        return;
      }
      setProfile(prof);
      setHealth(h);
      setLoading(false);
    });
  }, [router]);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
        <Navbar />
        <div className="container" style={{ paddingTop: '4rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
          Loading your citizen portal...
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)', display: 'flex', flexDirection: 'column' }}>
      <Navbar />

      <main className="container" style={{ flex: 1, padding: '2.5rem 1.5rem 4rem' }}>
        {/* Welcome Header */}
        <div style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', padding: '0.25rem 0.75rem', borderRadius: '999px', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#a5b4fc' }}>● CITIZEN DASHBOARD</span>
            </div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-text-main)', letterSpacing: '-0.02em' }}>
              Welcome back, {profile?.display_name || 'Citizen'}
            </h1>
            <p style={{ fontSize: '0.95rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
              All EPFO intelligence, claim calculators, rule diagnostics, and state tracking — available in one place.
            </p>
          </div>

          {/* System Health pill */}
          <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: health?.status === 'healthy' ? '#10b981' : '#f43f5e' }} />
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>EPFO API Service</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: health?.status === 'healthy' ? '#10b981' : '#f43f5e' }}>
                {health?.status ? health.status.toUpperCase() : 'ONLINE'}
              </div>
            </div>
          </div>
        </div>

        {/* Feature Cards Grid — ALL features for ALL users */}
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '1.25rem' }}>
          Available Services & Tools
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>

          {/* Card 1: PF Health Diagnostic */}
          <Link href="/health" style={{ textDecoration: 'none' }}>
            <div style={{
              background: 'var(--color-surface)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: 'var(--radius-lg)',
              padding: '1.75rem',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              transition: 'all 0.2s ease',
              boxShadow: 'var(--shadow-card)',
              cursor: 'pointer',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#10b981'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.3)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🏥</div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#10b981', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                  Rule Engine Diagnostics
                </div>
                <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '0.5rem' }}>
                  PF Health Diagnostic Report
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
                  Scan your employment records, Exit Dates, UAN multiplicity, and KYC status with deterministic rule engine. Get AI-powered plain language explanations.
                </p>
              </div>
              <div style={{ marginTop: '1.5rem', color: '#10b981', fontWeight: 700, fontSize: '0.875rem' }}>
                Run Health Audit →
              </div>
            </div>
          </Link>

          {/* Card 2: PF Decision Wizard */}
          <Link href="/decision" style={{ textDecoration: 'none' }}>
            <div style={{
              background: 'var(--color-surface)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: 'var(--radius-lg)',
              padding: '1.75rem',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              transition: 'all 0.2s ease',
              boxShadow: 'var(--shadow-card)',
              cursor: 'pointer',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.3)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🧭</div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#a5b4fc', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                  Interactive Claim Wizard
                </div>
                <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '0.5rem' }}>
                  PF Decision Engine & Calculator
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
                  Input your requested withdrawal amount, evaluate Form 19/31 eligibility, compute TDS taxability, and get real AI LLM recommendations.
                </p>
              </div>
              <div style={{ marginTop: '1.5rem', color: '#a5b4fc', fontWeight: 700, fontSize: '0.875rem' }}>
                Open Decision Wizard →
              </div>
            </div>
          </Link>

          {/* Card 3: CaseWise Timeline */}
          <Link href="/cases" style={{ textDecoration: 'none' }}>
            <div style={{
              background: 'var(--color-surface)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: 'var(--radius-lg)',
              padding: '1.75rem',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              transition: 'all 0.2s ease',
              boxShadow: 'var(--shadow-card)',
              cursor: 'pointer',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#8b5cf6'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.3)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📋</div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#c084fc', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                  State Machine & Action Log
                </div>
                <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '0.5rem' }}>
                  CaseWise Timeline Tracker
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
                  Track active transfer & correction cases, view deterministic next actions, simulate back-office events, and read AI-generated narratives.
                </p>
              </div>
              <div style={{ marginTop: '1.5rem', color: '#c084fc', fontWeight: 700, fontSize: '0.875rem' }}>
                Track My Cases →
              </div>
            </div>
          </Link>

        </div>
      </main>
    </div>
  );
}
