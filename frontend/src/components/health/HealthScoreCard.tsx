import React from 'react';

interface Props {
  score: number;
  status: string;
  totalBalance: number;
  totalAccounts: number;
  findingCount: number;
}

export function HealthScoreCard({ score, status, totalBalance, totalAccounts, findingCount }: Props) {
  const getScoreColor = (s: number) => {
    if (s >= 80) return '#10b981';
    if (s >= 50) return '#f59e0b';
    return '#f43f5e';
  };

  const scoreColor = getScoreColor(score);

  return (
    <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '2rem', marginBottom: '2rem', boxShadow: 'var(--shadow-card)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '2rem', alignItems: 'center' }}>
        
        {/* Score Dial */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{
            width: '100px',
            height: '100px',
            borderRadius: '50%',
            border: `6px solid ${scoreColor}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '2rem',
            fontWeight: 800,
            color: scoreColor,
            boxShadow: `0 0 20px ${scoreColor}33`
          }}>
            {score}
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-dim)' }}>PF Health Score</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text-main)', marginTop: '0.25rem' }}>
              {status === 'HEALTHY' ? 'Healthy Record' : status === 'ATTENTION_NEEDED' ? 'Attention Needed' : 'Action Required'}
            </div>
            <div style={{ fontSize: '0.825rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
              {findingCount === 0 ? 'No open issues detected across your accounts.' : `${findingCount} active issue(s) require official correction.`}
            </div>
          </div>
        </div>

        {/* Financial Summary */}
        <div style={{ borderLeft: '1px solid var(--color-border)', paddingLeft: '2rem' }}>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-dim)' }}>Total Tracked PF Balance</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--color-accent-teal)', marginTop: '0.25rem' }}>
            ₹{totalBalance.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '0.825rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
            Across {totalAccounts} linked PF member account(s)
          </div>
        </div>

      </div>
    </div>
  );
}
