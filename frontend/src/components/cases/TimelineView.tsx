'use client';

import React from 'react';

export interface TimelineItem {
  id: string;
  event_type: string;
  occurred_at: string;
  actor: string;
  actor_label: string;
  what_happened: string;
  why_it_happened?: string | null;
  status_change?: {
    from_status?: string | null;
    to_status?: string | null;
  } | null;
  evidence?: Record<string, any> | null;
  is_action_required: boolean;
}

// ── Source badge provenance ────────────────────────────────────────────────────
// Derives from CaseEvent.actor which is stored in the DB as actual provenance.
// CITIZEN = status update entered by the citizen from EPFO portal check
// EPFO    = would be a direct official EPFO system integration (rare in demo)
// SYSTEM  = PF Compass analysis / rule-engine derived event

type SourceType = 'CITIZEN' | 'EPFO' | 'PF_COMPASS' | 'SIMULATED';

function getSourceConfig(actor: string, eventType: string): {
  source: SourceType; label: string; color: string; bg: string; borderColor: string; dotColor: string;
} {
  const upper = actor.toUpperCase();
  if (upper === 'CITIZEN') {
    return {
      source: 'CITIZEN', label: '● Citizen provided',
      color: '#60a5fa', bg: 'rgba(59,130,246,0.08)',
      borderColor: 'rgba(59,130,246,0.2)', dotColor: '#3b82f6',
    };
  }
  if (upper === 'EPFO') {
    return {
      source: 'EPFO', label: '✓ EPFO official',
      color: '#10b981', bg: 'rgba(16,185,129,0.08)',
      borderColor: 'rgba(16,185,129,0.2)', dotColor: '#10b981',
    };
  }
  if (upper === 'EMPLOYER') {
    return {
      source: 'CITIZEN', label: '● Employer record',
      color: '#f59e0b', bg: 'rgba(245,158,11,0.08)',
      borderColor: 'rgba(245,158,11,0.2)', dotColor: '#f59e0b',
    };
  }
  // SYSTEM = PF Compass analysis
  return {
    source: 'PF_COMPASS', label: '◐ PF Compass analysis',
    color: '#a855f7', bg: 'rgba(168,85,247,0.08)',
    borderColor: 'rgba(168,85,247,0.2)', dotColor: '#a855f7',
  };
}

// ── Citizen-readable event type labels ────────────────────────────────────────
function readableEventType(eventType: string): string {
  const map: Record<string, string> = {
    CLAIM_SUBMITTED:        'Claim submitted',
    CASE_OPENED:            'Case started',
    STATUS_UPDATED:         'Status updated',
    DOCUMENT_REQUESTED:     'Document requested by field office',
    DOCUMENT_SUBMITTED:     'Document submitted',
    CORRECTION_REQUESTED:   'Correction request sent',
    CORRECTION_APPROVED:    'Correction approved',
    CLAIM_APPROVED:         'Claim approved',
    CLAIM_REJECTED:         'Claim rejected',
    CLAIM_SETTLED:          'Funds credited',
    GRIEVANCE_FILED:        'Grievance submitted',
    GRIEVANCE_RESOLVED:     'Grievance resolved',
    PF_COMPASS_ANALYSIS:    'PF Compass analysis added',
    EMPLOYER_VERIFICATION:  'Employer verification',
    EPFO_REVIEW:            'EPFO field office review',
  };
  return map[eventType] || eventType.replace(/_/g, ' ').toLowerCase().replace(/^./, c => c.toUpperCase());
}

// ── Readable status label ─────────────────────────────────────────────────────
function readableStatus(s?: string | null): string {
  if (!s) return '';
  const map: Record<string, string> = {
    SUBMITTED: 'Submitted', UNDER_REVIEW: 'Under Review',
    DOCUMENT_PENDING: 'Document Pending', APPROVED: 'Approved',
    SETTLED: 'Settled', REJECTED: 'Rejected', OPEN: 'Open',
    IN_CORRECTION: 'In Correction', PENDING_EPFO: 'Pending EPFO Review',
    RESOLVED: 'Resolved', DRAFT: 'Draft',
  };
  return map[s] || s.replace(/_/g, ' ');
}

