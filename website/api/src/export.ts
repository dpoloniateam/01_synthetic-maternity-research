/**
 * Daily export Cloud Run job. Reads all responses for a study and
 * writes one JSON file plus (for studies with `questions`) two CSVs to
 * gs://${BUCKET}/exports/${STUDY_ID}/${date}.{json,_likert.csv,_open_ended.csv}.
 *
 * Triggered by Cloud Scheduler. Service account needs roles/datastore.viewer
 * and roles/storage.objectAdmin on the bucket.
 *
 * For Paper 1 (rubric mode, dimensions set): writes JSON only — the existing
 * analysis pipeline reads JSON.
 *
 * For Paper 2 (questions mode, dimensions empty + questions populated):
 * writes JSON plus two CSVs in the schemas the study2 analysis scripts expect:
 *   - {date}_likert.csv:    rater_uid, item_id, dimension_id, value
 *   - {date}_open_ended.csv: rater_uid, prompt_id, response_text
 */
import { Firestore } from "@google-cloud/firestore";
import { Storage } from "@google-cloud/storage";

const project = mustEnv("GCP_PROJECT");
const studyId = mustEnv("STUDY_ID");
const bucketName = process.env.BUCKET ?? `${project}-data`;

const db = new Firestore();
const storage = new Storage();

interface QuestionDef {
  id: string;
  text: string;
  kind?: "likert_7" | "single_select" | "text_short" | "text_long";
  dimension_id?: string;
}

async function main() {
  const studyDoc = await db.doc(`studies/${studyId}`).get();
  if (!studyDoc.exists) {
    throw new Error(`No such study: ${studyId}`);
  }
  const study = studyDoc.data()!;
  const dimensions: string[] = study.dimensions ?? [];
  const questions: QuestionDef[] = study.questions ?? [];

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
  const jsonDest = `exports/${studyId}/${date}.json`;
  await storage.bucket(bucketName).file(jsonDest).save(
    JSON.stringify(rows, null, 2),
    { contentType: "application/json" },
  );
  console.log(`Wrote ${rows.length} responses to gs://${bucketName}/${jsonDest}`);

  // CSV mode is opt-in via questions[]. Paper 1 (dimensions[]) keeps JSON only.
  if (questions.length > 0 && dimensions.length === 0) {
    const likertRows: string[] = ["rater_uid,item_id,dimension_id,value"];
    const openRows: string[] = ["rater_uid,prompt_id,response_text"];

    const likertIds = new Set(questions.filter((q) => q.kind === "likert_7").map((q) => q.id));
    const openIds = new Set(questions.filter((q) => q.kind === "text_long").map((q) => q.id));
    const dimById = Object.fromEntries(
      questions.filter((q) => q.kind === "likert_7").map((q) => [q.id, q.dimension_id ?? ""]),
    );

    for (const r of rows) {
      const answers = (r as any).answers ?? {};
      const uid = (r as any).rater_uid ?? "";
      for (const [qid, val] of Object.entries(answers)) {
        if (likertIds.has(qid)) {
          likertRows.push(`${csv(uid)},${csv(qid)},${csv(dimById[qid] ?? "")},${csv(String(val ?? ""))}`);
        } else if (openIds.has(qid)) {
          openRows.push(`${csv(uid)},${csv(qid)},${csv(String(val ?? ""))}`);
        }
      }
    }

    const likertDest = `exports/${studyId}/${date}_likert.csv`;
    await storage.bucket(bucketName).file(likertDest).save(
      likertRows.join("\n"),
      { contentType: "text/csv" },
    );
    console.log(`Wrote ${likertRows.length - 1} likert rows to gs://${bucketName}/${likertDest}`);

    const openDest = `exports/${studyId}/${date}_open_ended.csv`;
    await storage.bucket(bucketName).file(openDest).save(
      openRows.join("\n"),
      { contentType: "text/csv" },
    );
    console.log(`Wrote ${openRows.length - 1} open-ended rows to gs://${bucketName}/${openDest}`);
  }
}

function csv(s: string): string {
  if (/[,"\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
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
