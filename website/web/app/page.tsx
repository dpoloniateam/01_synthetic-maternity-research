"use client";
import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>Synthetic Maternity Research — coder portal</h1>
      <p>Sign in with the email address you were invited with, then pick the study you were assigned.</p>
      <p><Link href="/login">Sign in</Link></p>
      <h2>Studies</h2>
      <ul>
        <li><Link href="/queue?study=paper1_irr">Paper 1 — IRR baseline (5-dimension richness rubric, 30 transcripts)</Link></li>
        <li><Link href="/queue?study=paper2_users">Paper 2 — user evaluation (invite-only)</Link></li>
      </ul>
      <hr style={{ margin: "2rem 0", border: 0, borderTop: "1px solid #ddd" }} />
      <p style={{ color: "#555", fontSize: "0.9rem" }}>
        <Link href="/privacy">Privacy notice</Link>{"  ·  "}
        <Link href="/transparency">AI transparency</Link>{"  ·  "}
        <Link href="/me">Manage my data</Link>
      </p>
      <p style={{ color: "#777", fontSize: "0.85rem", marginTop: "1rem" }}>
        Controller: Universidade de Aveiro · Daniel Polónia (<a href="mailto:dpolonia@ua.pt">dpolonia@ua.pt</a>) ·
        DPO: <a href="mailto:dpo@ua.pt">dpo@ua.pt</a> ·
        Supervisory authority: <a href="https://www.cnpd.pt" target="_blank" rel="noopener">CNPD</a>.
      </p>
    </main>
  );
}
