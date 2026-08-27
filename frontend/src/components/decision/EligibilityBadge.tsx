'use client';

import { useState } from 'react';
import Link from 'next/link';
import { EligibilityResult, explainDecision, DecisionExplanation } from '@/lib/api';

interface Props {
  result: EligibilityResult;
}

const STATUS_CONFIG = {
  ELIGIBLE: {
    bg: 'linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(5,150,105,0.08) 100%)',
    border: '#10b981',
    pill: 'rgba(16,185,129,0.2)',
    pillText: '#6ee7b7',
    icon: '✅',
    label: 'ELIGIBLE',
  },
  CONDITIONALLY_ELIGIBLE: {
    bg: 'linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(217,119,6,0.08) 100%)',
    border: '#f59e0b',
    pill: 'rgba(245,158,11,0.2)',
    pillText: '#fde68a',
    icon: '⚠️',
    label: 'CONDITIONALLY ELIGIBLE',
  },
  INELIGIBLE: {
    bg: 'linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(185,28,28,0.08) 100%)',
    border: '#ef4444',
    pill: 'rgba(239,68,68,0.2)',
    pillText: '#fca5a5',
    icon: '❌',
    label: 'INELIGIBLE',
  },
} as const;

export default function EligibilityBadge({ result }: Props) {
  const cfg = STATUS_CONFIG[result.status] ?? STATUS_CONFIG.INELIGIBLE;

  const [aiExplanation, setAiExplanation] = useState<DecisionExplanation | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const handleAiExplain = async () => {
    if (aiExplanation) return;
    const token = localStorage.getItem('pf_token') || localStorage.getItem('token');
    if (!token) return;
    setAiLoading(true);
    try {
      const res = await explainDecision(token, result.claim_type);
      setAiExplanation(res);
    } catch (e) {
      console.error('AI explanation error:', e);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div
      style={{
        background: cfg.bg,
        border: `1.5px solid ${cfg.border}`,
        borderRadius: 16,
        padding: '24px',
        marginTop: 16,
      }}
    >
      {/* Status Pill */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <span style={{ fontSize: 28 }}>{cfg.icon}</span>
        <span
          style={{
            background: cfg.pill,
            color: cfg.pillText,
            borderRadius: 999,
            padding: '4px 16px',
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
          }}
        >
          {cfg.label}
        </span>
        <span style={{ color: '#94a3b8', fontSize: 13, marginLeft: 'auto' }}>
          {result.rule_id} · {result.form_number}
        </span>
      </div>

      {/* Summary */}
      <p style={{ color: '#e2e8f0', fontSize: 15, marginBottom: 8, fontWeight: 500 }}>
        {result.what_is_wrong}
      </p>
      <p style={{ color: '#94a3b8', fontSize: 13, marginBottom: 16, lineHeight: 1.6 }}>
        {result.why_it_happened}
      </p>

      {/* Reasons */}
      {result.reasons.length > 0 && (
        <ul style={{ paddingLeft: 20, marginBottom: 16 }}>
          {result.reasons.map((r, i) => (
            <li key={i} style={{ color: '#fca5a5', fontSize: 13, marginBottom: 6, lineHeight: 1.5 }}>
              {r}
            </li>
          ))}
        </ul>
      )}

      {/* Recommended Action Box */}
      <div
        style={{
          background: 'rgba(99,102,241,0.12)',
          border: '1px solid rgba(99,102,241,0.25)',
          borderRadius: 10,
          padding: '12px 16px',
          marginBottom: 16,
        }}
      >
        <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginBottom: 12 }}>
          <span style={{ fontSize: 16 }}>🎯</span>
          <span style={{ color: '#c7d2fe', fontSize: 13, lineHeight: 1.5, fontWeight: 600 }}>
            {result.recommended_action}
          </span>
        </div>

        {/* Action Buttons to navigate and clarify/resolve issue */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {result.claim_type !== 'PF_TRANSFER' && (
            <Link href="/decision?type=PF_TRANSFER">
              <button style={{
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                color: '#fff',
                padding: '6px 14px',
                borderRadius: 8,
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
              }}>
                🔄 Switch to PF Transfer (Form 13) →
              </button>
            </Link>
          )}

          <Link href="/health">
            <button style={{
              background: 'rgba(16,185,129,0.18)',
              border: '1px solid rgba(16,185,129,0.35)',
              color: '#6ee7b7',
              padding: '6px 14px',
              borderRadius: 8,
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
            }}>
              🏥 Inspect Record in PF Health →
            </button>
          </Link>

          <Link href="/cases">
            <button style={{
              background: 'rgba(59,130,246,0.18)',
              border: '1px solid rgba(59,130,246,0.35)',
              color: '#60a5fa',
              padding: '6px 14px',
              borderRadius: 8,
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
            }}>
              📋 View CaseWise Tracker →
            </button>
          </Link>
        </div>
      </div>

      {/* AI Explain Button */}
      <button
        onClick={handleAiExplain}
        disabled={aiLoading}
        style={{
          width: '100%',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(139,92,246,0.18) 100%)',
          border: '1px solid rgba(99,102,241,0.4)',
          borderRadius: 10,
          color: '#c7d2fe',
          padding: '10px',
          fontSize: 13,
          fontWeight: 700,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          transition: 'all 0.2s',
        }}
      >
        {aiLoading ? '🤖 Generating AI Decision Explanation...' : '✨ Explain Decision with AI (Groq Llama 3.3)'}
      </button>

      {/* AI Explanation Result */}
      {aiExplanation && (
        <div
          style={{
            marginTop: 16,
            background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.95) 100%)',
            border: '1.5px solid rgba(99,102,241,0.4)',
            borderRadius: 12,
            padding: '18px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <span style={{ fontSize: 20 }}>🤖</span>
            <span style={{ fontSize: 13, fontWeight: 700, color: '#a5b4fc', letterSpacing: '0.05em' }}>
              AI CITIZEN EXPLANATION (GROQ LLAMA 3.3)
            </span>
          </div>
          <p style={{ color: '#f8fafc', fontSize: 14, fontWeight: 600, marginBottom: 8, lineHeight: 1.5 }}>
            {aiExplanation.plain_language_summary}
          </p>
          <p style={{ color: '#cbd5e1', fontSize: 13, marginBottom: 10, lineHeight: 1.6 }}>
            {aiExplanation.why_eligible_or_not}
          </p>

          <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 8, padding: '10px 12px', marginBottom: 12 }}>
            <span style={{ color: '#6ee7b7', fontSize: 12, fontWeight: 700, display: 'block', marginBottom: 2 }}>NEXT STEP</span>
            <span style={{ color: '#e2e8f0', fontSize: 13 }}>{aiExplanation.what_happens_next}</span>
          </div>

          {/* Action Buttons to navigate from AI insight */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <a
              href="https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
              target="_blank"
              rel="noopener noreferrer"
            >
              <button style={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: '#fff',
                padding: '6px 14px',
                borderRadius: 8,
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
              }}>
                🌐 Take Action on EPFO Member Portal ↗
              </button>
            </a>
            <Link href="/cases">
              <button style={{
                background: 'rgba(99,102,241,0.2)',
                border: '1px solid rgba(99,102,241,0.4)',
                color: '#a5b4fc',
                padding: '6px 14px',
                borderRadius: 8,
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
              }}>
                📋 Track Progress in CaseWise →
              </button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
