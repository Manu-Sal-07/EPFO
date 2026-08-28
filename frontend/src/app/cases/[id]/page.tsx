'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { NextActionCard, NextActionSet } from '@/components/cases/NextActionCard';
import { TimelineItem, TimelineView } from '@/components/cases/TimelineView';
import { explainCaseNarrative, CaseNarrative, API_BASE } from '@/lib/api';

export interface CaseDetail {
  id: string;
  citizen_id: string;
  case_type: string;
  case_subtype: string;
  status: string;
  opened_at: string;
  resolved_at?: string | null;
  resolution_note?: string | null;
  claim_id?: string | null;
  finding_id?: string | null;
  timeline: {
    case_id: string;
    current_status: string;
    total_duration_days: number;
    items: TimelineItem[];
  };
  next_actions: NextActionSet;
}

export default function CaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.id as string;

  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Note addition
  const [noteText, setNoteText] = useState<string>('');
  const [submittingNote, setSubmittingNote] = useState<boolean>(false);

  // AI Explanation
  const [aiNarrative, setAiNarrative] = useState<CaseNarrative | null>(null);
  const [aiLoading, setAiLoading] = useState<boolean>(false);

  const fetchDetail = async () => {
    try {
      const token = localStorage.getItem('pf_token') || localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/v1/cases/${caseId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`Failed to fetch case detail: ${res.statusText}`);
      const data = await res.json();
      setCaseDetail(data);
    } catch (err: any) {
      setError(err.message || 'Error loading case details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) fetchDetail();
  }, [caseId]);

  const handleAiExplain = async () => {
    if (aiNarrative) return;
    const token = localStorage.getItem('pf_token') || localStorage.getItem('token');
    if (!token) return;
    setAiLoading(true);
    try {
      const res = await explainCaseNarrative(token, caseId);
      setAiNarrative(res);
    } catch (e) {
      console.error('AI case explanation error:', e);
    } finally {
      setAiLoading(false);
    }
  };

  const handleSimulate = async () => {
    setSimulating(true);
    setError(null);
    try {
      const token = localStorage.getItem('pf_token') || localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/v1/cases/${caseId}/simulate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Simulation failed');
      }
      const updated = await res.json();
      setCaseDetail(updated);
    } catch (err: any) {
      setError(err.message || 'Simulation error');
    } finally {
      setSimulating(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteText.trim()) return;
    setSubmittingNote(true);
    try {
      const token = localStorage.getItem('pf_token') || localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/v1/cases/${caseId}/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          event_type: 'NOTE_ADDED',
          actor: 'CITIZEN',
          what_happened: noteText,
          why_it_happened: 'Citizen recorded update to case journey',
        }),
      });
      if (!res.ok) throw new Error('Failed to add note');
      setNoteText('');
      await fetchDetail();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmittingNote(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
        <Navbar />
        <div className="container" style={{ paddingTop: '4rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
          Loading CaseWise journey...
        </div>
      </div>
    );
  }

  if (error || !caseDetail) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
        <Navbar />
        <div className="container" style={{ paddingTop: '4rem' }}>
          <div style={{ padding: '1.5rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-md)', color: '#f87171' }}>
            {error || 'Case not found'}
          </div>
          <div style={{ marginTop: '1rem' }}>
            <Link href="/cases" style={{ color: 'var(--color-primary)', textDecoration: 'underline' }}>
              ← Back to CaseWise
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const isRejected = caseDetail.status === 'REJECTED';
  const hasOfficialReason = !!caseDetail.resolution_note;
  const hasHealthLink = !!caseDetail.finding_id;

  const openedDateStr = new Date(caseDetail.opened_at).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  });

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <Navbar />
      <div className="container" style={{ paddingTop: '2.5rem', paddingBottom: '4rem' }}>
        
        {/* Back Navigation */}
        <div style={{ marginBottom: '1.5rem' }}>
          <Link href="/cases" style={{ fontSize: '0.875rem', color: 'var(--color-text-dim)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
            ← Back to CaseWise
          </Link>
        </div>

        {/* 1. CASE HEADER */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.95) 100%)',
            border: isRejected ? '1.5px solid rgba(239,68,68,0.4)' : '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: '1.75rem',
            marginBottom: '2rem',
            boxShadow: '0 10px 25px -5px rgba(0,0,0,0.4)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 800,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    padding: '3px 10px',
                    borderRadius: 4,
                    background: caseDetail.case_type === 'CORRECTION' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                    color: caseDetail.case_type === 'CORRECTION' ? '#fbbf24' : '#60a5fa',
                  }}
                >
                  {caseDetail.case_type}
                </span>
                <span style={{ fontSize: 12, color: 'var(--color-text-dim)' }}>
                  Source: Citizen provided status update
                </span>
              </div>

              <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-text-main)', margin: '0 0 8px' }}>
                {caseDetail.case_subtype}
              </h1>

              <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                <span>Opened: {openedDateStr}</span>
                <span>Tracked Duration: {caseDetail.timeline.total_duration_days} days</span>
              </div>
            </div>

            {/* Status Pill & Demo Simulator Action */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 12 }}>
              <span
                style={{
                  fontSize: '0.875rem',
                  fontWeight: 800,
                  letterSpacing: '0.05em',
                  padding: '6px 16px',
                  borderRadius: 999,
                  backgroundColor: isRejected ? 'rgba(239,68,68,0.2)' : 'rgba(59,130,246,0.2)',
                  color: isRejected ? '#fca5a5' : '#60a5fa',
                  border: isRejected ? '1px solid rgba(239,68,68,0.4)' : '1px solid rgba(59,130,246,0.4)',
                }}
              >
                {caseDetail.status.replace(/_/g, ' ')}
              </span>

              <button
                onClick={handleSimulate}
                disabled={simulating}
                style={{
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  color: '#cbd5e1',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  padding: '5px 12px',
                  borderRadius: 6,
                  cursor: simulating ? 'not-allowed' : 'pointer',
                  opacity: simulating ? 0.7 : 1,
                }}
              >
                {simulating ? 'Simulating step...' : '⚡ Advance Demo Step'}
              </button>
            </div>
          </div>
        </div>

        {/* 2-COLUMN LAYOUT: 4-PART MODEL & DETAILS */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>

          {/* SECTION: 1. WHAT WE KNOW & 2. WHAT IS UNKNOWN (4-PART MODEL) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            
            {/* 2. WHAT WE KNOW */}
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(15,23,42,0.9) 100%)',
                border: '1px solid rgba(16,185,129,0.3)',
                borderRadius: 14,
                padding: '1.25rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <span style={{ fontSize: 18 }}>✓</span>
                <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: '#6ee7b7', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                  1. WHAT WE KNOW (VERIFIED FACTS)
                </h3>
              </div>
              <ul style={{ paddingLeft: 18, margin: 0, color: '#e2e8f0', fontSize: 13, lineHeight: 1.6 }}>
                <li style={{ marginBottom: 6 }}>
                  <strong>Claim/Case Subtype:</strong> {caseDetail.case_subtype}
                </li>
                <li style={{ marginBottom: 6 }}>
                  <strong>Official Status:</strong> <span style={{ color: isRejected ? '#fca5a5' : '#6ee7b7', fontWeight: 700 }}>{caseDetail.status}</span>
                </li>
                <li style={{ marginBottom: 6 }}>
                  <strong>Opened Date:</strong> {openedDateStr}
                </li>
                <li>
                  <strong>Status Provenance:</strong> Verified via Citizen EPFO portal check
                </li>
              </ul>
            </div>

            {/* 3. WHAT IS UNKNOWN (EXPLICIT UNCERTAINTY) */}
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(239,68,68,0.08) 0%, rgba(15,23,42,0.9) 100%)',
                border: '1px solid rgba(239,68,68,0.3)',
                borderRadius: 14,
                padding: '1.25rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <span style={{ fontSize: 18 }}>❓</span>
                <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: '#fca5a5', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                  2. WHAT IS UNKNOWN (EXPLICIT UNCERTAINTY)
                </h3>
              </div>

              {hasOfficialReason ? (
                <p style={{ color: '#e2e8f0', fontSize: 13, lineHeight: 1.5, margin: 0 }}>
                  Official EPFO Remark: {caseDetail.resolution_note}
                </p>
              ) : (
                <div>
                  <p style={{ color: '#f8fafc', fontSize: 14, fontWeight: 700, margin: '0 0 6px' }}>
                    Official reason: Not available
                  </p>
                  <p style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.5, margin: 0 }}>
                    EPFO&apos;s available status information does not provide a specific rejection reason for this claim.
                  </p>
                  <div style={{ marginTop: 10, padding: '6px 10px', background: 'rgba(239,68,68,0.12)', borderRadius: 6, fontSize: 11, color: '#fca5a5' }}>
                    ℹ PF Compass explicitly does not invent official government rejection reasons when EPFO records omit them.
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 6. PF HEALTH CONNECTION (POSSIBLE CONTRIBUTING FACTOR) */}
          {hasHealthLink && (
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(245,158,11,0.12) 0%, rgba(30,41,59,0.95) 100%)',
                border: '1.5px solid rgba(245,158,11,0.4)',
                borderRadius: 14,
                padding: '1.5rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <span style={{ fontSize: 24 }}>⚠</span>
                <div>
                  <span style={{ fontSize: 11, fontWeight: 800, color: '#fbbf24', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'block' }}>
                    3. WHAT MAY BE RELEVANT (PF HEALTH CONNECTION)
                  </span>
                  <h4 style={{ margin: 0, color: '#fef08a', fontSize: 16, fontWeight: 700 }}>
                    Possible Contributing Factor
                  </h4>
                </div>
              </div>

              <p style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600, margin: '0 0 6px' }}>
                Unresolved PF Health Issue Detected (Rule PFH-001)
              </p>
              
              <p style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.6, margin: '0 0 14px' }}>
                PF Compass identified an unresolved issue in your PF profile before this claim was submitted. 
                <strong style={{ color: '#fbbf24', marginLeft: 4 }}>
                  This issue may affect claim processing, but EPFO has not confirmed it as the official rejection reason.
                </strong>
              </p>

              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                <Link href="/health">
                  <button style={{
                    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                    color: '#000',
                    fontWeight: 700,
                    fontSize: 13,
                    padding: '8px 16px',
                    borderRadius: 8,
                    cursor: 'pointer',
                    border: 'none',
                  }}>
                    Review PF Health Issue →
                  </button>
                </Link>
                <Link href="/decision?type=PF_TRANSFER">
                  <button style={{
                    background: 'rgba(255,255,255,0.08)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    color: '#e2e8f0',
                    fontWeight: 600,
                    fontSize: 13,
                    padding: '8px 16px',
                    borderRadius: 8,
                    cursor: 'pointer',
                  }}>
                    Start Form 13 Transfer →
                  </button>
                </Link>
              </div>
            </div>
          )}

          {/* 7. WHAT PF COMPASS CAN EXPLAIN (AI NARRATIVE) */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(15,23,42,0.95) 100%)',
              border: '1.5px solid rgba(99,102,241,0.35)',
              borderRadius: 14,
              padding: '1.5rem',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 20 }}>🤖</span>
                <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: '#a5b4fc', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                  PF Compass Plain-Language Case Explanation
                </h3>
              </div>

              <button
                onClick={handleAiExplain}
                disabled={aiLoading}
                style={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  color: '#fff',
                  fontWeight: 700,
                  fontSize: 12,
                  padding: '7px 14px',
                  borderRadius: 8,
                  cursor: 'pointer',
                  border: 'none',
                }}
              >
                {aiLoading ? 'Generating AI Guide...' : '✨ Explain Case with AI (Groq)'}
              </button>
            </div>

            {aiNarrative ? (
              <div style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 10, padding: 16 }}>
                <p style={{ color: '#f8fafc', fontSize: 14, fontWeight: 600, margin: '0 0 8px' }}>
                  {aiNarrative.case_summary ?? aiNarrative.status_summary ?? 'Case status summary is not available yet.'}
                </p>
                <p style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.6, margin: '0 0 12px' }}>
                  {aiNarrative.detailed_narrative ?? aiNarrative.citizen_friendly_note ?? aiNarrative.what_is_pending ?? 'Case details are being prepared.'}
                </p>
                <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 8, padding: 12 }}>
                  <span style={{ color: '#6ee7b7', fontSize: 12, fontWeight: 700, display: 'block', marginBottom: 2 }}>RECOMMENDED ACTION</span>
                  <span style={{ color: '#e2e8f0', fontSize: 13 }}>{aiNarrative.recommended_next_step ?? aiNarrative.what_is_pending ?? 'Review the official next action below.'}</span>
                </div>
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: 13, margin: 0, lineHeight: 1.5 }}>
                Your claim is currently marked as {caseDetail.status}. Click above to generate an AI explanation grounded strictly in structured backend facts.
              </p>
            )}
          </div>

          {/* 8. NEXT OFFICIAL ACTION BANNER */}
          <div style={{ marginTop: 8 }}>
            <div style={{ fontSize: 11, fontWeight: 800, color: 'var(--color-primary)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>
              4. WHAT SHOULD YOU DO NEXT? (OFFICIAL ACTION)
            </div>
            <NextActionCard nextActions={caseDetail.next_actions} />
          </div>

          {/* 4. CASE TIMELINE VIEW */}
          <div style={{ marginTop: 12 }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '1.25rem' }}>
              Case Timeline & Event Journey
            </h3>
            <TimelineView items={caseDetail.timeline.items} />
          </div>

          {/* CITIZEN NOTE FORM */}
          <div style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 14,
            padding: '1.5rem',
            marginTop: 16,
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-main)', margin: '0 0 6px' }}>
              Add Personal Note / Communication Log
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: 12 }}>
              Record an update, dispatch slip number, or conversation note to keep your case timeline complete.
            </p>
            <form onSubmit={handleAddNote}>
              <textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                placeholder="Type your note here..."
                rows={3}
                style={{
                  width: '100%',
                  background: 'var(--color-bg)',
                  border: '1px solid var(--color-border-bright)',
                  borderRadius: 8,
                  padding: 12,
                  color: 'var(--color-text-main)',
                  fontSize: 14,
                  resize: 'none',
                  marginBottom: 10,
                }}
              />
              <button
                type="submit"
                disabled={submittingNote || !noteText.trim()}
                style={{
                  background: 'var(--color-primary)',
                  color: '#fff',
                  fontWeight: 700,
                  fontSize: 13,
                  padding: '8px 18px',
                  borderRadius: 8,
                  cursor: submittingNote || !noteText.trim() ? 'not-allowed' : 'pointer',
                  opacity: submittingNote || !noteText.trim() ? 0.5 : 1,
                  border: 'none',
                }}
              >
                {submittingNote ? 'Saving...' : 'Add Note to Timeline'}
              </button>
            </form>
          </div>

        </div>
      </div>
    </div>
  );
}
