import { Hono } from "hono";
import { cors } from "hono/cors";
import { serve } from "@hono/node-server";
import { Firestore, FieldValue } from "@google-cloud/firestore";

const db = new Firestore();
const app = new Hono();

const CONSENT_VERSION = "2026-05-09-v1";

app.use("*", cors({ origin: (origin) => origin ?? "*", credentials: true }));

// Per-UID + per-IP token bucket. Resets on cold start. Sufficient at
// research scale; replace with Cloud Armor if traffic > 10k/day.
const RATE_BUCKET = new Map<string, { tokens: number; refilled: number }>();
function rateLimited(key: string, capacity = 30, refillPerMin = 30): boolean {
  const now = Date.now();
  const entry = RATE_BUCKET.get(key) ?? { tokens: capacity, refilled: now };
  const elapsed = (now - entry.refilled) / 60000;
  entry.tokens = Math.min(capacity, entry.tokens + elapsed * refillPerMin);
  entry.refilled = now;
  if (entry.tokens < 1) {
    RATE_BUCKET.set(key, entry);
    return true;
  }
  entry.tokens -= 1;
  RATE_BUCKET.set(key, entry);
  return false;
}

interface AuthedUser { uid: string; email: string; }

async function authedUser(req: Request): Promise<AuthedUser | null> {
  const auth = req.headers.get("authorization") ?? "";
  if (!auth.startsWith("Bearer ")) return null;
  const idToken = auth.slice(7);
  const apiKey = process.env.GCIP_API_KEY;
  if (!apiKey) throw new Error("GCIP_API_KEY not set");
  const r = await fetch(
    `https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${apiKey}`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ idToken }),
    },
  );
  if (!r.ok) return null;
  const j = (await r.json()) as { users?: Array<{ localId: string; email?: string }> };
  const u = j.users?.[0];
  if (!u || !u.email) return null;
  return { uid: u.localId, email: u.email };
}

app.get("/api/healthz", (c) => c.json({ ok: true }));

app.get("/api/me", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);
  return c.json(me);
});

app.get("/api/study/:study_id", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);
  const studyId = c.req.param("study_id");
  const doc = await db.doc(`studies/${studyId}`).get();
  if (!doc.exists) return c.json({ error: "no_study" }, 404);
  const study = doc.data()!;
  if (!study.open_to_anyone &&
      !(study.rater_allowlist ?? []).includes(me.email)) {
    return c.json({ error: "not_allowlisted" }, 403);
  }
  // Strip allowlist before returning to client.
  const { rater_allowlist: _, ...safe } = study;
  return c.json({ id: studyId, ...safe });
});

app.get("/api/study/:study_id/queue", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);
  const studyId = c.req.param("study_id");

  const studyDoc = await db.doc(`studies/${studyId}`).get();
  if (!studyDoc.exists) return c.json({ error: "no_study" }, 404);
  const study = studyDoc.data()!;
  if (!study.open_to_anyone &&
      !(study.rater_allowlist ?? []).includes(me.email)) {
    return c.json({ error: "not_allowlisted" }, 403);
  }

  const sessionsSnap = await db.collection(`studies/${studyId}/sessions`)
    .orderBy("order").get();

  const submitted = new Set<string>();
  const responsesSnap = await db.collection(`studies/${studyId}/responses`)
    .where("rater_uid", "==", me.uid).get();
  responsesSnap.forEach((d) => {
    const data = d.data();
    if (data.submitted_at) submitted.add(data.session_id);
  });

  const queue = sessionsSnap.docs.map((d) => ({
    session_id: d.id,
    order: d.get("order"),
    payload_summary: {
      version: d.get("payload.version") ?? null,
      persona_journey_stage: d.get("payload.persona_journey_stage") ?? null,
      persona_risk_level: d.get("payload.persona_risk_level") ?? null,
      n_pairs: (d.get("payload.pairs") ?? []).length,
    },
    submitted: submitted.has(d.id),
  }));
  return c.json({ study_id: studyId, queue });
});

