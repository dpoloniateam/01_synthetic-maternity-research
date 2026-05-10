"use client";
import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main>
      <p><Link href="/">← home</Link></p>
      <h1>Privacy notice</h1>
      <p>Last updated 2026-05-09. This notice satisfies GDPR Articles 13 and 14.</p>

      <h2>1. Controller</h2>
      <p>Universidade de Aveiro, represented by Daniel Polónia (lead author).<br />
        Email: <a href="mailto:dpolonia@ua.pt">dpolonia@ua.pt</a><br />
        Data Protection Officer: <a href="mailto:dpo@ua.pt">dpo@ua.pt</a><br />
        Supervisory authority: <a href="https://www.cnpd.pt" target="_blank" rel="noopener">CNPD (Portugal)</a>.</p>

      <h2>2. What we collect</h2>
      <ul>
        <li>Your email address (for sign-in only).</li>
        <li>Per-dimension integer scores (0–5) you submit.</li>
        <li>Optional free-text notes you choose to write.</li>
        <li>Submission timestamps.</li>
        <li>A consent record (email hash + consent version + timestamp).</li>
      </ul>
      <p>We do <strong>not</strong> collect IP addresses, device fingerprints, behavioural analytics, geolocation, demographic data, or health data.</p>

      <h2>3. Why and on what legal basis</h2>
      <ul>
        <li>Authenticate you and process your submissions — <strong>your explicit consent</strong> (GDPR Art 6(1)(a)).</li>
        <li>Maintain a security audit log — <strong>legitimate interest</strong> in security (Art 6(1)(f)).</li>
        <li>Demonstrate that consent was validly obtained — <strong>legal obligation</strong> (Art 7(1)).</li>
      </ul>

      <h2>4. Who can see your data</h2>
      <ul>
        <li>Daniel Polónia (lead author, controller representative).</li>
        <li>Rui S. Patrício (co-author) — only the analysis output, not per-coder raw scores.</li>
        <li>Google Cloud EMEA Limited — processor under DPA.</li>
      </ul>
      <p>The three large language models that scored transcripts (Anthropic, Google, OpenAI) receive <strong>only synthetic transcript text</strong>. They never receive your identity or your scores.</p>

      <h2>5. Where your data is stored</h2>
      <p>Google Cloud <code>europe-west2</code> (London, UK — covered by the EU adequacy decision). Single-region storage; no cross-region replication of your data.</p>

      <h2>6. How long we keep it</h2>
      <ul>
        <li>Email and submissions: until 12 months after publication of the corresponding paper, then automatically deleted.</li>
        <li>Consent record: 24 months after publication.</li>
        <li>Aggregated, irreversibly de-identified statistics published in the paper: indefinitely.</li>
      </ul>

      <h2>7. Your rights</h2>
      <p>You can exercise all GDPR Articles 15–22 rights. The two most direct are self-service:</p>
      <ul>
        <li><Link href="/me"><strong>Export my data</strong></Link> — JSON copy of everything we hold (Art 15 / 20).</li>
        <li><Link href="/me"><strong>Delete my data</strong></Link> — erasure of your submissions and consent (Art 17).</li>
      </ul>
      <p>For rectification, restriction, objection, or anything else, email <a href="mailto:dpolonia@ua.pt">dpolonia@ua.pt</a>. We respond within 30 days.</p>

      <h2>8. AI Act transparency</h2>
      <p>The transcripts you score are <strong>AI-generated</strong> by foundation models (Anthropic Claude, Google Gemini, OpenAI GPT) acting as both interviewer and persona over synthetic EHR data (Synthea). They depict synthetic personas, not real patients. Full system card: <Link href="/transparency">/transparency</Link>.</p>

      <h2>9. Security</h2>
      <p>TLS 1.3 in transit; Google-managed encryption at rest; least-privilege service accounts; Firestore security rules; CSP, HSTS, Permissions-Policy, X-Frame-Options DENY. Breach notification within 72 hours where the GDPR requires it.</p>

      <h2>10. No automated decisions</h2>
      <p>We do not make any automated decisions about you that produce legal or significant effects (GDPR Art 22).</p>

      <p style={{ marginTop: "2rem" }}><Link href="/">← home</Link></p>
    </main>
  );
}
