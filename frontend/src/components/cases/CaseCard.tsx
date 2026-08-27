'use client';

import React from 'react';
import Link from 'next/link';

export interface CaseSummary {
  id: string;
  citizen_id: string;
  case_type: 'CLAIM' | 'CORRECTION' | string;
  case_subtype: string;
  status: string;
  opened_at: string;
  resolved_at?: string | null;
  event_count: number;
  latest_event_text?: string;
  finding_id?: string | null;        // non-null = PF Health connection exists
  resolution_note?: string | null;   // null = official reason not available
}

// ── Status Configuration ───────────────────────────────────────────────────────

const STATUS_CONFIG: Record<string, { dot: string; pill: string; pillText: string; label: string }> = {
  SUBMITTED:        { dot: '#3b82f6', pill: 'rgba(59,130,246,0.15)',   pillText: '#60a5fa', label: 'Submitted' },
  UNDER_REVIEW:     { dot: '#f59e0b', pill: 'rgba(245,158,11,0.15)',   pillText: '#fbbf24', label: 'Under Review' },
  DOCUMENT_PENDING: { dot: '#f43f5e', pill: 'rgba(244,63,94,0.15)',    pillText: '#f87171', label: 'Document Pending' },
  APPROVED:         { dot: '#14b8a6', pill: 'rgba(20,184,166,0.15)',   pillText: '#2dd4bf', label: 'Approved' },
  SETTLED:          { dot: '#10b981', pill: 'rgba(16,185,129,0.15)',   pillText: '#34d399', label: 'Settled' },
  RESOLVED:         { dot: '#10b981', pill: 'rgba(16,185,129,0.15)',   pillText: '#34d399', label: 'Resolved' },
  REJECTED:         { dot: '#ef4444', pill: 'rgba(239,68,68,0.15)',    pillText: '#f87171', label: 'Rejected' },
  OPEN:             { dot: '#3b82f6', pill: 'rgba(59,130,246,0.15)',   pillText: '#60a5fa', label: 'Open' },
  IN_CORRECTION:    { dot: '#f59e0b', pill: 'rgba(245,158,11,0.15)',   pillText: '#fbbf24', label: 'In Correction' },
  PENDING_EPFO:     { dot: '#a855f7', pill: 'rgba(168,85,247,0.15)',   pillText: '#c084fc', label: 'Pending EPFO' },
};

const DEFAULT_STATUS = { dot: '#6b7280', pill: 'rgba(107,114,128,0.15)', pillText: '#9ca3af', label: 'Unknown' };

// ── Source Badge ──────────────────────────────────────────────────────────────
// Maps CaseEvent.actor provenance to citizen-readable source labels.
// CITIZEN = citizen-provided status update
// EPFO = official EPFO event (rare in demo without live integration)
// SYSTEM = PF Compass analysis

function SourceBadge({ source }: { source: 'CITIZEN' | 'EPFO' | 'PF_COMPASS' | 'NOT_AVAILABLE' }) {
  const configs = {
    CITIZEN:       { icon: '●', label: 'Citizen provided', color: '#60a5fa', bg: 'rgba(59,130,246,0.1)' },
    EPFO:          { icon: '✓', label: 'EPFO verified',    color: '#10b981', bg: 'rgba(16,185,129,0.1)' },
    PF_COMPASS:    { icon: '◐', label: 'PF Compass',       color: '#a855f7', bg: 'rgba(168,85,247,0.1)' },
    NOT_AVAILABLE: { icon: '?', label: 'Not available',    color: '#6b7280', bg: 'rgba(107,114,128,0.1)' },
  };
  const cfg = configs[source];
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      fontSize: 10, fontWeight: 700, letterSpacing: '0.05em',
      color: cfg.color, background: cfg.bg,
      padding: '2px 7px', borderRadius: 999,
    }}>
      {cfg.icon} {cfg.label.toUpperCase()}
    </span>
  );
}

// ── Case Type Label ───────────────────────────────────────────────────────────

function caseTypeLabel(caseType: string): string {
  const map: Record<string, string> = {
    CLAIM: 'Claim',
    CORRECTION: 'Record Correction',
    TRANSFER: 'PF Transfer',
    GRIEVANCE: 'Grievance',
  };
  return map[caseType.toUpperCase()] || caseType;
}

// ── CaseCard ─────────────────────────────────────────────────────────────────

