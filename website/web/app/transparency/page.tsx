"use client";
import Link from "next/link";

export default function TransparencyPage() {
  return (
    <main>
      <p><Link href="/">← home</Link></p>
      <h1>AI transparency</h1>
      <p>This page satisfies the EU AI Act Article 50 transparency obligations for this research project.</p>

      <h2>What is AI-generated</h2>
      <ul>
        <li>The 30 transcripts you may score on this site are entirely AI-generated.</li>
        <li>Both the interviewer's questions and the persona's answers were produced by foundation models, working from a synthetic patient persona that was itself generated from synthetic EHR data (Synthea).</li>
        <li>None of the personas, transcripts, or scores in this corpus describes any real patient.</li>
      </ul>

      <h2>Models used</h2>
      <ul>
        <li>Anthropic Claude (Haiku 4.5, Sonnet 4.6)</li>
        <li>Google Gemini (2.5 Flash)</li>
        <li>OpenAI GPT (gpt-5-mini-2025-08-07)</li>
      </ul>
      <p>The exact model identifier used to generate each transcript is in the transcript JSON file, fields <code>interviewer_model</code> and <code>persona_model</code>.</p>

      <h2>Risk classification</h2>
      <p>This system is a <strong>limited-risk</strong> AI system under the EU AI Act. It is not used for clinical decision-making, employment, education, law enforcement, biometrics, critical infrastructure, migration, or justice. It is research output only.</p>

      <h2>Known limitations</h2>
      <ul>
        <li>Transcripts may inherit any biases present in foundation models.</li>
        <li>Synthea EHR data has known under-representation of edge demographic profiles.</li>
        <li>The corpus has 3,925 unique themes but is not theme-saturated.</li>
        <li>Adversarial-stress profiles pass the project's robustness tests but are not guaranteed to surface every blind spot.</li>
      </ul>

      <h2>Full documentation</h2>
      <p>The complete system card is in the project repository at <code>docs/AI_ACT_TRANSPARENCY.md</code>. Compliance overview at <code>docs/COMPLIANCE.md</code>.</p>

      <p style={{ marginTop: "2rem" }}><Link href="/privacy">← privacy notice</Link>{"  ·  "}<Link href="/">home</Link></p>
    </main>
  );
}
