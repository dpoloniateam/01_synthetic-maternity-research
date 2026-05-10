import { auth, API_BASE } from "./firebase";

async function authedFetch(path: string, init?: RequestInit): Promise<Response> {
  const u = auth.currentUser;
  if (!u) throw new Error("not signed in");
  const token = await u.getIdToken();
  return fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
      authorization: `Bearer ${token}`,
      "content-type": "application/json",
    },
  });
}

export type QuestionKind = "likert_7" | "single_select" | "text_short" | "text_long";

export interface QuestionDef {
  id: string;
  text: string;
  scale?: string;
  kind?: QuestionKind;
  options?: string[];
  placeholder?: string;
  optional?: boolean;
  dimension_id?: string;
  dimension_label?: string;
}

export interface Study {
  id: string;
  title: string;
  instrument: string;
  dimensions?: string[];
  questions?: QuestionDef[];
  dimension_meta?: Array<{ id: string; label: string; definition: string }>;
  open_to_anyone: boolean;
}

export interface QueueItem {
  session_id: string;
  order: number;
  payload_summary: {
    version: number | null;
    persona_journey_stage: string | null;
    persona_risk_level: string | null;
    n_pairs: number;
  };
  submitted: boolean;
}

export interface SessionDetail {
  session_id: string;
  instrument: string;
  dimensions: string[] | null;
  questions: QuestionDef[] | null;
  payload: {
    session_id: string;
    version?: number | string;
    persona_journey_stage?: string;
    persona_risk_level?: string;
    persona_vulnerability_flags?: string[];
    encoded_latent_dimensions?: string[];
    pairs?: Array<{
      question_id: string;
      question_text: string;
      response_text: string;
    }>;
    stimulus_markdown?: string;
    design_context?: string[];
  };
}

export async function getStudy(studyId: string): Promise<Study> {
  const r = await authedFetch(`/study/${studyId}`);
  if (!r.ok) throw new Error(`getStudy: ${r.status}`);
  return r.json();
}

export async function getQueue(studyId: string): Promise<QueueItem[]> {
  const r = await authedFetch(`/study/${studyId}/queue`);
  if (!r.ok) throw new Error(`getQueue: ${r.status}`);
  const j = await r.json();
  return j.queue;
}

export async function getSession(
  studyId: string, sessionId: string,
): Promise<SessionDetail> {
  const r = await authedFetch(`/study/${studyId}/session/${sessionId}`);
  if (!r.ok) throw new Error(`getSession: ${r.status}`);
  return r.json();
}

export async function submitScore(body: {
  study_id: string;
  session_id: string;
  scores?: Record<string, number>;
  answers?: Record<string, unknown>;
  notes?: string;
}): Promise<{ ok: boolean; response_id: string }> {
  const r = await authedFetch(`/score`, {
    method: "POST", body: JSON.stringify(body),
  });
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    throw new Error(`submitScore: ${r.status} ${JSON.stringify(j)}`);
  }
  return r.json();
}

// ── consent ──────────────────────────────────────────────────────────

export interface ConsentState {
  granted: boolean;
  consent_version: string;
}

export async function getConsent(studyId: string): Promise<ConsentState> {
  const r = await authedFetch(`/consent/${studyId}`);
  if (!r.ok) throw new Error(`getConsent: ${r.status}`);
  return r.json();
}

export async function postConsent(body: {
  study_id: string;
  consent_version: string;
  granted: boolean;
  flags?: Record<string, boolean>;
}): Promise<{ ok: boolean; consent_version: string }> {
  const r = await authedFetch(`/consent`, {
    method: "POST", body: JSON.stringify(body),
  });
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    throw new Error(`postConsent: ${r.status} ${JSON.stringify(j)}`);
  }
  return r.json();
}

// ── DSAR ─────────────────────────────────────────────────────────────

export async function exportMyData(): Promise<unknown> {
  const r = await authedFetch(`/me/export`);
  if (!r.ok) throw new Error(`exportMyData: ${r.status}`);
  return r.json();
}

export async function deleteMyData(): Promise<{ ok: boolean; deleted_response_count: number }> {
  const r = await authedFetch(`/me/delete`, {
    method: "POST",
    body: JSON.stringify({ confirm: "DELETE_MY_DATA" }),
  });
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    throw new Error(`deleteMyData: ${r.status} ${JSON.stringify(j)}`);
  }
  return r.json();
}
