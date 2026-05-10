"use client";
import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { onAuthStateChanged, type User } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { getQueue, getStudy, type QueueItem, type Study } from "@/lib/api";
import ConsentGate from "@/components/ConsentGate";

function QueueInner() {
  const router = useRouter();
  const params = useSearchParams();
  const studyId = params.get("study") ?? "";
  const [user, setUser] = useState<User | null>(null);
  const [study, setStudy] = useState<Study | null>(null);
  const [queue, setQueue] = useState<QueueItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => onAuthStateChanged(auth, (u) => {
    setUser(u);
    if (!u) router.replace("/login");
  }), [router]);

  useEffect(() => {
    if (!user || !studyId) return;
    Promise.all([getStudy(studyId), getQueue(studyId)])
      .then(([s, q]) => { setStudy(s); setQueue(q); })
      .catch((e: Error) => setError(e.message));
  }, [user, studyId]);

  if (!studyId) return <main><p>Missing <code>?study=...</code> in URL.</p></main>;
  if (!user) return <main><p>Redirecting to sign-in…</p></main>;
  if (error) return <main><h1>Error</h1><p>{error}</p></main>;
  if (!study || !queue) return <main><p>Loading…</p></main>;

  const total = queue.length;
  const done = queue.filter((q) => q.submitted).length;

  return (
    <ConsentGate studyId={studyId}>
      <main>
        <h1>{study.title}</h1>
        <p>Signed in as <strong>{user.email}</strong>. Progress: {done}/{total}.{" "}
          <Link href="/me">Manage my data</Link>{"  ·  "}
          <Link href="/privacy">Privacy</Link>
        </p>
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>
              <th align="left">#</th>
              <th align="left">Session</th>
              <th align="left">Version</th>
              <th align="left">Stage</th>
              <th align="left">Risk</th>
              <th align="left">Pairs</th>
              <th align="left">Status</th>
            </tr>
          </thead>
          <tbody>
            {queue.map((q) => (
              <tr key={q.session_id} style={{ borderTop: "1px solid #ddd" }}>
                <td>{q.order + 1}</td>
                <td>
                  <Link href={`/score?study=${studyId}&sid=${q.session_id}`}>{q.session_id}</Link>
                </td>
                <td>{q.payload_summary.version ?? "—"}</td>
                <td>{q.payload_summary.persona_journey_stage ?? "—"}</td>
                <td>{q.payload_summary.persona_risk_level ?? "—"}</td>
                <td>{q.payload_summary.n_pairs}</td>
                <td>{q.submitted ? "✓ submitted" : "pending"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </ConsentGate>
  );
}

export default function QueuePage() {
  return (
    <Suspense fallback={<main><p>Loading…</p></main>}>
      <QueueInner />
    </Suspense>
  );
}
