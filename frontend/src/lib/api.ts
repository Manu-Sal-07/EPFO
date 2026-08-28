export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL !== undefined
    ? process.env.NEXT_PUBLIC_API_URL
    : process.env.NODE_ENV === 'production'
    ? ''
    : 'http://localhost:8000';

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token: string;
}

export interface CitizenProfile {
  id: string;
  display_name: string;
  email: string;
  is_demo: boolean;
  created_at: string;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  environment: string;
  database: boolean;
  redis: boolean;
  version: string;
}

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/api/v1/system/health`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Login failed');
  }
  return res.json();
}

export async function fetchProfile(accessToken: string): Promise<CitizenProfile> {
  const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Failed to fetch profile');
  return res.json();
}

// ── PF Decision Engine ────────────────────────────────────────────────────────

export interface RuleEvidence {
  field: string;
  expected: string;
  actual: string;
  description: string;
}

export interface EligibilityResult {
  rule_id: string;
  claim_type: string;
  form_number: string;
  status: 'ELIGIBLE' | 'CONDITIONALLY_ELIGIBLE' | 'INELIGIBLE';
  is_eligible: boolean;
  what_is_wrong: string;
  why_it_happened: string;
  recommended_action: string;
  reasons: string[];
  evidence: RuleEvidence[];
}

export interface CalculationResult {
  employee_share: number;
  employer_share: number;
  interest_accrued: number;
  total_balance: number;
  eligible_payout_amount: number;
  total_service_years: number;
  is_tax_free: boolean;
  taxability_reason: string;
  tds_rate_percent: number;
  estimated_tds_amount: number;
  form_15g_applicable: boolean;
  form_15g_recommendation: string;
}

export interface PreSubmitCheckItem {
  check_id: string;
  title: string;
  description: string;
  status: 'PASSED' | 'FAILED' | 'WARNING';
  is_blocking: boolean;
  remediation_hint: string;
}

export interface PreSubmitResult {
  is_ready_to_submit: boolean;
  readiness_score: number;
  total_checks: number;
  passed_checks: number;
  blocking_issues_count: number;
  check_items: PreSubmitCheckItem[];
}

export async function evaluateEligibility(
  token: string,
  claim_type: string,
  advance_ground?: string,
): Promise<EligibilityResult> {
  const res = await fetch(`${API_BASE}/api/v1/decision/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ claim_type, advance_ground }),
  });
  if (!res.ok) throw new Error('Eligibility evaluation failed');
  return res.json();
}

export async function calculatePayout(
  token: string,
  claim_type: string,
  advance_ground?: string,
  requested_amount?: number,
  has_pan?: boolean,
): Promise<CalculationResult> {
  const body: Record<string, unknown> = { claim_type };
  if (advance_ground) body.advance_ground = advance_ground;
  if (requested_amount && requested_amount > 0) body.requested_amount = requested_amount;
  if (has_pan !== undefined) body.has_pan = has_pan;

  const res = await fetch(`${API_BASE}/api/v1/decision/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error('Calculation failed');
  return res.json();
}

export async function runPreSubmitAudit(
  token: string,
  claim_type: string,
): Promise<PreSubmitResult> {
  const res = await fetch(`${API_BASE}/api/v1/decision/presubmit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ claim_type }),
  });
  if (!res.ok) throw new Error('Pre-submit audit failed');
  return res.json();
}

// ── AI Explanation Layer & RAG Knowledge Base ─────────────────────────────────

export interface FindingExplanation {
  plain_language_summary: string;
  what_this_means_for_you: string;
  steps_to_fix: string[];
  urgency_note: string | null;
  source_references: string[];
}

export interface DecisionExplanation {
  plain_language_summary: string;
  why_eligible_or_not: string;
  what_happens_next: string;
  tax_note: string | null;
}

export interface CaseNarrative {
  // Current backend contract
  status_summary?: string;
  what_is_pending?: string;
  citizen_friendly_note?: string;
  estimated_timeline?: string | null;

  // Legacy / UI compatibility fields used by older frontend payloads
  case_summary?: string;
  detailed_narrative?: string;
  recommended_next_step?: string;
}

export interface KnowledgeChunk {
  chunk_id: string;
  doc_title: string;
  section: string;
  content: string;
  scheme_reference: string;
}

export async function explainFinding(token: string, findingId: string): Promise<FindingExplanation> {
  const res = await fetch(`${API_BASE}/api/v1/health/findings/${findingId}/explain`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Finding explanation failed');
  return res.json();
}

export async function explainDecision(token: string, claimType: string, advanceGround?: string): Promise<DecisionExplanation> {
  const res = await fetch(`${API_BASE}/api/v1/decision/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ claim_type: claimType, advance_ground: advanceGround }),
  });
  if (!res.ok) throw new Error('Decision explanation failed');
  return res.json();
}

export async function explainCase(token: string, caseId: string): Promise<CaseNarrative> {
  const res = await fetch(`${API_BASE}/api/v1/cases/${caseId}/explain`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Case narrative explanation failed');
  return res.json();
}

export const explainCaseNarrative = explainCase;

export async function searchKnowledge(query: string): Promise<KnowledgeChunk[]> {
  const res = await fetch(`${API_BASE}/api/v1/knowledge/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('Knowledge search failed');
  return res.json();
}
