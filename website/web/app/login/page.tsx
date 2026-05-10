"use client";
import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  sendSignInLinkToEmail, isSignInWithEmailLink, signInWithEmailLink,
  onAuthStateChanged,
} from "firebase/auth";
import { auth } from "@/lib/firebase";

const STORAGE_KEY = "irr_signin_email";
const STUDY_KEY = "irr_signin_study";
const DEFAULT_STUDY = "paper1_irr";

function LoginInner() {
  const router = useRouter();
  const params = useSearchParams();
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<string>("");
  const [signedIn, setSignedIn] = useState<string | null>(null);

  // Honour ?study=… on first visit; remember across the email-link round-trip.
  const studyFromQuery = params.get("study");
  const targetStudy = studyFromQuery
    ?? (typeof window !== "undefined"
        ? window.localStorage.getItem(STUDY_KEY) ?? DEFAULT_STUDY
        : DEFAULT_STUDY);

  useEffect(() => onAuthStateChanged(auth, (u) => {
    setSignedIn(u?.email ?? null);
  }), []);

  useEffect(() => {
    if (studyFromQuery) {
      window.localStorage.setItem(STUDY_KEY, studyFromQuery);
    }
  }, [studyFromQuery]);

  useEffect(() => {
    const url = window.location.href;
    if (!isSignInWithEmailLink(auth, url)) return;
    const stored = window.localStorage.getItem(STORAGE_KEY)
      ?? window.prompt("Confirm your email to finish signing in:") ?? "";
    if (!stored) return;
    const study = window.localStorage.getItem(STUDY_KEY) ?? DEFAULT_STUDY;
    setStatus("Signing in…");
    signInWithEmailLink(auth, stored, url)
      .then(() => {
        window.localStorage.removeItem(STORAGE_KEY);
        window.localStorage.removeItem(STUDY_KEY);
        router.replace(`/queue?study=${encodeURIComponent(study)}`);
      })
      .catch((e) => setStatus(`Error: ${e.message}`));
  }, [router]);

  async function send() {
    setStatus("Sending link…");
    try {
      await sendSignInLinkToEmail(auth, email, {
        url: `${window.location.origin}/login`,
        handleCodeInApp: true,
      });
      window.localStorage.setItem(STORAGE_KEY, email);
      setStatus("Link sent. Check your email and click it on this device.");
    } catch (e) {
      setStatus(`Error: ${(e as Error).message}`);
    }
  }

  if (signedIn) {
    return (
      <main>
        <h1>Signed in</h1>
        <p>You are signed in as <strong>{signedIn}</strong>.</p>
        <p><a href={`/queue?study=${encodeURIComponent(targetStudy)}`}>Go to your queue ({targetStudy})</a></p>
        <p style={{ color: "#888", fontSize: "0.9rem" }}>
          Other studies: <a href="/queue?study=paper1_irr">paper1_irr</a> · <a href="/queue?study=paper2_users">paper2_users</a>
        </p>
      </main>
    );
  }

  return (
    <main>
      <h1>Sign in</h1>
      <p>Enter the email address you were invited with. We will email you a one-time sign-in link.</p>
      <p style={{ color: "#888", fontSize: "0.9rem" }}>You will be routed to study: <code>{targetStudy}</code></p>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
             placeholder="you@university.edu"
             style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }} />
      <button onClick={send} disabled={!email}
              style={{ marginTop: "0.5rem", padding: "0.5rem 1rem" }}>
        Email me a sign-in link
      </button>
      <p>{status}</p>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<main><p>Loading…</p></main>}>
      <LoginInner />
    </Suspense>
  );
}