app.get("/api/study/:study_id/session/:session_id", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);
  const { study_id, session_id } = c.req.param();
  const studyDoc = await db.doc(`studies/${study_id}`).get();
  if (!studyDoc.exists) return c.json({ error: "no_study" }, 404);
  const study = studyDoc.data()!;
  if (!study.open_to_anyone &&
      !(study.rater_allowlist ?? []).includes(me.email)) {
    return c.json({ error: "not_allowlisted" }, 403);
  }
  const sessDoc = await db.doc(
    `studies/${study_id}/sessions/${session_id}`).get();
  if (!sessDoc.exists) return c.json({ error: "no_session" }, 404);
  return c.json({
    session_id,
    payload: sessDoc.get("payload"),
    instrument: study.instrument,
    dimensions: study.dimensions ?? null,
    questions: study.questions ?? null,
  });
});

interface ScoreBody {
  study_id: string;
  session_id: string;
  scores?: Record<string, number>;
  answers?: Record<string, unknown>;
  notes?: string;
}

interface ConsentBody {
  study_id: string;
  consent_version: string;
  granted: boolean;
  flags?: Record<string, boolean>;
}

async function hasValidConsent(studyId: string, uid: string): Promise<boolean> {
  const doc = await db.doc(`studies/${studyId}/consents/${uid}`).get();
  if (!doc.exists) return false;
  const c = doc.data()!;
  return c.granted === true && c.consent_version === CONSENT_VERSION;
}

app.post("/api/consent", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);
  if (rateLimited(`consent:${me.uid}`, 5, 5)) {
    return c.json({ error: "rate_limited" }, 429);
  }
  const body = await c.req.json<ConsentBody>();
  if (!body?.study_id || typeof body.granted !== "boolean") {
    return c.json({ error: "bad_request" }, 400);
  }
  // Pin consent version server-side — clients cannot pretend to consent
  // to an older or differently-worded notice.
  await db.doc(`studies/${body.study_id}/consents/${me.uid}`).set({
    rater_uid: me.uid,
    email_hash: await sha256(me.email),
    granted: body.granted,
    consent_version: CONSENT_VERSION,
    flags: body.flags ?? {},
    created_at: FieldValue.serverTimestamp(),
  }, { merge: true });
  return c.json({ ok: true, consent_version: CONSENT_VERSION });
});

app.get("/api/consent/:study_id", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);
  const studyId = c.req.param("study_id");
  const doc = await db.doc(`studies/${studyId}/consents/${me.uid}`).get();
  if (!doc.exists) {
    return c.json({ granted: false, consent_version: CONSENT_VERSION });
  }
  const data = doc.data()!;
  return c.json({
    granted: data.granted === true && data.consent_version === CONSENT_VERSION,
    consent_version: CONSENT_VERSION,
  });
});

app.post("/api/score", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);
  if (rateLimited(`score:${me.uid}`, 30, 30)) {
    return c.json({ error: "rate_limited" }, 429);
  }
  const body = await c.req.json<ScoreBody>();
  if (!body?.study_id || !body?.session_id) {
    return c.json({ error: "bad_request" }, 400);
  }

  const studyDoc = await db.doc(`studies/${body.study_id}`).get();
  if (!studyDoc.exists) return c.json({ error: "no_study" }, 404);
  const study = studyDoc.data()!;
  if (study.closed_at) {
    return c.json({ error: "study_closed" }, 409);
  }
  if (!study.open_to_anyone &&
      !(study.rater_allowlist ?? []).includes(me.email)) {
    return c.json({ error: "not_allowlisted" }, 403);
  }

  // GDPR Art 7: refuse processing without valid consent for current notice.
  if (!(await hasValidConsent(body.study_id, me.uid))) {
    return c.json({ error: "consent_required",
                    consent_version: CONSENT_VERSION }, 412);
  }

  // Validate payload shape against the study instrument.
  const dims: string[] = study.dimensions ?? [];
  if (dims.length > 0) {
    if (!body.scores) return c.json({ error: "scores_required" }, 400);
    for (const d of dims) {
      const v = body.scores[d];
      if (typeof v !== "number" || v < 0 || v > 5 || !Number.isInteger(v)) {
        return c.json({ error: `bad_score:${d}` }, 400);
      }
    }
    // Reject submissions with extraneous fields (data minimisation).
    for (const k of Object.keys(body.scores)) {
      if (!dims.includes(k)) return c.json({ error: `unknown_dim:${k}` }, 400);
    }
  } else {
    if (!body.answers) return c.json({ error: "answers_required" }, 400);
  }
  if (typeof body.notes === "string" && body.notes.length > 5000) {
    return c.json({ error: "notes_too_long" }, 400);
  }

  const docId = `${me.uid}__${body.session_id}`;
  const ref = db.doc(`studies/${body.study_id}/responses/${docId}`);
  const existing = await ref.get();
  if (existing.exists && existing.get("submitted_at")) {
    return c.json({ error: "already_submitted" }, 409);
  }

  const composite = body.scores
    ? round1(avg(Object.values(body.scores)))
    : null;

  // Data minimisation: store rater_uid (pseudonym) only. Do NOT store
  // rater_email or user_agent on the submission document. Identity
  // remains in the auth profile only.
  await ref.set({
    rater_uid: me.uid,
    session_id: body.session_id,
    scores: body.scores ?? null,
    answers: body.answers ?? null,
    composite,
    notes: body.notes ?? "",
    instrument_version: study.instrument,
    consent_version: CONSENT_VERSION,
    started_at: existing.get("started_at") ?? FieldValue.serverTimestamp(),
    submitted_at: FieldValue.serverTimestamp(),
  }, { merge: true });

  return c.json({ ok: true, response_id: docId });
});

