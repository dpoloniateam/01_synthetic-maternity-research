/**
 * Daily export Cloud Run job. Reads all responses for a study and
 * writes one JSON file per study to gs://${BUCKET}/exports/${STUDY_ID}/${date}.json.
 *
 * Triggered by Cloud Scheduler. Service account needs roles/datastore.viewer
 * and roles/storage.objectAdmin on the bucket.
 */
import { Firestore } from "@google-cloud/firestore";
import { Storage } from "@google-cloud/storage";

const project = mustEnv("GCP_PROJECT");
const studyId = mustEnv("STUDY_ID");
const bucketName = process.env.BUCKET ?? `${project}-data`;

const db = new Firestore();
const storage = new Storage();

async function main() {
  const snap = await db.collection(`studies/${studyId}/responses`).get();
  const rows = snap.docs.map((d) => {
    const data = d.data();
    return {
      response_id: d.id,
      ...data,
      started_at: data.started_at?.toDate?.()?.toISOString() ?? null,
      submitted_at: data.submitted_at?.toDate?.()?.toISOString() ?? null,
    };
  });

  const date = new Date().toISOString().slice(0, 10);
  const dest = `exports/${studyId}/${date}.json`;
  await storage.bucket(bucketName).file(dest).save(
    JSON.stringify(rows, null, 2),
    { contentType: "application/json" },
  );
  console.log(`Wrote ${rows.length} responses to gs://${bucketName}/${dest}`);
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
