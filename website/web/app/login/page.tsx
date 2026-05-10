"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  sendSignInLinkToEmail, isSignInWithEmailLink, signInWithEmailLink,
  onAuthStateChanged,
} from "firebase/auth";
import { auth } from "@/lib/firebase";

const STORAGE_KEY = "irr_signin_email";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<string>("");
  const [signedIn, setSignedIn] = useState<string | null>(null);

  useEffect(() => onAuthStateChanged(auth, (u) => {
    setSignedIn(u?.email ?? null);
  }), []);

  useEffect(() => {
    const url = window.location.href;
    if (!isSignInWithEmailLink(auth, url)) return;
    const stored = window.localStorage.getItem(STORAGE_KEY)
      ?? window.prompt("Confirm your email to finish signing in:") ?? "";
    if (!stored) return;
    setStatus("Signing in…");
    signInWithEmailLink(auth, stored, url)
      .then(() => {
        window.localStorage.removeItem(STORAGE_KEY);
        router.replace("/queue?study=paper1_irr");
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
        <p><a href="/queue?study=paper1_irr">Go to Paper 1 — IRR queue</a></p>
      </main>
    );
  }

  return (
    <main>
      <h1>Sign in</h1>
      <p>Enter the email address you were invited with. We will email you a one-time sign-in link.</p>
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
