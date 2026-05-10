"use client";
import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { onAuthStateChanged, type User } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { getSession, submitScore, type SessionDetail, type QuestionDef } from "@/lib/api";

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

const LIKERT_7_ANCHORS = [
  { value: "1", label: "1 — Strongly disagree" },
  { value: "2", label: "2 — Disagree" },
  { value: "3", label: "3 — Somewhat disagree" },
  { value: "4", label: "4 — Neither agree nor disagree" },
  { value: "5", label: "5 — Somewhat agree" },
  { value: "6", label: "6 — Agree" },
  { value: "7", label: "7 — Strongly agree" },
  { value: "n/a", label: "Unable to judge" },
];

function isAnswered(q: QuestionDef, answers: Record<string, string>): boolean {
  if (q.optional) return true;
  const v = answers[q.id];
  return typeof v === "string" && v.length > 0;
}

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
    : (data.questions ?? []).every((q) => isAnswered(q, answers));

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
        {p.stimulus_markdown && (
          <>
            {(p.design_context ?? []).map((para, i) => (
              <p key={`ctx-${i}`} style={{ fontStyle: "italic", color: "#555" }}>{para}</p>
            ))}
            <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{p.stimulus_markdown}</pre>
          </>
        )}
        {!p.stimulus_markdown && (p.pairs ?? []).map((pair, i) => (
          <div key={pair.question_id} style={{ marginBottom: "1rem" }}>
            <p><strong>Q{i + 1} ({pair.question_id})</strong></p>
            <p style={{ whiteSpace: "pre-wrap" }}>{pair.question_text}</p>
            <p style={{ marginTop: "0.5rem" }}><strong>Persona:</strong></p>
            <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{pair.response_text}</pre>
          </div>
        ))}
        {!p.stimulus_markdown && (p.pairs ?? []).length === 0 && (
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

      {!rubricMode && (data.questions ?? []).map((q) => {
        const kind = q.kind ?? "text_short";
        const value = answers[q.id] ?? "";
        const setValue = (v: string) => setAnswers({ ...answers, [q.id]: v });
        const dimTag = q.dimension_label ? <span style={{ color: "#888", fontSize: "0.85rem" }}> [{q.dimension_label}]</span> : null;
        return (
          <div key={q.id} style={{ margin: "1rem 0", paddingBottom: "0.5rem", borderBottom: "1px solid #eee" }}>
            <label><strong>{q.id}.</strong> {q.text}{dimTag}{q.optional && <em style={{ color: "#888" }}> (optional)</em>}</label>
            {kind === "likert_7" && (
              <select value={value} onChange={(e) => setValue(e.target.value)}
                      style={{ display: "block", marginTop: "0.4rem", padding: "0.4rem" }}>
                <option value="" disabled>—</option>
                {LIKERT_7_ANCHORS.map((a) => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
            )}
            {kind === "single_select" && (
              <select value={value} onChange={(e) => setValue(e.target.value)}
                      style={{ display: "block", marginTop: "0.4rem", padding: "0.4rem" }}>
                <option value="" disabled>—</option>
                {(q.options ?? []).map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            )}
            {kind === "text_long" && (
              <textarea value={value} onChange={(e) => setValue(e.target.value)}
                        rows={4}
                        placeholder={q.placeholder ?? "your response"}
                        style={{ display: "block", width: "100%", marginTop: "0.4rem", padding: "0.5rem" }} />
            )}
            {kind === "text_short" && (
              <input value={value} onChange={(e) => setValue(e.target.value)}
                     placeholder={q.placeholder ?? q.scale ?? "your answer"}
                     style={{ display: "block", width: "100%", marginTop: "0.4rem", padding: "0.5rem" }} />
            )}
          </div>
        );
      })}

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
