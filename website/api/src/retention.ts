/**
 * Data-retention job. Deletes response docs older than RETENTION_DAYS.
 * Set DRY_RUN=true to print what would be deleted without deleting.
 *
 * Honours the privacy notice's promise: 12 months after publication the
 * raw responses are erased. RETENTION_DAYS defaults to 395 (12 months
 * + 30-day grace). Toggle DRY_RUN=false only after Paper 1 is published.
 */
import { Firestore } from "@google-cloud/firestore";

const db = new Firestore();

const RETENTION_DAYS = Number(process.env.RETENTION_DAYS ?? "395");
const STUDY_ID = process.env.STUDY_ID ?? "paper1_irr";
const DRY_RUN = (process.env.DRY_RUN ?? "true") === "true";

async function main() {
  const cutoff = new Date(Date.now() - RETENTION_DAYS * 86400 * 1000);
  const snap = await db.collection(`studies/${STUDY_ID}/responses`).get();
  let candidates = 0;
  let deleted = 0;
  for (const d of snap.docs) {
    const submitted = d.get("submitted_at")?.toDate?.();
    if (!submitted || submitted >= cutoff) continue;
    candidates += 1;
    if (DRY_RUN) {
      console.log("would delete", d.id, "submitted_at", submitted.toISOString());
      continue;
    }
    await d.ref.delete();
    deleted += 1;
  }
  console.log(
    `${DRY_RUN ? "DRY RUN — would delete" : "Deleted"} ${DRY_RUN ? candidates : deleted} ` +
    `responses older than ${cutoff.toISOString()} in study ${STUDY_ID}`
  );
}

main().catch((e) => { console.error(e); process.exit(1); });
