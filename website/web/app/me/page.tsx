"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { onAuthStateChanged, signOut, type User } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { exportMyData, deleteMyData } from "@/lib/api";

export default function MePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string>("");

  useEffect(() => onAuthStateChanged(auth, (u) => {
    setUser(u);
    if (!u) router.replace("/login");
  }), [router]);

  async function onExport() {
    setBusy(true);
    setStatus("Preparing your data…");
    try {
      const data = await exportMyData();
      const blob = new Blob([JSON.stringify(data, null, 2)],
        { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `my-data-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      setStatus("Exported.");
    } catch (e) {
      setStatus(`Error: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  }

  async function onDelete() {
    if (!confirm("This permanently deletes ALL your submissions and your consent record. This action cannot be undone. Continue?")) return;
    setBusy(true);
    setStatus("Deleting…");
    try {
      const r = await deleteMyData();
      setStatus(`Deleted ${r.deleted_response_count} response(s). Signing you out.`);
      await signOut(auth);
      setTimeout(() => router.replace("/"), 2000);
    } catch (e) {
      setStatus(`Error: ${(e as Error).message}`);
      setBusy(false);
    }
  }

  if (!user) return <main><p>Redirecting…</p></main>;

  return (
    <main>
      <p><Link href="/">← home</Link></p>
      <h1>Your data</h1>
      <p>Signed in as <strong>{user.email}</strong>.</p>

      <h2>Export (GDPR Article 15 / 20)</h2>
      <p>Download all the personal data we hold about you, as JSON. Includes every submission you've made and your consent record.</p>
      <button onClick={onExport} disabled={busy} style={{ padding: "0.6rem 1.2rem" }}>
        Export my data
      </button>

      <h2 style={{ marginTop: "2rem" }}>Delete (GDPR Article 17)</h2>
      <p>Permanently erase all your submissions and your consent record. Aggregated statistics that were already published in a paper cannot be retracted, but every individual record we hold about you will be deleted from our systems.</p>
      <button onClick={onDelete} disabled={busy}
              style={{ padding: "0.6rem 1.2rem", background: "#cc2222", color: "white", border: 0 }}>
        Delete my data
      </button>

      <h2 style={{ marginTop: "2rem" }}>Other rights</h2>
      <p>For rectification, restriction of processing, or to object to processing on legitimate-interest grounds, email <a href="mailto:dpolonia@ua.pt">dpolonia@ua.pt</a>. We respond within 30 days.</p>

      <p style={{ marginTop: "1rem", color: status.startsWith("Error") ? "#cc2222" : "#0a7" }}>{status}</p>

      <p style={{ marginTop: "2rem" }}>
        <Link href="/privacy">Privacy notice</Link>{"  ·  "}
        <Link href="/transparency">AI transparency</Link>
      </p>
    </main>
  );
}
