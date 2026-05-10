/**
 * One-shot seeder. Reads transcripts.json from Cloud Storage and
 * writes a study + sessions to Firestore.
 *
 * Usage:
 *   GCP_PROJECT=synthetic-mat-irr STUDY_ID=paper1_irr \
 *     ALLOWLIST=coderA@uni.edu,coderB@uni.edu node dist/seed.js
 */
import { Firestore } from "@google-cloud/firestore";
import { Storage } from "@google-cloud/storage";

interface SessionPayload {
  session_id: string;
  version?: number;
  persona_journey_stage?: string;
  persona_risk_level?: string;
  persona_vulnerability_flags?: string[];
  encoded_latent_dimensions?: string[];
  pairs?: Array<{
    question_id: string;
    question_text: string;
    response_text: string;
  }>;
}

const project = mustEnv("GCP_PROJECT");
const studyId = mustEnv("STUDY_ID");
const bucketName = process.env.BUCKET ?? `${project}-data`;
const allowlist = (process.env.ALLOWLIST ?? "")
  .split(",").map((s) => s.trim()).filter(Boolean);
const openToAnyone = (process.env.OPEN_TO_ANYONE ?? "false") === "true";

const db = new Firestore();
const storage = new Storage();

async function main() {
  const file = storage.bucket(bucketName)
    .file(`studies/${studyId}/transcripts.json`);
  const [buf] = await file.download();
  const transcripts = JSON.parse(buf.toString("utf8")) as SessionPayload[];
  console.log(`Loaded ${transcripts.length} sessions from gs://${bucketName}`);

  const studyRef = db.doc(`studies/${studyId}`);
  await studyRef.set({
    title: process.env.TITLE ?? `Study ${studyId}`,
    instrument: process.env.INSTRUMENT ?? "irr_richness_rubric_v1",
    dimensions: process.env.DIMENSIONS
      ? process.env.DIMENSIONS.split(",")
      : [
          "emotional_depth", "specificity", "latent_surfacing",
          "narrative_quality", "clinical_grounding",
        ],
    rater_allowlist: allowlist,
    open_to_anyone: openToAnyone,
    created_at: new Date(),
    closed_at: null,
  }, { merge: true });

  let n = 0;
  for (const t of transcripts) {
    await db.doc(`studies/${studyId}/sessions/${t.session_id}`)
      .set({ payload: t, order: n });
    n += 1;
    if (n % 10 === 0) console.log(`  seeded ${n}/${transcripts.length}`);
  }
  console.log(`Done. Study /studies/${studyId} with ${n} sessions.`);
}

function mustEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`${name} not set`);
  return v;
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
