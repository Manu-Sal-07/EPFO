'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { PreSubmitResult } from '@/lib/api';

interface Props {
  result: PreSubmitResult;
}

const STATUS_ICON: Record<string, string> = {
  PASSED: '✅',
  FAILED: '❌',
  WARNING: '⚠️',
};
const STATUS_COLOR: Record<string, string> = {
  PASSED: '#10b981',
  FAILED: '#ef4444',
  WARNING: '#f59e0b',
};
const STATUS_BG: Record<string, string> = {
  PASSED: 'rgba(16,185,129,0.1)',
  FAILED: 'rgba(239,68,68,0.1)',
  WARNING: 'rgba(245,158,11,0.1)',
};

export default function PreSubmitChecklist({ result }: Props) {
  // Real-time animation states
  const [animating, setAnimating] = useState(true);
  const [visibleItemsCount, setVisibleItemsCount] = useState(0);
  const [currentScore, setCurrentScore] = useState(0);

  const totalItems = result.check_items.length;

  useEffect(() => {
    setAnimating(true);
    setVisibleItemsCount(0);
    setCurrentScore(0);

    let stage = 0;
    const interval = setInterval(() => {
      stage++;
      if (stage <= totalItems) {
        setVisibleItemsCount(stage);
        // Calculate intermediate score up to this stage
        const subset = result.check_items.slice(0, stage);
        const passedCount = subset.filter(i => i.status === 'PASSED').length;
        const targetPartialScore = Math.round((passedCount / totalItems) * 100);
        setCurrentScore(targetPartialScore);
      } else {
        clearInterval(interval);
        setAnimating(false);
        setCurrentScore(result.readiness_score);
      }
    }, 450); // Advance each stage every 450ms

    return () => clearInterval(interval);
  }, [result]);

  const scoreColor = currentScore >= 80 ? '#10b981' : currentScore >= 50 ? '#f59e0b' : '#ef4444';
  const circumference = 2 * Math.PI * 28;
  const dashOffset = circumference - (currentScore / 100) * circumference;

  return (
    <div
      style={{
        background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.95) 100%)',
        border: `1.5px solid ${!animating && result.is_ready_to_submit ? 'rgba(16,185,129,0.4)' : 'rgba(239,68,68,0.4)'}`,
        borderRadius: 16,
        padding: '24px',
        marginTop: 16,
        boxShadow: '0 20px 30px -10px rgba(0,0,0,0.5)',
      }}
    >
      {/* Real-time Audit Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
        {/* Animated Score Ring */}
        <div style={{ position: 'relative', width: 72, height: 72, flexShrink: 0 }}>
          <svg width="72" height="72" viewBox="0 0 72 72" style={{ transform: 'rotate(-90deg)' }}>
            <circle cx="36" cy="36" r="28" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6" />
            <circle
              cx="36" cy="36" r="28"
              fill="none"
              stroke={scoreColor}
              strokeWidth="6"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              style={{ transition: 'stroke-dashoffset 0.4s ease, stroke 0.4s ease' }}
            />
          </svg>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: scoreColor, fontSize: 16, fontWeight: 800 }}>{currentScore}%</span>
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <h3 style={{ color: '#e2e8f0', fontSize: 17, fontWeight: 700, margin: 0 }}>
              Pre-Submit Readiness Audit
            </h3>
            {animating && (
              <span style={{
                fontSize: 11,
                fontWeight: 700,
                color: '#60a5fa',
                background: 'rgba(59,130,246,0.15)',
                padding: '2px 8px',
                borderRadius: 999,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 4
              }}>
                <span className="pulse-dot">⚡</span> AUDITING LIVE...
              </span>
            )}
          </div>
          <p style={{ color: '#64748b', fontSize: 13, margin: 0 }}>
            {visibleItemsCount}/{totalItems} checks completed
            {!animating && result.blocking_issues_count > 0 && (
              <span style={{ color: '#fca5a5', marginLeft: 8 }}>
                · {result.blocking_issues_count} blocking issue{result.blocking_issues_count > 1 ? 's' : ''}
              </span>
            )}
          </p>
        </div>

        {!animating && (
          <div
            style={{
              background: result.is_ready_to_submit ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
              color: result.is_ready_to_submit ? '#6ee7b7' : '#fca5a5',
              borderRadius: 999,
              padding: '5px 14px',
              fontSize: 12,
              fontWeight: 700,
            }}
          >
            {result.is_ready_to_submit ? 'READY' : 'NOT READY'}
          </div>
        )}
      </div>

      {/* Stage-by-Stage Scanning Animation List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {result.check_items.map((item, idx) => {
          const isVisible = idx < visibleItemsCount;
          const isScanningCurrently = idx === visibleItemsCount - 1 && animating;

          if (!isVisible) {
            return (
              <div
                key={item.check_id}
                style={{
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px border rgba(255,255,255,0.05)',
                  borderRadius: 10,
                  padding: '12px 14px',
                  opacity: 0.3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                }}
              >
                <span style={{ fontSize: 14, color: '#475569' }}>⏳</span>
                <span style={{ color: '#475569', fontSize: 13 }}>Stage {idx + 1}: Waiting to scan {item.title}...</span>
              </div>
            );
          }

          return (
            <div
              key={item.check_id}
              style={{
                background: STATUS_BG[item.status] || 'rgba(255,255,255,0.03)',
                border: `1px solid ${STATUS_COLOR[item.status]}30`,
                borderRadius: 10,
                padding: '12px 14px',
                transition: 'all 0.3s ease',
                animation: 'fadeIn 0.3s ease-in',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: item.status !== 'PASSED' ? 8 : 0 }}>
                <span style={{ fontSize: 18 }}>{STATUS_ICON[item.status]}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600 }}>{item.title}</span>
                    {item.is_blocking && item.status === 'FAILED' && (
                      <span
                        style={{
                          background: 'rgba(239,68,68,0.2)',
                          color: '#fca5a5',
                          borderRadius: 999,
                          padding: '1px 8px',
                          fontSize: 10,
                          fontWeight: 700,
                          letterSpacing: '0.06em',
                        }}
                      >
                        BLOCKING
                      </span>
                    )}
                  </div>
                  <span style={{ color: '#64748b', fontSize: 12 }}>{item.description}</span>
                </div>
              </div>

              {/* Remediation Hint & Navigation Resolution Buttons */}
              {item.status !== 'PASSED' && (
                <div
                  style={{
                    marginTop: 6,
                    paddingTop: 8,
                    borderTop: `1px solid ${STATUS_COLOR[item.status]}20`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 8,
                  }}
                >
                  <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                    <span style={{ fontSize: 13 }}>💡</span>
                    <span style={{ color: '#cbd5e1', fontSize: 12, lineHeight: 1.5 }}>{item.remediation_hint}</span>
                  </div>

                  {/* Resolution Buttons to Clarify & Fix Issue */}
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 4 }}>
                    {item.check_id.includes('EXIT') || item.title.includes('Exit') ? (
                      <>
                        <Link href="/cases">
                          <button style={{
                            padding: '6px 12px',
                            background: 'rgba(59,130,246,0.15)',
                            border: '1px solid rgba(59,130,246,0.3)',
                            borderRadius: 6,
                            color: '#60a5fa',
                            fontSize: 12,
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}>
                            📋 View Exit Date Correction Case →
                          </button>
                        </Link>
                        <a
                          href="https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <button style={{
                            padding: '6px 12px',
                            background: 'rgba(16,185,129,0.15)',
                            border: '1px solid rgba(16,185,129,0.3)',
                            borderRadius: 6,
                            color: '#6ee7b7',
                            fontSize: 12,
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}>
                            🌐 Mark Exit on EPFO Portal ↗
                          </button>
                        </a>
                      </>
                    ) : item.check_id.includes('UAN') || item.title.includes('UAN') ? (
                      <>
                        <Link href="/decision?type=PF_TRANSFER">
                          <button style={{
                            padding: '6px 12px',
                            background: 'rgba(139,92,246,0.15)',
                            border: '1px solid rgba(139,92,246,0.3)',
                            borderRadius: 6,
                            color: '#c084fc',
                            fontSize: 12,
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}>
                            🔄 Apply for PF Transfer (Form 13) →
                          </button>
                        </Link>
                        <Link href="/health">
                          <button style={{
                            padding: '6px 12px',
                            background: 'rgba(245,158,11,0.15)',
                            border: '1px solid rgba(245,158,11,0.3)',
                            borderRadius: 6,
                            color: '#fcd34d',
                            fontSize: 12,
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}>
                            🏥 Resolve Duplicate UAN in Health Audit →
                          </button>
                        </Link>
                      </>
                    ) : (
                      <a
                        href="https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <button style={{
                          padding: '6px 12px',
                          background: 'rgba(99,102,241,0.15)',
                          border: '1px solid rgba(99,102,241,0.3)',
                          borderRadius: 6,
                          color: '#a5b4fc',
                          fontSize: 12,
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}>
                          🌐 Fix KYC on Unified Member Portal ↗
                        </button>
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