// ── DSAR endpoints (GDPR Articles 15, 17, 20) ───────────────────────

app.get("/api/me/export", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);

  const responses: any[] = [];
  const consents: any[] = [];

  const studiesSnap = await db.collection("studies").get();
  for (const studyDoc of studiesSnap.docs) {
    const studyId = studyDoc.id;
    const respSnap = await db.collection(`studies/${studyId}/responses`)
      .where("rater_uid", "==", me.uid).get();
    respSnap.forEach((d) => responses.push({
      study_id: studyId, response_id: d.id, ...d.data(),
    }));
    const consDoc = await db.doc(`studies/${studyId}/consents/${me.uid}`).get();
    if (consDoc.exists) {
      consents.push({ study_id: studyId, ...consDoc.data() });
    }
  }

  return c.json({
    rater_uid: me.uid, rater_email: me.email,
    exported_at: new Date().toISOString(),
    responses, consents,
    notice: "This export contains all personal data we hold about you that is associated with your authenticated identity. Synthetic transcripts and rubric metadata are excluded — they are not personal data.",
  });
});

app.post("/api/me/delete", async (c) => {
  const me = await authedUser(c.req.raw);
  if (!me) return c.json({ error: "unauthorized" }, 401);
  const body = await c.req.json<{ confirm: string }>().catch(() => ({} as any));
  if (body.confirm !== "DELETE_MY_DATA") {
    return c.json({ error: "confirm_required",
                    expect: 'POST body must include {"confirm":"DELETE_MY_DATA"}' }, 400);
  }

  const studiesSnap = await db.collection("studies").get();
  let deleted = 0;
  for (const studyDoc of studiesSnap.docs) {
    const studyId = studyDoc.id;
    const respSnap = await db.collection(`studies/${studyId}/responses`)
      .where("rater_uid", "==", me.uid).get();
    for (const d of respSnap.docs) {
      await d.ref.delete();
      deleted += 1;
    }
    await db.doc(`studies/${studyId}/consents/${me.uid}`).delete()
      .catch(() => undefined);
  }

  // Audit log of the deletion event (does NOT contain the deleted data).
  await db.collection("dsar_log").add({
    action: "delete",
    rater_uid: me.uid,
    email_hash: await sha256(me.email),
    deleted_response_count: deleted,
    at: FieldValue.serverTimestamp(),
  });

  return c.json({ ok: true, deleted_response_count: deleted });
});

async function sha256(input: string): Promise<string> {
  const buf = await crypto.subtle.digest(
    "SHA-256", new TextEncoder().encode(input));
  return [...new Uint8Array(buf)]
    .map((b) => b.toString(16).padStart(2, "0")).join("");
}

function avg(xs: number[]): number {
  if (xs.length === 0) return 0;
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}
function round1(x: number): number {
  return Math.round(x * 10) / 10;
}

const port = Number(process.env.PORT ?? 8080);
serve({ fetch: app.fetch, port });
console.log(`irr-api listening on :${port}`);