// ── TimelineView ──────────────────────────────────────────────────────────────
export const TimelineView: React.FC<{ items: TimelineItem[] }> = ({ items }) => {
  if (!items || items.length === 0) {
    return (
      <div style={{ color: 'var(--color-text-dim)', textAlign: 'center', padding: '2rem' }}>
        No events recorded yet.
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      {items.map((item, index) => {
        const src = getSourceConfig(item.actor, item.event_type);
        const isLast = index === items.length - 1;
        const isPFCompassEvent = item.actor.toUpperCase() === 'SYSTEM';

        const date = new Date(item.occurred_at).toLocaleDateString('en-IN', {
          day: 'numeric', month: 'short', year: 'numeric',
        });
        const time = new Date(item.occurred_at).toLocaleTimeString('en-IN', {
          hour: '2-digit', minute: '2-digit',
        });

        return (
          <div key={item.id || index} style={{ display: 'flex', gap: '1rem', marginBottom: isLast ? 0 : '1.5rem' }}>
            {/* Timeline spine */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0, width: 20 }}>
              <div style={{
                width: 12, height: 12, borderRadius: '50%', flexShrink: 0,
                background: item.is_action_required ? '#ef4444' : src.dotColor,
                border: '2px solid var(--color-bg)',
                boxShadow: item.is_action_required ? '0 0 8px rgba(239,68,68,0.6)' : 'none',
                marginTop: 4,
              }} />
              {!isLast && (
                <div style={{ width: 1, flex: 1, background: 'var(--color-border)', marginTop: 4 }} />
              )}
            </div>

            {/* Event card */}
            <div style={{ flex: 1, paddingBottom: isLast ? 0 : '0.25rem' }}>
              {/* Date + source badge row */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6, flexWrap: 'wrap', gap: 6 }}>
                <span style={{ fontSize: 12, color: 'var(--color-text-dim)', fontWeight: 500 }}>
                  {date} · {time}
                </span>
                <span style={{
                  fontSize: 10, fontWeight: 700, letterSpacing: '0.05em',
                  color: src.color, background: src.bg,
                  padding: '2px 7px', borderRadius: 999,
                }}>
                  {src.label.toUpperCase()}
                </span>
              </div>

              <div style={{
                background: isPFCompassEvent ? 'rgba(168,85,247,0.06)' : 'var(--color-surface)',
                border: `1px solid ${item.is_action_required ? 'rgba(239,68,68,0.4)' : src.borderColor}`,
                borderRadius: 10,
                padding: '0.875rem 1rem',
              }}>
                {/* Event type label */}
                <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: src.color, marginBottom: 5 }}>
                  {readableEventType(item.event_type)}
                </div>

                {/* Main description */}
                <p style={{ color: 'var(--color-text-main)', fontSize: '0.9rem', lineHeight: 1.5, margin: 0, marginBottom: item.why_it_happened ? 6 : 0 }}>
                  {item.what_happened}
                </p>

                {/* Context / why */}
                {item.why_it_happened && (
                  <p style={{
                    fontSize: '0.825rem', color: 'var(--color-text-muted)',
                    lineHeight: 1.5, margin: 0,
                    paddingTop: 6, borderTop: '1px dashed var(--color-border)',
                    marginTop: 6,
                  }}>
                    {item.why_it_happened}
                  </p>
                )}

                {/* Status change */}
                {item.status_change && (item.status_change.from_status || item.status_change.to_status) && (
                  <div style={{
                    marginTop: 8, paddingTop: 6,
                    borderTop: '1px dashed var(--color-border)',
                    fontSize: 11, color: 'var(--color-text-dim)',
                    display: 'flex', alignItems: 'center', gap: 6,
                  }}>
                    <span>Status changed</span>
                    {item.status_change.from_status && (
                      <span style={{ textDecoration: 'line-through', opacity: 0.6 }}>
                        {readableStatus(item.status_change.from_status)}
                      </span>
                    )}
                    {item.status_change.to_status && (
                      <>
                        <span>→</span>
                        <span style={{ color: '#60a5fa', fontWeight: 700 }}>
                          {readableStatus(item.status_change.to_status)}
                        </span>
                      </>
                    )}
                  </div>
                )}

                {/* Action required flag */}
                {item.is_action_required && (
                  <div style={{
                    marginTop: 8, padding: '5px 8px',
                    background: 'rgba(239,68,68,0.1)', borderRadius: 6,
                    fontSize: 11, color: '#f87171', fontWeight: 700,
                  }}>
                    ⚡ Action required from you
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
