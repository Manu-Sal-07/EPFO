'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { fetchProfile, CitizenProfile } from '@/lib/api';

const NAV_LINKS = [
  { href: '/dashboard', label: '🏠 Home' },
  { href: '/health', label: '🏥 PF Health' },
  { href: '/decision', label: '🧭 Decision Wizard' },
  { href: '/cases', label: '📋 CaseWise' },
];

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [profile, setProfile] = useState<CitizenProfile | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('pf_token');
    if (token) {
      fetchProfile(token)
        .then(setProfile)
        .catch(() => setProfile(null));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('pf_token');
    router.push('/');
  };

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      borderBottom: '1px solid rgba(99,102,241,0.18)',
      background: 'rgba(11,15,25,0.92)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
    }}>
      <div style={{
        maxWidth: 1280,
        margin: '0 auto',
        padding: '0 1.5rem',
        height: 60,
        display: 'flex',
        alignItems: 'center',
        gap: '2rem',
      }}>
        {/* Logo */}
        <Link href="/dashboard" style={{ textDecoration: 'none', flexShrink: 0 }}>
          <span style={{
            fontWeight: 800,
            fontSize: '1.15rem',
            letterSpacing: '-0.03em',
            background: 'linear-gradient(135deg, #6366f1 0%, #a78bfa 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}>
            PF COMPASS
          </span>
        </Link>

        {/* Nav Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', flex: 1 }}>
          {NAV_LINKS.map(({ href, label }) => {
            const active = pathname === href || (href !== '/dashboard' && pathname.startsWith(href));
            return (
              <Link
                key={href}
                href={href}
                style={{
                  padding: '0.4rem 0.9rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  fontWeight: active ? 700 : 500,
                  color: active ? '#a5b4fc' : '#64748b',
                  background: active ? 'rgba(99,102,241,0.12)' : 'transparent',
                  textDecoration: 'none',
                  transition: 'all 0.15s ease',
                  whiteSpace: 'nowrap',
                }}
              >
                {label}
              </Link>
            );
          })}
        </nav>

        {/* User + Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0 }}>
          {profile && (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0' }}>
                {profile.display_name}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#475569' }}>{profile.email}</div>
            </div>
          )}
          <button
            onClick={handleLogout}
            style={{
              padding: '0.4rem 0.9rem',
              borderRadius: '8px',
              border: '1px solid rgba(244,63,94,0.3)',
              background: 'rgba(244,63,94,0.08)',
              color: '#f87171',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(244,63,94,0.18)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(244,63,94,0.08)'; }}
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}
