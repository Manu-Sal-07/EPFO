'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { HealthScoreCard } from '@/components/health/HealthScoreCard';
import { FindingCard, HealthFindingData } from '@/components/health/FindingCard';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface HealthReport {
  citizen_id: string;
  display_name: string;
  health_score: number;
  health_status: string;
  total_balance: number;
  total_accounts: number;
  findings: HealthFindingData[];
}

export default function PFHealthPage() {
  const router = useRouter();
  const [report, setReport] = useState<HealthReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');

  useEffect(() => {
    const token = localStorage.getItem('pf_token');
    if (!token) {
      router.push('/');
      return;
    }

    fetch(`${API_BASE}/api/v1/health/report`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load PF Health report');
        return res.json();
      })
      .then((data) => {
        setReport(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [router]);

  const filteredFindings = report?.findings.filter((f) => {
    if (filterSeverity === 'ALL') return true;
    return f.severity.toUpperCase() === filterSeverity;
  }) || [];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <Navbar />

      <div className="container" style={{ padding: '2rem 1.5rem' }}>
        
        {/* Page Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)', padding: '0.25rem 0.75rem', borderRadius: '999px', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#10b981', letterSpacing: '0.05em' }}>🏥 RULE ENGINE DIAGNOSTICS</span>
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--color-text-main)', marginTop: '0.25rem' }}>
              PF HEALTH REPORT
            </h1>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              Deterministic diagnostic analysis of your linked EPFO accounts & employment records
            </p>
          </div>

          {report && (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>Citizen Profile</div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-main)' }}>{report.display_name}</div>
            </div>
          )}
        </div>

        {/* Loading / Error States */}
        {loading && (
          <div style={{ background: 'var(--color-surface)', padding: '3rem', borderRadius: 'var(--radius-lg)', textAlign: 'center', border: '1px solid var(--color-border)' }}>
            <div style={{ fontSize: '1.1rem', color: 'var(--color-primary)', fontWeight: 600 }}>Running Deterministic Rule Engine...</div>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginTop: '0.5rem' }}>Evaluating PF accounts, employment records, UANs, and KYC status</p>
          </div>
        )}

        {error && (
          <div style={{ background: 'rgba(244, 63, 94, 0.1)', border: '1px solid #f43f5e', padding: '1.5rem', borderRadius: 'var(--radius-md)', color: '#f43f5e' }}>
            <strong>Unable to generate health report:</strong> {error}
          </div>
        )}

        {/* Report Content */}
        {report && (
          <>
            {/* Score Card */}
            <HealthScoreCard
              score={report.health_score}
              status={report.health_status}
              totalBalance={report.total_balance}
              totalAccounts={report.total_accounts}
              findingCount={report.findings.length}
            />

            {/* Filter Tabs */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text-main)' }}>
                Detected Issue Breakdown ({report.findings.length})
              </h2>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setFilterSeverity(sev)}
                    style={{
                      padding: '0.35rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      background: filterSeverity === sev ? 'var(--color-primary)' : 'var(--color-surface)',
                      color: filterSeverity === sev ? '#fff' : 'var(--color-text-muted)',
                      border: '1px solid var(--color-border)',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>

            {/* Findings List */}
            {filteredFindings.length === 0 ? (
              <div style={{ background: 'var(--color-surface)', padding: '3rem', borderRadius: 'var(--radius-lg)', textAlign: 'center', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🎉</div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#10b981' }}>No Issues Found</h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                  Your PF records pass all active health rule checks.
                </p>
              </div>
            ) : (
              <div>
                {filteredFindings.map((finding) => (
                  <FindingCard key={finding.id} finding={finding} />
                ))}
              </div>
            )}
          </>
        )}

      </div>
    </div>
  );
}
