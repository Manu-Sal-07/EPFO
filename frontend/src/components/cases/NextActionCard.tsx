'use client';

import React from 'react';

export interface NextActionSet {
  primary_action: string;
  secondary_actions: string[];
  estimated_wait_days: number;
  can_citizen_act_now: boolean;
  action_url?: string | null;
}

export const NextActionCard: React.FC<{ nextActions: NextActionSet }> = ({ nextActions }) => {
  return (
    <div
      style={{
        background: nextActions.can_citizen_act_now
          ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(17, 24, 39, 0.9) 100%)'
          : 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(17, 24, 39, 0.9) 100%)',
        border: `1px solid ${nextActions.can_citizen_act_now ? 'rgba(245, 158, 11, 0.3)' : 'rgba(59, 130, 246, 0.3)'}`,
        borderRadius: 'var(--radius-md)',
        padding: '1.25rem 1.5rem',
        marginBottom: '2rem',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span
            style={{
              display: 'inline-block',
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: nextActions.can_citizen_act_now ? '#f59e0b' : '#3b82f6',
              boxShadow: nextActions.can_citizen_act_now ? '0 0 10px #f59e0b' : '0 0 10px #3b82f6',
            }}
          />
          <span style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: nextActions.can_citizen_act_now ? '#fbbf24' : '#60a5fa' }}>
            {nextActions.can_citizen_act_now ? 'Action Required From You' : 'Status & Next Step'}
          </span>
        </div>
        {nextActions.estimated_wait_days > 0 && (
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-dim)', background: 'rgba(0,0,0,0.3)', padding: '2px 8px', borderRadius: '4px' }}>
            Est. Turnaround: ~{nextActions.estimated_wait_days} day{nextActions.estimated_wait_days > 1 ? 's' : ''}
          </span>
        )}
      </div>

      <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '0.75rem' }}>
        {nextActions.primary_action}
      </h3>

      {nextActions.secondary_actions.length > 0 && (
        <ul style={{ paddingLeft: '1.2rem', margin: 0, color: 'var(--color-text-muted)', fontSize: '0.9rem', lineHeight: '1.6' }}>
          {nextActions.secondary_actions.map((tip, idx) => (
            <li key={idx}>{tip}</li>
          ))}
        </ul>
      )}

      {nextActions.can_citizen_act_now && nextActions.action_url && (
        <div style={{ marginTop: '1rem' }}>
          <a
            href={nextActions.action_url}
            target={nextActions.action_url.startsWith('http') ? '_blank' : '_self'}
            rel="noopener noreferrer"
            style={{
              display: 'inline-block',
              background: '#f59e0b',
              color: '#000',
              fontWeight: 600,
              fontSize: '0.875rem',
              padding: '0.5rem 1.25rem',
              borderRadius: 'var(--radius-sm)',
              textDecoration: 'none',
            }}
          >
            Take Action Now →
          </a>
        </div>
      )}
    </div>
  );
};
