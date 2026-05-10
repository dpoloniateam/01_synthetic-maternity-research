"use client";
import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { onAuthStateChanged, type User } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { getSession, submitScore, type SessionDetail } from "@/lib/api";

const RUBRIC_BLURBS: Record<string, string> = {
  emotional_depth:
    "Layered, embodied, contradictory feelings — not just named affect.",
  specificity:
    "Numerals, named places, concrete scene-setting.",
  latent_surfacing:
    "Of the persona's encoded latent dimensions (listed below), how many surface in the response?",
  narrative_quality:
    "Temporal/causal connectives, reflection, story-shape across responses.",
  clinical_grounding:
    "Specific maternity-care terms (titres, prenatal vitamins, ultrasound, miscarriage), not just 'doctor'.",
};

function ScoreInner() {
  const router = useRouter();
  const params = useSearchParams();
  const studyId = params.get("study") ?? "";
  const sessionId = params.get("sid") ?? "";

  const [user, setUser] = useState<User | null>(null);
  const [data, setData] = useState<SessionDetail | null>(null);
  const [scores, setScores] = useState<Record<string, number>>({});
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => onAuthStateChanged(auth, (u) => {
    setUser(u);
    if (!u) router.replace("/login");
  }), [router]);

  useEffect(() => {
    if (!user || !studyId || !sessionId) return;
    getSession(studyId, sessionId)
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, [user, studyId, sessionId]);

  if (!studyId || !sessionId) return <main><p>Missing <code>?study=...&amp;sid=...</code> in URL.</p></main>;
  if (!user) return <main><p>Redirecting…</p></main>;
  if (error) return <main><p>Error: {error}</p></main>;
  if (!data) return <main><p>Loading…</p></main>;
  if (done) {
    return (
      <main>
        <h1>Submitted — {sessionId}</h1>
        <p>Thank you. Your scores are saved.</p>
        <p><Link href={`/queue?study=${studyId}`}>← back to queue</Link></p>
      </main>
    );
  }

  const rubricMode = (data.dimensions ?? []).length > 0;
  const ready = rubricMode
    ? (data.dimensions ?? []).every((d) => typeof scores[d] === "number")
    : (data.questions ?? []).every((q) => answers[q.id]?.length);

  async function onSubmit() {
    setSubmitting(true);
    try {
      await submitScore({
        study_id: studyId,
        session_id: sessionId,
        scores: rubricMode ? scores : undefined,
        answers: rubricMode ? undefined : answers,
        notes,
      });
      setDone(true);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  const p = data.payload;
  return (
    <main>
      <p><Link href={`/queue?study=${studyId}`}>← queue</Link></p>
      <h1>{sessionId}{p.version ? ` (v${p.version})` : ""}</h1>
      <p style={{ color: "#555" }}>
        {p.persona_journey_stage ?? "—"}, risk: {p.persona_risk_level ?? "—"}.
        Vulnerability flags: {(p.persona_vulnerability_flags ?? []).join(", ") || "—"}.
      </p>
      {rubricMode && (
        <p style={{ color: "#555" }}>
          Encoded latent dimensions: <em>{(p.encoded_latent_dimensions ?? []).join(", ") || "—"}</em>
        </p>
      )}

      <section style={{ background: "#f7f7f7", padding: "1rem", borderRadius: 8 }}>
        {(p.pairs ?? []).map((pair, i) => (
          <div key={pair.question_id} style={{ marginBottom: "1rem" }}>
            <p><strong>Q{i + 1} ({pair.question_id})</strong></p>
            <p style={{ whiteSpace: "pre-wrap" }}>{pair.question_text}</p>
            <p style={{ marginTop: "0.5rem" }}><strong>Persona:</strong></p>
            <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{pair.response_text}</pre>
          </div>
        ))}
        {(p.pairs ?? []).length === 0 && (
          <p><em>Empty transcript — score 0 across the board.</em></p>
        )}
      </section>

      <h2>Score</h2>
      {rubricMode && (data.dimensions ?? []).map((d) => (
        <div key={d} style={{ margin: "0.75rem 0" }}>
          <label><strong>{d}</strong>{" "}
            <select value={scores[d] ?? ""}
                    onChange={(e) =>
                      setScores({ ...scores, [d]: Number(e.target.value) })}>
              <option value="" disabled>—</option>
              {[0, 1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
          <p style={{ margin: "0.25rem 0 0", color: "#555", fontSize: "0.9rem" }}>{RUBRIC_BLURBS[d] ?? ""}</p>
        </div>
      ))}

      {!rubricMode && (data.questions ?? []).map((q) => (
        <div key={q.id} style={{ margin: "0.75rem 0" }}>
          <label><strong>{q.text}</strong></label>
          <input value={answers[q.id] ?? ""}
                 onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                 placeholder={q.scale ?? "your answer"}
                 style={{ display: "block", width: "100%", padding: "0.5rem" }} />
        </div>
      ))}

      <h3>Notes (optional)</h3>
      <textarea value={notes} onChange={(e) => setNotes(e.target.value)}
                rows={4}
                style={{ width: "100%", padding: "0.5rem" }} />

      <p style={{ marginTop: "1rem" }}>
        <button onClick={onSubmit} disabled={!ready || submitting}
                style={{ padding: "0.6rem 1.2rem", fontSize: "1rem" }}>
          {submitting ? "Submitting…" : "Submit"}
        </button>
      </p>
    </main>
  );
}

export default function ScorePage() {
  return (
    <Suspense fallback={<main><p>Loading…</p></main>}>
      <ScoreInner />
    </Suspense>
  );
}
