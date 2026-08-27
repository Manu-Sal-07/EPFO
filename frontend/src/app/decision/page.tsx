'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import {
  EligibilityResult,
  CalculationResult,
  PreSubmitResult,
  DecisionExplanation,
  evaluateEligibility,
  calculatePayout,
  runPreSubmitAudit,
  explainDecision,
} from '@/lib/api';
import EligibilityBadge from '@/components/decision/EligibilityBadge';
import CalculationSummaryCard from '@/components/decision/CalculationSummaryCard';
import PreSubmitChecklist from '@/components/decision/PreSubmitChecklist';

// ── Types & Constants ─────────────────────────────────────────────────────────

type ClaimType = 'FULL_WITHDRAWAL' | 'PARTIAL_ADVANCE' | 'PENSION_CLAIM' | 'PF_TRANSFER';
type AdvanceGround = 'ILLNESS' | 'MARRIAGE' | 'EDUCATION' | 'HOUSE' | 'PANDEMIC';

const CLAIM_OPTIONS: { type: ClaimType; label: string; desc: string; form: string; icon: string }[] = [
  { type: 'FULL_WITHDRAWAL', label: 'Full PF Withdrawal', desc: 'Claim entire PF corpus after leaving employment', form: 'Form 19', icon: '🏧' },
  { type: 'PARTIAL_ADVANCE', label: 'Partial Advance', desc: 'Emergency advance without exiting service', form: 'Form 31', icon: '💳' },
  { type: 'PENSION_CLAIM', label: 'Pension Benefit', desc: 'Pension withdrawal or scheme certificate (EPS)', form: 'Form 10C', icon: '🏦' },
  { type: 'PF_TRANSFER', label: 'PF Transfer', desc: 'Consolidate previous accounts to current employer', form: 'Form 13', icon: '🔄' },
];

const ADVANCE_GROUNDS: { ground: AdvanceGround; label: string; minYears: number; para: string }[] = [
  { ground: 'ILLNESS', label: 'Illness / Medical', minYears: 0, para: 'Para 68J' },
  { ground: 'MARRIAGE', label: 'Marriage / Education', minYears: 7, para: 'Para 68K' },
  { ground: 'EDUCATION', label: 'Children Education', minYears: 7, para: 'Para 68K' },
  { ground: 'HOUSE', label: 'House Purchase / Construction', minYears: 5, para: 'Para 68B' },
  { ground: 'PANDEMIC', label: 'Pandemic Emergency', minYears: 0, para: 'Para 68L' },
];

const STEPS = ['Select Goal', 'Check Eligibility', 'View Calculation', 'Pre-Submit Audit'];

// ── Page Component ────────────────────────────────────────────────────────────

function DecisionPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [step, setStep] = useState(0);
  const [token, setToken] = useState<string | null>(null);

  // Step 1
  const [claimType, setClaimType] = useState<ClaimType | null>(() => {
    const queryType = searchParams?.get('type');
    if (queryType && ['FULL_WITHDRAWAL', 'PARTIAL_ADVANCE', 'PENSION_CLAIM', 'PF_TRANSFER'].includes(queryType)) {
      return queryType as ClaimType;
    }
    return null;
  });
  const [advanceGround, setAdvanceGround] = useState<AdvanceGround>('ILLNESS');
  
  // User Inputs (interactive, not static)
  const [requestedAmount, setRequestedAmount] = useState<string>('');
  const [hasPan, setHasPan] = useState<boolean>(true);

  // Step 2
  const [eligibility, setEligibility] = useState<EligibilityResult | null>(null);
  // Step 3
  const [calculation, setCalculation] = useState<CalculationResult | null>(null);
  // Step 4
  const [preSubmit, setPreSubmit] = useState<PreSubmitResult | null>(null);
  
  // AI Explanation
  const [aiExplanation, setAiExplanation] = useState<DecisionExplanation | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem('pf_token') || localStorage.getItem('token');
    if (!t) { router.push('/'); return; }
    setToken(t);
  }, [router]);

  async function handleCheckEligibility() {
    if (!claimType || !token) return;
    setLoading(true);
    setError(null);
    setAiExplanation(null);
    try {
      const ground = claimType === 'PARTIAL_ADVANCE' ? advanceGround : undefined;
      const res = await evaluateEligibility(token, claimType, ground);
      setEligibility(res);
      setStep(1);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Eligibility check failed');
    } finally {
      setLoading(false);
    }
  }

  async function handleAiExplain() {
    if (!claimType || !token) return;
    setAiLoading(true);
    try {
      const ground = claimType === 'PARTIAL_ADVANCE' ? advanceGround : undefined;
      const res = await explainDecision(token, claimType, ground);
      setAiExplanation(res);
    } catch (e: unknown) {
      console.error('AI explain error:', e);
    } finally {
      setAiLoading(false);
    }
  }

  async function handleCalculate() {
    if (!claimType || !token) return;
    setLoading(true);
    setError(null);
    try {
      const ground = claimType === 'PARTIAL_ADVANCE' ? advanceGround : undefined;
      const amount = requestedAmount ? parseFloat(requestedAmount) : undefined;
      const res = await calculatePayout(token, claimType, ground, amount, hasPan);
      setCalculation(res);
      setStep(2);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Calculation failed');
    } finally {
      setLoading(false);
    }
  }

  async function handlePreSubmit() {
    if (!claimType || !token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await runPreSubmitAudit(token, claimType);
      setPreSubmit(res);
      setStep(3);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Pre-submit audit failed');
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setStep(0);
    setClaimType(null);
    setEligibility(null);
    setCalculation(null);
    setPreSubmit(null);
    setAiExplanation(null);
    setRequestedAmount('');
    setHasPan(true);
    setError(null);
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0a0f1e 0%, #0f172a 50%, #1a0a2e 100%)', fontFamily: "'Inter', sans-serif" }}>
      <Navbar />

      <main style={{ maxWidth: 760, margin: '0 auto', padding: '40px 24px' }}>
        {/* Title */}
        <div style={{ marginBottom: 36 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', borderRadius: 999, padding: '4px 14px', marginBottom: 14 }}>
            <span style={{ fontSize: 14 }}>🧭</span>
            <span style={{ color: '#a5b4fc', fontSize: 12, fontWeight: 600, letterSpacing: '0.08em' }}>PF DECISION WIZARD</span>
          </div>
          <h1 style={{ color: '#f8fafc', fontSize: 32, fontWeight: 800, margin: '0 0 8px', lineHeight: 1.2 }}>
            What's your PF goal?
          </h1>
          <p style={{ color: '#64748b', fontSize: 15, margin: 0 }}>
            Get deterministic eligibility evaluation, payout estimates, and a pre-submit readiness check — all rule-based, with real AI recommendations.
          </p>
        </div>

        {/* Step Indicator */}
        <div style={{ display: 'flex', gap: 0, marginBottom: 36, borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(99,102,241,0.2)' }}>
          {STEPS.map((s, i) => (
            <div
              key={s}
              style={{
                flex: 1,
                padding: '10px 6px',
                textAlign: 'center',
                background: i === step ? 'rgba(99,102,241,0.25)' : i < step ? 'rgba(16,185,129,0.12)' : 'rgba(255,255,255,0.02)',
                borderRight: i < STEPS.length - 1 ? '1px solid rgba(99,102,241,0.15)' : 'none',
                transition: 'background 0.3s',
              }}
            >
              <div style={{ fontSize: 11, fontWeight: 700, color: i === step ? '#a5b4fc' : i < step ? '#6ee7b7' : '#475569', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                {i < step ? '✓ ' : `${i + 1}. `}{s}
              </div>
            </div>
          ))}
        </div>

        {/* Error Banner */}
        {error && (
          <div style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, padding: '12px 16px', marginBottom: 20, color: '#fca5a5', fontSize: 13 }}>
            ⚠️ {error}
          </div>
        )}

        {/* ─── STEP 0: Goal Selection ─── */}
        {step === 0 && (
          <section>
            <h2 style={{ color: '#e2e8f0', fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Choose your claim type</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 24 }}>
              {CLAIM_OPTIONS.map(({ type, label, desc, form, icon }) => {
                const selected = claimType === type;
                return (
                  <button
                    key={type}
                    id={`claim-${type}`}
                    onClick={() => setClaimType(type)}
                    style={{
                      background: selected ? 'linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(139,92,246,0.15) 100%)' : 'rgba(255,255,255,0.03)',
                      border: `2px solid ${selected ? '#6366f1' : 'rgba(255,255,255,0.07)'}`,
                      borderRadius: 14,
                      padding: '18px 16px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.2s',
                    }}
                    onMouseEnter={e => { if (!selected) e.currentTarget.style.borderColor = 'rgba(99,102,241,0.4)'; }}
                    onMouseLeave={e => { if (!selected) e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'; }}
                  >
                    <div style={{ fontSize: 28, marginBottom: 8 }}>{icon}</div>
                    <div style={{ color: '#e2e8f0', fontSize: 15, fontWeight: 700, marginBottom: 4 }}>{label}</div>
                    <div style={{ color: '#64748b', fontSize: 12, marginBottom: 8, lineHeight: 1.5 }}>{desc}</div>
                    <div style={{ display: 'inline-block', background: 'rgba(99,102,241,0.12)', color: '#a5b4fc', borderRadius: 6, padding: '2px 8px', fontSize: 11, fontWeight: 600 }}>
                      {form}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Advance Ground (only for PARTIAL_ADVANCE) */}
            {claimType === 'PARTIAL_ADVANCE' && (
              <div style={{ background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 14, padding: 20, marginBottom: 24 }}>
                <h3 style={{ color: '#e2e8f0', fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Select Advance Ground</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {ADVANCE_GROUNDS.map(({ ground, label, minYears, para }) => (
                    <label
                      key={ground}
                      style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer', padding: '10px 12px', borderRadius: 10, background: advanceGround === ground ? 'rgba(99,102,241,0.15)' : 'transparent', transition: 'background 0.2s' }}
                    >
                      <input
                        type="radio"
                        name="advance_ground"
                        value={ground}
                        checked={advanceGround === ground}
                        onChange={() => setAdvanceGround(ground)}
                        style={{ accentColor: '#6366f1' }}
                      />
                      <span style={{ flex: 1, color: '#e2e8f0', fontSize: 14 }}>{label}</span>
                      <span style={{ color: '#475569', fontSize: 12 }}>{para}</span>
                      <span style={{ color: '#64748b', fontSize: 11 }}>{minYears === 0 ? 'Any service' : `${minYears}+ yrs`}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* ── User Input: Requested Amount ── */}
            {claimType && (claimType === 'PARTIAL_ADVANCE' || claimType === 'FULL_WITHDRAWAL') && (
              <div style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 14, padding: 20, marginBottom: 24 }}>
                <h3 style={{ color: '#e2e8f0', fontSize: 15, fontWeight: 700, marginBottom: 6 }}>
                  💰 Enter Requested Withdrawal Amount
                </h3>
                <p style={{ color: '#64748b', fontSize: 12, marginBottom: 14 }}>
                  Enter the amount you want to withdraw. The engine will verify against your balance and compute applicable tax/TDS.
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                  <span style={{ color: '#10b981', fontSize: 20, fontWeight: 700 }}>₹</span>
                  <input
                    type="number"
                    min="1000"
                    step="1000"
                    placeholder="e.g. 50000"
                    value={requestedAmount}
                    onChange={(e) => setRequestedAmount(e.target.value)}
                    style={{
                      flex: 1,
                      padding: '12px 16px',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1.5px solid rgba(16,185,129,0.3)',
                      borderRadius: 10,
                      color: '#f8fafc',
                      fontSize: 18,
                      fontWeight: 700,
                      outline: 'none',
                    }}
                    onFocus={(e) => { e.currentTarget.style.borderColor = '#10b981'; }}
                    onBlur={(e) => { e.currentTarget.style.borderColor = 'rgba(16,185,129,0.3)'; }}
                  />
                </div>

                {/* PAN Card Toggle */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={hasPan}
                      onChange={(e) => setHasPan(e.target.checked)}
                      style={{ accentColor: '#6366f1', width: 18, height: 18 }}
                    />
                    <span style={{ color: '#e2e8f0', fontSize: 14 }}>I have a valid PAN Card linked</span>
                  </label>
                  <span style={{ fontSize: 11, color: '#64748b', marginLeft: 'auto' }}>
                    {hasPan ? 'TDS @ 10%' : 'TDS @ 20% (no PAN)'}
                  </span>
                </div>
              </div>
            )}

            <button
              id="btn-check-eligibility"
              onClick={handleCheckEligibility}
              disabled={!claimType || loading}
              style={{
                width: '100%',
                background: claimType ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' : 'rgba(255,255,255,0.05)',
                color: claimType ? '#fff' : '#475569',
                border: 'none',
                borderRadius: 12,
                padding: '14px',
                fontSize: 15,
                fontWeight: 700,
                cursor: claimType ? 'pointer' : 'not-allowed',
                letterSpacing: '0.02em',
                transition: 'all 0.2s',
              }}
            >
              {loading ? 'Checking...' : '🔍 Check Eligibility →'}
            </button>
          </section>
        )}

        {/* ─── STEP 1: Eligibility Result ─── */}
        {step === 1 && eligibility && (
          <section>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <h2 style={{ color: '#e2e8f0', fontSize: 18, fontWeight: 700, margin: 0 }}>Eligibility Result</h2>
              <button onClick={reset} style={{ marginLeft: 'auto', background: 'none', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#64748b', padding: '4px 12px', cursor: 'pointer', fontSize: 12 }}>
                ← Start Over
              </button>
            </div>
            <EligibilityBadge result={eligibility} />

            {/* AI Explain Button */}
            <div style={{ marginTop: 16 }}>
              <button
                onClick={handleAiExplain}
                disabled={aiLoading}
                style={{
                  width: '100%',
                  background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(139,92,246,0.15) 100%)',
                  border: '1px solid rgba(99,102,241,0.35)',
                  borderRadius: 12,
                  color: '#a5b4fc',
                  padding: '12px',
                  fontSize: 14,
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
              >
                {aiLoading ? '🤖 Generating AI Explanation...' : '✨ Get AI Explanation (Groq LLM)'}
              </button>
            </div>

            {/* AI Explanation Panel */}
            {aiExplanation && (
              <div style={{
                marginTop: 16,
                background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.95) 100%)',
                border: '1px solid rgba(99,102,241,0.35)',
                borderRadius: 12,
                padding: '1.25rem',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{ fontSize: 18 }}>🤖</span>
                  <span style={{ fontSize: 13, fontWeight: 700, color: '#a5b4fc', letterSpacing: '0.05em' }}>AI CITIZEN EXPLANATION (GROQ LLAMA 3.3)</span>
                </div>

                <p style={{ fontSize: 14, color: '#e2e8f0', fontWeight: 600, marginBottom: 8 }}>
                  {aiExplanation.plain_language_summary}
                </p>

                <div style={{ marginBottom: 12 }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: '#c7d2fe', display: 'block', marginBottom: 4 }}>WHY ELIGIBLE OR NOT</span>
                  <p style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.6 }}>
                    {aiExplanation.why_eligible_or_not}
                  </p>
                </div>

                <div style={{ marginBottom: 12 }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: '#c7d2fe', display: 'block', marginBottom: 4 }}>WHAT HAPPENS NEXT</span>
                  <p style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.6 }}>
                    {aiExplanation.what_happens_next}
                  </p>
                </div>

                {aiExplanation.tax_note && (
                  <div style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)', borderRadius: 8, padding: '10px 14px', marginTop: 8 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: '#fbbf24' }}>💡 TAX NOTE</span>
                    <p style={{ fontSize: 13, color: '#fde68a', marginTop: 4 }}>{aiExplanation.tax_note}</p>
                  </div>
                )}
              </div>
            )}

            <button
              id="btn-calculate-payout"
              onClick={handleCalculate}
              disabled={loading}
              style={{ width: '100%', marginTop: 20, background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: '#fff', border: 'none', borderRadius: 12, padding: '14px', fontSize: 15, fontWeight: 700, cursor: 'pointer', letterSpacing: '0.02em' }}
            >
              {loading ? 'Calculating...' : '💰 Calculate Payout →'}
            </button>
          </section>
        )}

        {/* ─── STEP 2: Payout Calculation ─── */}
        {step === 2 && calculation && (
          <section>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <h2 style={{ color: '#e2e8f0', fontSize: 18, fontWeight: 700, margin: 0 }}>Payout & Tax Estimate</h2>
              <button onClick={() => setStep(1)} style={{ marginLeft: 'auto', background: 'none', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#64748b', padding: '4px 12px', cursor: 'pointer', fontSize: 12 }}>
                ← Back
              </button>
            </div>
            <CalculationSummaryCard result={calculation} />

            <button
              id="btn-presubmit-audit"
              onClick={handlePreSubmit}
              disabled={loading}
              style={{ width: '100%', marginTop: 20, background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', color: '#0f172a', border: 'none', borderRadius: 12, padding: '14px', fontSize: 15, fontWeight: 700, cursor: 'pointer', letterSpacing: '0.02em' }}
            >
              {loading ? 'Auditing...' : '🔎 Run Pre-Submit Audit →'}
            </button>
          </section>
        )}

        {/* ─── STEP 3: Pre-Submit Readiness ─── */}
        {step === 3 && preSubmit && (
          <section>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <h2 style={{ color: '#e2e8f0', fontSize: 18, fontWeight: 700, margin: 0 }}>Submission Readiness</h2>
              <button onClick={() => setStep(2)} style={{ marginLeft: 'auto', background: 'none', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#64748b', padding: '4px 12px', cursor: 'pointer', fontSize: 12 }}>
                ← Back
              </button>
            </div>
            <PreSubmitChecklist result={preSubmit} />

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 20 }}>
              <button
                id="btn-reset-wizard"
                onClick={reset}
                style={{ background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', borderRadius: 12, color: '#a5b4fc', padding: '12px', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
              >
                🔄 Start New Assessment
              </button>
              <a
                id="btn-epfo-portal"
                href="https://unifiedportal-mem.epfindia.gov.in/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'block',
                  background: preSubmit.is_ready_to_submit ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'rgba(255,255,255,0.05)',
                  color: preSubmit.is_ready_to_submit ? '#fff' : '#475569',
                  textDecoration: 'none',
                  borderRadius: 12,
                  padding: '12px',
                  fontSize: 14,
                  fontWeight: 700,
                  textAlign: 'center',
                  pointerEvents: preSubmit.is_ready_to_submit ? 'auto' : 'none',
                }}
              >
                🚀 Go to EPFO Portal
              </a>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default function DecisionPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#cbd5e1', background: 'linear-gradient(135deg, #0a0f1e 0%, #0f172a 50%, #1a0a2e 100%)' }}>Loading decision wizard…</div>}>
      <DecisionPageContent />
    </Suspense>
  );
}
