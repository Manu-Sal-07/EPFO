import React, { useState } from 'react';
import Link from 'next/link';
import { explainFinding, FindingExplanation } from '@/lib/api';

export interface HealthFindingData {
  id: string;
  rule_id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO' | string;
  status: string;
  what_is_wrong: string;
  why_it_happened: string;
  potential_impact: string;
  correction_path: {
    summary: string;
    form_numbers: string[];
    estimated_days: number;
    steps: string[];
  };
  evidence: Array<{
    field: string;
    expected: string;
    actual: string;
    source: string;
    description: string;
  }>;
  detected_at: string;
}

interface Props {
  finding: HealthFindingData;
}

export function FindingCard({ finding }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<FindingExplanation | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const handleAiExplain = async () => {
    if (aiExplanation) return;
    const token = localStorage.getItem('pf_token') || localStorage.getItem('token');
    if (!token) return;
    setAiLoading(true);
    try {
      const res = await explainFinding(token, finding.id);
      setAiExplanation(res);
    } catch (e) {
      console.error('AI explanation error:', e);
    } finally {
      setAiLoading(false);
    }
  };

  const getSeverityStyle = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL':
        return { bg: 'rgba(244, 63, 94, 0.1)', border: '#f43f5e', text: '#f43f5e' };
      case 'HIGH':
        return { bg: 'rgba(245, 158, 11, 0.1)', border: '#f59e0b', text: '#f59e0b' };
      case 'MEDIUM':
        return { bg: 'rgba(59, 130, 246, 0.1)', border: '#3b82f6', text: '#3b82f6' };
      default:
        return { bg: 'rgba(156, 163, 175, 0.1)', border: '#9ca3af', text: '#9ca3af' };
    }
  };

  const sevStyle = getSeverityStyle(finding.severity);

  return (
    <div style={{
      background: 'var(--color-surface)',
      border: `1px solid ${sevStyle.border}40`,
      borderLeft: `4px solid ${sevStyle.border}`,
      borderRadius: 'var(--radius-md)',
      padding: '1.5rem',
      marginBottom: '1.25rem',
      transition: 'all 0.2s ease'
    }}>
      {/* Header Badge & Rule ID */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: 700,
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            background: sevStyle.bg,
            color: sevStyle.text,
            border: `1px solid ${sevStyle.border}60`,
            letterSpacing: '0.05em'
          }}>
            {finding.severity}
          </span>
          <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--color-text-dim)' }}>
            Rule {finding.rule_id}
          </span>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>
          Status: <strong style={{ color: 'var(--color-text-main)' }}>{finding.status}</strong>
        </span>
      </div>

      {/* Principle 4: What is wrong? */}
      <div style={{ marginBottom: '0.75rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
          {finding.what_is_wrong}
        </h3>
      </div>

      {/* Principle 4: Why? */}
      {finding.why_it_happened && (
        <div style={{ marginBottom: '0.75rem', background: 'var(--color-bg)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-accent-amber)', display: 'block', marginBottom: '0.25rem' }}>WHY DID THIS HAPPEN?</span>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>{finding.why_it_happened}</p>
        </div>
      )}

      {/* Principle 4: Impact */}
      <div style={{ marginBottom: '1rem' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-accent-rose)', display: 'block', marginBottom: '0.25rem' }}>POTENTIAL IMPACT</span>
        <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>{finding.potential_impact}</p>
      </div>

      {/* Principle 4 & 5: Official Correction Path */}
      <div style={{ background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.2)', padding: '1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-primary)', letterSpacing: '0.05em' }}>OFFICIAL EPFO CORRECTION PATH</span>
          {finding.correction_path.estimated_days > 0 && (
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>Est. Time: ~{finding.correction_path.estimated_days} days</span>
          )}
        </div>
        <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '0.5rem' }}>
          {finding.correction_path.summary}
        </p>

        {finding.correction_path.form_numbers?.length > 0 && (
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {finding.correction_path.form_numbers.map((form) => (
              <span key={form} style={{ fontSize: '0.7rem', padding: '0.15rem 0.4rem', background: 'var(--color-surface)', border: '1px solid var(--color-border-bright)', borderRadius: '4px', color: 'var(--color-accent-teal)', fontFamily: 'monospace' }}>
                Official {form}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Evidence & AI Toggle Buttons */}
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button
          onClick={() => setExpanded(!expanded)}
          style={{ fontSize: '0.8rem', color: 'var(--color-primary)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}
        >
          {expanded ? '▲ Hide Audit Evidence' : '▼ View Audit Evidence & Steps'}
        </button>

        <button
          onClick={handleAiExplain}
          disabled={aiLoading}
          style={{
            fontSize: '0.75rem',
            background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(139,92,246,0.15) 100%)',
            border: '1px solid rgba(99,102,241,0.3)',
            borderRadius: '6px',
            color: '#a5b4fc',
            padding: '0.35rem 0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            marginLeft: 'auto',
          }}
        >
          {aiLoading ? '🤖 Generating AI Guide...' : '✨ Explain with AI Guide'}
        </button>
      </div>

      {/* AI Explanation Panel */}
      {aiExplanation && (
        <div style={{
          marginTop: '1rem',
          background: 'linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(30,41,59,0.9) 100%)',
          border: '1px solid rgba(99,102,241,0.35)',
          borderRadius: 'var(--radius-sm)',
          padding: '1.25rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.1rem' }}>🤖</span>
            <span style={{ fontSize: '0.825rem', fontWeight: 700, color: '#a5b4fc', letterSpacing: '0.05em' }}>AI CITIZEN EXPLANATION (GROQ LLAMA 3.3)</span>
          </div>

          <p style={{ fontSize: '0.875rem', color: '#e2e8f0', fontWeight: 600, marginBottom: '0.5rem' }}>
            {aiExplanation.plain_language_summary}
          </p>

          <p style={{ fontSize: '0.825rem', color: '#94a3b8', marginBottom: '0.75rem', lineHeight: 1.5 }}>
            {aiExplanation.what_this_means_for_you}
          </p>

          {aiExplanation.steps_to_fix.length > 0 && (
            <div style={{ marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#c7d2fe', display: 'block', marginBottom: '0.35rem' }}>RECOMMENDED ACTION STEPS</span>
              <ol style={{ paddingLeft: '1.25rem', fontSize: '0.8rem', color: '#cbd5e1' }}>
                {aiExplanation.steps_to_fix.map((step, idx) => (
                  <li key={idx} style={{ marginBottom: '0.25rem' }}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          {aiExplanation.source_references.length > 0 && (
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem', marginBottom: '0.75rem' }}>
              {aiExplanation.source_references.map((ref, idx) => (
                <span key={idx} style={{ fontSize: '0.7rem', padding: '0.15rem 0.4rem', background: 'rgba(99,102,241,0.15)', borderRadius: '4px', color: '#c7d2fe' }}>
                  📜 {ref}
                </span>
              ))}
            </div>
          )}

          {/* Action Buttons to navigate and resolve issue */}
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px dashed rgba(99,102,241,0.25)' }}>
            {finding.rule_id === 'PFH-004' ? (
              <Link href="/decision?type=PF_TRANSFER">
                <button style={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  color: '#fff',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}>
                  🔄 Initiate PF Transfer (Form 13) →
                </button>
              </Link>
            ) : finding.rule_id === 'PFH-002' ? (
              <Link href="/cases">
                <button style={{
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  color: '#fff',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}>
                  📋 Track Exit Date Correction Case →
                </button>
              </Link>
            ) : (
              <Link href="/decision">
                <button style={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: '#fff',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}>
                  🧭 Open Decision Engine →
                </button>
              </Link>
            )}

            <a
              href="https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
              target="_blank"
              rel="noopener noreferrer"
            >
              <button style={{
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.15)',
                color: '#e2e8f0',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}>
                🌐 Open EPFO Member Portal ↗
              </button>
            </a>
          </div>
        </div>
      )}

      {/* Expanded Audit Evidence */}
      {expanded && (
        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px dashed var(--color-border)' }}>
          <div style={{ marginBottom: '1rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-dim)', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'block' }}>Step-by-Step Resolution Guide</span>
            <ol style={{ paddingLeft: '1.25rem', fontSize: '0.825rem', color: 'var(--color-text-muted)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              {finding.correction_path.steps?.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ol>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-dim)', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'block' }}>Rule Engine Evidence Log</span>
            <div style={{ background: 'var(--color-bg)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', fontFamily: 'monospace', fontSize: '0.75rem' }}>
              {finding.evidence.map((ev, idx) => (
                <div key={idx} style={{ marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--color-accent-teal)' }}>[{ev.field}]</span> Expected: <span style={{ color: '#10b981' }}>{ev.expected}</span> | Actual: <span style={{ color: '#f43f5e' }}>{ev.actual}</span>
                  <div style={{ color: 'var(--color-text-dim)', fontSize: '0.7rem' }}>Source: {ev.source} — {ev.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
