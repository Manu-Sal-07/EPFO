'use client';

import { CalculationResult } from '@/lib/api';

function fmt(n: number) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);
}

interface Props {
  result: CalculationResult;
}

export default function CalculationSummaryCard({ result }: Props) {
  const taxColor = result.is_tax_free ? '#10b981' : '#f59e0b';

  return (
    <div
      style={{
        background: 'linear-gradient(135deg, rgba(15,23,42,0.8) 0%, rgba(30,41,59,0.8) 100%)',
        border: '1px solid rgba(99,102,241,0.3)',
        borderRadius: 16,
        padding: '24px',
        marginTop: 16,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
        <span style={{ fontSize: 24 }}>💰</span>
        <h3 style={{ color: '#e2e8f0', fontSize: 17, fontWeight: 700, margin: 0 }}>
          Payout & Tax Estimate
        </h3>
        <span
          style={{
            marginLeft: 'auto',
            background: result.is_tax_free ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
            color: taxColor,
            borderRadius: 999,
            padding: '3px 12px',
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: '0.06em',
          }}
        >
          {result.is_tax_free ? 'TAX FREE' : `TDS ${result.tds_rate_percent}%`}
        </span>
      </div>

      {/* Balance Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 20 }}>
        {[
          { label: 'Employee Share', value: result.employee_share, icon: '👤' },
          { label: 'Employer Share', value: result.employer_share, icon: '🏢' },
          { label: 'Interest Accrued', value: result.interest_accrued, icon: '📈' },
        ].map(({ label, value, icon }) => (
          <div
            key={label}
            style={{
              background: 'rgba(99,102,241,0.08)',
              border: '1px solid rgba(99,102,241,0.15)',
              borderRadius: 10,
              padding: '12px 14px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 20, marginBottom: 4 }}>{icon}</div>
            <div style={{ color: '#a5b4fc', fontSize: 13, fontWeight: 600 }}>{fmt(value)}</div>
            <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Payout and Service */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
        <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 12, padding: 16 }}>
          <div style={{ color: '#64748b', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
            Eligible Payout
          </div>
          <div style={{ color: '#6ee7b7', fontSize: 24, fontWeight: 800 }}>{fmt(result.eligible_payout_amount)}</div>
          <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 4 }}>Estimated gross amount</div>
        </div>
        <div style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)', borderRadius: 12, padding: 16 }}>
          <div style={{ color: '#64748b', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
            Total Service
          </div>
          <div style={{ color: '#c7d2fe', fontSize: 24, fontWeight: 800 }}>{result.total_service_years} yrs</div>
          <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 4 }}>Combined across employers</div>
        </div>
      </div>

      {/* TDS Row */}
      {result.estimated_tds_amount > 0 && (
        <div
          style={{
            background: 'rgba(239,68,68,0.08)',
            border: '1px solid rgba(239,68,68,0.2)',
            borderRadius: 10,
            padding: '10px 14px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 16,
          }}
        >
          <span style={{ color: '#fca5a5', fontSize: 13 }}>
            Estimated TDS @ {result.tds_rate_percent}%
          </span>
          <span style={{ color: '#f87171', fontWeight: 700, fontSize: 15 }}>
            − {fmt(result.estimated_tds_amount)}
          </span>
        </div>
      )}

      {/* Net Payout */}
      <div
        style={{
          background: 'rgba(16,185,129,0.12)',
          border: '1.5px solid rgba(16,185,129,0.3)',
          borderRadius: 12,
          padding: '14px 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <span style={{ color: '#e2e8f0', fontWeight: 600 }}>Estimated Net Payout</span>
        <span style={{ color: '#6ee7b7', fontWeight: 800, fontSize: 20 }}>
          {fmt(result.eligible_payout_amount - result.estimated_tds_amount)}
        </span>
      </div>

      {/* Tax Reasoning */}
      <div
        style={{
          background: 'rgba(99,102,241,0.08)',
          border: '1px solid rgba(99,102,241,0.15)',
          borderRadius: 10,
          padding: '12px 14px',
        }}
      >
        <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginBottom: result.form_15g_applicable ? 10 : 0 }}>
          <span style={{ fontSize: 16 }}>⚖️</span>
          <span style={{ color: '#94a3b8', fontSize: 12, lineHeight: 1.6 }}>{result.taxability_reason}</span>
        </div>
        {result.form_15g_applicable && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginTop: 8, paddingTop: 8, borderTop: '1px solid rgba(99,102,241,0.15)' }}>
            <span style={{ fontSize: 14 }}>📋</span>
            <span style={{ color: '#fde68a', fontSize: 12, lineHeight: 1.6 }}>{result.form_15g_recommendation}</span>
          </div>
        )}
      </div>
    </div>
  );
}
