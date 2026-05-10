"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getConsent, postConsent } from "@/lib/api";

interface Props {
  studyId: string;
  children: React.ReactNode;
}

export default function ConsentGate({ studyId, children }: Props) {
  const [state, setState] =
    useState<"loading" | "needs_consent" | "granted" | "error">("loading");
  const [error, setError] = useState<string | null>(null);
  const [consentVersion, setConsentVersion] = useState<string>("");
  const [agreeProcessing, setAgreeProcessing] = useState(false);
  const [agreeAi, setAgreeAi] = useState(false);
  const [agreeRetention, setAgreeRetention] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getConsent(studyId)
      .then((c) => {
        setConsentVersion(c.consent_version);
        setState(c.granted ? "granted" : "needs_consent");
      })
      .catch((e: Error) => { setError(e.message); setState("error"); });
  }, [studyId]);

  async function grant() {
    if (!agreeProcessing || !agreeAi || !agreeRetention) return;
    setBusy(true);
    try {
      await postConsent({
        study_id: studyId,
        consent_version: consentVersion,
        granted: true,
        flags: { processing: true, ai_origin: true, retention: true },
      });
      setState("granted");
    } catch (e) {
      setError((e as Error).message);
      setState("error");
    } finally {
      setBusy(false);
    }
  }

  if (state === "loading") return <main><p>Loading consent state…</p></main>;
  if (state === "error") return <main><p>Error: {error}</p></main>;
  if (state === "granted") return <>{children}</>;

  return (
    <main>
      <h1>Informed consent</h1>
      <p>Before you start scoring, please read the <Link href="/privacy">privacy notice</Link> and the <Link href="/transparency">AI transparency page</Link>, then confirm the three statements below. You can withdraw at any time on the <Link href="/me">/me</Link> page.</p>

      <p><strong>What you are consenting to (consent version {consentVersion}):</strong></p>

      <label style={{ display: "block", margin: "0.75rem 0" }}>
        <input type="checkbox" checked={agreeProcessing}
               onChange={(e) => setAgreeProcessing(e.target.checked)} />{" "}
        I understand that my email and the integer scores I submit will be processed by Daniel Polónia (Universidade de Aveiro) for the purpose of computing inter-rater reliability for the synthetic maternity research project.
      </label>

      <label style={{ display: "block", margin: "0.75rem 0" }}>
        <input type="checkbox" checked={agreeAi}
               onChange={(e) => setAgreeAi(e.target.checked)} />{" "}
        I understand that the transcripts I will score are <strong>AI-generated</strong> from synthetic personas based on synthetic EHR data, and depict no real patient.
      </label>

      <label style={{ display: "block", margin: "0.75rem 0" }}>
        <input type="checkbox" checked={agreeRetention}
               onChange={(e) => setAgreeRetention(e.target.checked)} />{" "}
        I understand that my personal data is retained for at most 12 months after publication of the corresponding paper, and that I may export or delete my data at any time on the /me page.
      </label>

      <p style={{ marginTop: "1rem" }}>
        <button onClick={grant}
                disabled={busy || !agreeProcessing || !agreeAi || !agreeRetention}
                style={{ padding: "0.6rem 1.2rem", fontSize: "1rem" }}>
          {busy ? "Saving…" : "I consent — continue"}
        </button>
      </p>

      <p style={{ marginTop: "2rem", color: "#555", fontSize: "0.9rem" }}>
        Lawful basis: GDPR Article 6(1)(a) — your explicit consent. You may withdraw consent at any time via /me, with the same effect as a deletion request. Withdrawal does not affect the lawfulness of processing carried out before withdrawal.
      </p>
    </main>
  );
}