export const CaseCard: React.FC<{ caseItem: CaseSummary }> = ({ caseItem }) => {
  const statusCfg = STATUS_CONFIG[caseItem.status] || DEFAULT_STATUS;
  const isRejected = caseItem.status === 'REJECTED';
  const hasHealthLink = !!caseItem.finding_id;

  const openedDate = new Date(caseItem.opened_at).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  });
  const resolvedDate = caseItem.resolved_at
    ? new Date(caseItem.resolved_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    : null;

  // Source provenance: determine from context
  // All demo cases are citizen-provided status updates or PF Compass analysis
  const statusSource: 'CITIZEN' | 'EPFO' | 'PF_COMPASS' | 'NOT_AVAILABLE' = 'CITIZEN';

  return (
    <Link href={`/cases/${caseItem.id}`} style={{ textDecoration: 'none', display: 'block' }}>
      <div
        style={{
          background: 'var(--color-surface)',
          border: isRejected
            ? '1px solid rgba(239,68,68,0.35)'
            : '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          transition: 'all 0.2s ease',
          cursor: 'pointer',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.borderColor = isRejected ? 'rgba(239,68,68,0.6)' : 'rgba(99,102,241,0.5)';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.borderColor = isRejected ? 'rgba(239,68,68,0.35)' : 'var(--color-border)';
        }}
      >
        {/* Card Top: Case type + status */}
        <div style={{ padding: '1.25rem 1.25rem 0.75rem', borderBottom: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{
                  fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em',
                  color: caseItem.case_type === 'CORRECTION' ? '#fbbf24' : '#60a5fa',
                }}>
                  {caseTypeLabel(caseItem.case_type)}
                </span>
                <span style={{ fontSize: 10, color: 'var(--color-text-dim)' }}>
                  · Opened {openedDate}
                </span>
              </div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-main)', lineHeight: 1.3 }}>
                {caseItem.case_subtype}
              </h3>
            </div>

            {/* Status Pill */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: statusCfg.dot, flexShrink: 0 }} />
              <span style={{
                fontSize: 11, fontWeight: 700, letterSpacing: '0.04em',
                color: statusCfg.pillText, background: statusCfg.pill,
                padding: '3px 10px', borderRadius: 999, whiteSpace: 'nowrap',
              }}>
                {statusCfg.label}
              </span>
            </div>
          </div>
        </div>

        {/* WHAT WE KNOW section */}
        <div style={{ padding: '0.875rem 1.25rem' }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--color-text-dim)', letterSpacing: '0.07em', textTransform: 'uppercase', marginBottom: 8 }}>
            WHAT WE KNOW
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
            {/* Official status */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
              <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>Current status</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: statusCfg.pillText }}>{statusCfg.label}</span>
                <SourceBadge source={statusSource} />
              </div>
            </div>

            {/* Official reason */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
              <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>Official reason</span>
              {caseItem.resolution_note ? (
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-main)', maxWidth: 200, textAlign: 'right' }}>
                  {caseItem.resolution_note}
                </span>
              ) : (
                <SourceBadge source="NOT_AVAILABLE" />
              )}
            </div>

            {/* Resolved date if applicable */}
            {resolvedDate && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>Last updated</span>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-main)' }}>{resolvedDate}</span>
              </div>
            )}
          </div>
        </div>

        {/* PF HEALTH CONNECTION — only shown when finding_id exists */}
        {hasHealthLink && (
          <div style={{
            margin: '0 1.25rem',
            padding: '0.75rem',
            background: 'rgba(245,158,11,0.06)',
            border: '1px solid rgba(245,158,11,0.2)',
            borderRadius: 8,
            marginBottom: '0.875rem',
          }}>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.07em', textTransform: 'uppercase', color: '#f59e0b', marginBottom: 4 }}>
              POSSIBLE CONTRIBUTING FACTOR
            </div>
            <p style={{ fontSize: 12, color: '#fde68a', margin: 0, lineHeight: 1.5 }}>
              ⚠ PF Health identified a related issue (PFH-001).
            </p>
            <p style={{ fontSize: 11, color: '#92400e', marginTop: 3 }}>
              This may be relevant, but EPFO has not confirmed it as the official reason.
            </p>
          </div>
        )}

        {/* Footer */}
        <div style={{
          padding: '0.625rem 1.25rem',
          borderTop: '1px solid var(--color-border)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <span style={{ fontSize: 11, color: 'var(--color-text-dim)' }}>
            {caseItem.event_count} recorded event{caseItem.event_count !== 1 ? 's' : ''}
          </span>
          <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-primary)' }}>
            View case →
          </span>
        </div>
      </div>
    </Link>
  );
};
