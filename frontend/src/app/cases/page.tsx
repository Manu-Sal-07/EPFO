'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { CaseCard, CaseSummary } from '@/components/cases/CaseCard';
import { API_BASE } from '@/lib/api';

export default function CasesPage() {
  const router = useRouter();
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'ALL' | 'CLAIM' | 'TRANSFER' | 'CORRECTION' | 'GRIEVANCE'>('ALL');
  
  // Add Case Modal state
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [addStep, setAddStep] = useState<number>(1);
  const [caseType, setCaseType] = useState<string>('CLAIM');
  const [caseSubtype, setCaseSubtype] = useState<string>('PF Withdrawal Claim');
  const [initialStatus, setInitialStatus] = useState<string>('SUBMITTED');
  const [notes, setNotes] = useState<string>('');
  const [submittingCase, setSubmittingCase] = useState<boolean>(false);

  const token = typeof window !== 'undefined' ? (localStorage.getItem('pf_token') || localStorage.getItem('token')) : null;

  useEffect(() => {
    if (!token) { router.push('/'); return; }
    fetchCases();
  }, [token]);

  async function fetchCases() {
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/cases`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`Failed to fetch cases: ${res.statusText}`);
      const data = await res.json();
      setCases(data);
    } catch (err: any) {
      setError(err.message || 'Error loading cases');
    } finally {
      setLoading(false);
    }
  }

  const filteredCases = cases.filter((c) => {
    if (filter === 'ALL') return true;
    return c.case_type.toUpperCase() === filter;
  });

  const handleCreateCase = async () => {
    if (!token) return;
    setSubmittingCase(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/cases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          case_type: caseType,
          case_subtype: caseSubtype,
          initial_event_text: notes || `Citizen started tracking ${caseSubtype}`,
        }),
      });
      if (!res.ok) throw new Error('Failed to create case');
      setShowAddModal(false);
      setAddStep(1);
      setNotes('');
      fetchCases();
    } catch (e: any) {
      alert(e.message || 'Could not create case');
    } finally {
      setSubmittingCase(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <Navbar />
      <div className="container" style={{ paddingTop: '2.5rem', paddingBottom: '4rem' }}>
        
        {/* Citizen-First Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontSize: 11, fontWeight: 800, color: 'var(--color-primary)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                CASEWISE
              </span>
              <span style={{ fontSize: 11, color: 'var(--color-text-dim)' }}>
                · Citizen Understanding Layer
              </span>
            </div>
            <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-text-main)', margin: '0 0 6px' }}>
              What happened? What do you know? What&apos;s next?
            </h1>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '1rem', margin: 0, maxWidth: 650, lineHeight: 1.5 }}>
              Turn your EPFO updates and evidence into a clear, understandable case journey.
            </p>
          </div>

          {/* Primary Action Buttons */}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <button
              onClick={() => setShowAddModal(true)}
              style={{
                background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                color: '#fff',
                fontWeight: 700,
                padding: '0.65rem 1.25rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.9rem',
                cursor: 'pointer',
                border: 'none',
                boxShadow: '0 4px 14px rgba(99,102,241,0.3)',
              }}
            >
              + Track a Case
            </button>

            <a
              href="https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ textDecoration: 'none' }}
            >
              <button
                style={{
                  background: 'rgba(255,255,255,0.06)',
                  color: '#e2e8f0',
                  border: '1px solid var(--color-border)',
                  fontWeight: 600,
                  padding: '0.65rem 1.25rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                }}
              >
                Check official EPFO status ↗
              </button>
            </a>
          </div>
        </div>

        {/* Citizen-Friendly Category Filter Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.75rem', overflowX: 'auto' }}>
          {[
            { id: 'ALL', label: 'All' },
            { id: 'CLAIM', label: 'Claims' },
            { id: 'TRANSFER', label: 'Transfers' },
            { id: 'CORRECTION', label: 'Corrections' },
            { id: 'GRIEVANCE', label: 'Grievances' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id as any)}
              style={{
                padding: '0.45rem 1.1rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.875rem',
                fontWeight: 600,
                backgroundColor: filter === tab.id ? 'var(--color-surface-hover)' : 'transparent',
                color: filter === tab.id ? 'var(--color-primary)' : 'var(--color-text-muted)',
                border: filter === tab.id ? '1px solid var(--color-border-bright)' : '1px solid transparent',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-text-muted)' }}>
            Loading CaseWise timeline records...
          </div>
        ) : error ? (
          <div style={{ padding: '1.5rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-md)', color: '#f87171' }}>
            {error}
          </div>
        ) : filteredCases.length === 0 ? (
          /* Redesigned Citizen-First Empty State */
          <div style={{
            textAlign: 'center',
            padding: '3.5rem 2rem',
            background: 'linear-gradient(135deg, rgba(15,23,42,0.8) 0%, rgba(30,41,59,0.8) 100%)',
            borderRadius: 'var(--radius-lg)',
            border: '1.5px dashed var(--color-border)',
            maxWidth: 680,
            margin: '2rem auto 0',
          }}>
            <span style={{ fontSize: 42, display: 'block', marginBottom: 12 }}>🧭</span>
            <h3 style={{ color: 'var(--color-text-main)', fontSize: '1.4rem', fontWeight: 700, margin: '0 0 8px' }}>
              Your PF journey isn&apos;t being tracked yet.
            </h3>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.95rem', marginBottom: '1.75rem', lineHeight: 1.6 }}>
              CaseWise helps you keep claims, transfers, corrections, and grievances organized in one clear timeline.
            </p>

            <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', marginBottom: '1.75rem' }}>
              <button
                onClick={() => setShowAddModal(true)}
                style={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                  color: '#fff',
                  padding: '0.6rem 1.4rem',
                  borderRadius: 'var(--radius-sm)',
                  fontWeight: 700,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  border: 'none',
                }}
              >
                + Track My First Case
              </button>

              <a
                href="https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ textDecoration: 'none' }}
              >
                <button
                  style={{
                    background: 'rgba(255,255,255,0.06)',
                    color: '#e2e8f0',
                    border: '1px solid var(--color-border)',
                    padding: '0.6rem 1.4rem',
                    borderRadius: 'var(--radius-sm)',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                  }}
                >
                  Check Official EPFO Status ↗
                </button>
              </a>
            </div>

            <p style={{ color: 'var(--color-text-dim)', fontSize: '0.8rem', margin: 0, fontStyle: 'italic' }}>
              EPFO remains the source of your official status. CaseWise adds context, evidence, and next actions around it.
            </p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.25rem' }}>
            {filteredCases.map((c) => (
              <CaseCard key={c.id} caseItem={c} />
            ))}
          </div>
        )}
      </div>

      {/* Add Case Modal */}
      {showAddModal && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: 16,
        }}>
          <div style={{
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
            border: '1.5px solid var(--color-border-bright)',
            borderRadius: 16,
            padding: 28,
            maxWidth: 520,
            width: '100%',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.7)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#f8fafc' }}>
                Track a New Case
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: 20, cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            {addStep === 1 ? (
              <div>
                <p style={{ color: '#94a3b8', fontSize: 14, marginBottom: 16 }}>What are you tracking?</p>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 20 }}>
                  {[
                    { type: 'CLAIM', subtype: 'PF Withdrawal Claim', label: '📄 PF Claim' },
                    { type: 'TRANSFER', subtype: 'PF Transfer (Form 13)', label: '🔄 PF Transfer' },
                    { type: 'CORRECTION', subtype: 'Date of Exit Correction', label: '🛠 Record Correction' },
                    { type: 'GRIEVANCE', subtype: 'EPFiGMS Grievance', label: '📣 Grievance' },
                  ].map((opt) => (
                    <button
                      key={opt.type}
                      onClick={() => {
                        setCaseType(opt.type);
                        setCaseSubtype(opt.subtype);
                      }}
                      style={{
                        padding: '14px',
                        borderRadius: 10,
                        border: caseType === opt.type ? '2px solid #6366f1' : '1px solid rgba(255,255,255,0.1)',
                        background: caseType === opt.type ? 'rgba(99,102,241,0.15)' : 'rgba(255,255,255,0.03)',
                        color: '#f8fafc',
                        fontWeight: 600,
                        fontSize: 14,
                        textAlign: 'left',
                        cursor: 'pointer',
                      }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                  <button
                    onClick={() => setAddStep(2)}
                    style={{
                      background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                      color: '#fff',
                      padding: '8px 18px',
                      borderRadius: 8,
                      fontWeight: 700,
                      cursor: 'pointer',
                      border: 'none',
                    }}
                  >
                    Next →
                  </button>
                </div>
              </div>
            ) : addStep === 2 ? (
              <div>
                <div style={{ marginBottom: 14 }}>
                  <label style={{ display: 'block', color: '#cbd5e1', fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
                    Case Subtype / Title
                  </label>
                  <input
                    type="text"
                    value={caseSubtype}
                    onChange={(e) => setCaseSubtype(e.target.value)}
                    style={{
                      width: '100%',
                      background: 'rgba(15,23,42,0.8)',
                      border: '1px solid rgba(255,255,255,0.15)',
                      borderRadius: 8,
                      padding: '10px 12px',
                      color: '#f8fafc',
                      fontSize: 14,
                    }}
                  />
                </div>

                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', color: '#cbd5e1', fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
                    Notes / Reference Details (Optional)
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="e.g. Submitted Form 19 on member portal reference #100987"
                    rows={3}
                    style={{
                      width: '100%',
                      background: 'rgba(15,23,42,0.8)',
                      border: '1px solid rgba(255,255,255,0.15)',
                      borderRadius: 8,
                      padding: '10px 12px',
                      color: '#f8fafc',
                      fontSize: 13,
                      resize: 'none',
                    }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <button
                    onClick={() => setAddStep(1)}
                    style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: 13, cursor: 'pointer' }}
                  >
                    ← Back
                  </button>
                  <button
                    onClick={() => setAddStep(3)}
                    style={{
                      background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                      color: '#fff',
                      padding: '8px 18px',
                      borderRadius: 8,
                      fontWeight: 700,
                      cursor: 'pointer',
                      border: 'none',
                    }}
                  >
                    Next (Evidence) →
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <div style={{
                  padding: 16,
                  background: 'rgba(59,130,246,0.08)',
                  border: '1px solid rgba(59,130,246,0.2)',
                  borderRadius: 10,
                  marginBottom: 16,
                  textAlign: 'center',
                }}>
                  <span style={{ fontSize: 28, display: 'block', marginBottom: 6 }}>📎</span>
                  <p style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600, margin: '0 0 4px' }}>
                    Do you have official evidence?
                  </p>
                  <p style={{ color: '#94a3b8', fontSize: 12, margin: 0 }}>
                    Uploading official document scans or screenshots is strictly optional. CaseWise works fully without uploads.
                  </p>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10 }}>
                  <button
                    onClick={() => setAddStep(2)}
                    style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: 13, cursor: 'pointer' }}
                  >
                    ← Back
                  </button>

                  <div style={{ display: 'flex', gap: 10 }}>
                    <button
                      onClick={handleCreateCase}
                      disabled={submittingCase}
                      style={{
                        background: 'rgba(255,255,255,0.08)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        color: '#e2e8f0',
                        padding: '8px 16px',
                        borderRadius: 8,
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Skip Upload
                    </button>

                    <button
                      onClick={handleCreateCase}
                      disabled={submittingCase}
                      style={{
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        color: '#fff',
                        padding: '8px 18px',
                        borderRadius: 8,
                        fontWeight: 700,
                        cursor: 'pointer',
                        border: 'none',
                      }}
                    >
                      {submittingCase ? 'Saving Case...' : 'Create Case ✓'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
