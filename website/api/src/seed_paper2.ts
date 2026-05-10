/**
 * Paper 2 seeder. Reads study2_survey_instrument.json (and the V4_R1 stimulus
 * markdown) from local disk or Cloud Storage and writes a `paper2_users` study
 * + a single session to Firestore.
 *
 * Usage (local files):
 *   GCP_PROJECT=synthetic-mat-irr STUDY_ID=paper2_users \
 *     INSTRUMENT_FILE=./study2_survey_instrument.json \
 *     STIMULUS_FILE=./annex_1_a1_1_v4r1_stimulus.md \
 *     ALLOWLIST=expert1@uni.edu,expert2@uni.edu \
 *     node dist/seed_paper2.js
 *
 * Usage (from gs:// bucket):
 *   GCP_PROJECT=synthetic-mat-irr STUDY_ID=paper2_users \
 *     ALLOWLIST=expert1@uni.edu,expert2@uni.edu \
 *     node dist/seed_paper2.js
 *   (defaults to gs://${project}-data/studies/paper2_users/instrument.json
 *                 gs://${project}-data/studies/paper2_users/stimulus.md)
 */
import * as fs from "node:fs";
import { Firestore } from "@google-cloud/firestore";
import { Storage } from "@google-cloud/storage";

interface LikertItem {
  id: string;
  text: string;
  kind: "likert_7";
  dimension_id: string;
  dimension_label: string;
}
interface SelectItem {
  id: string;
  text: string;
  kind: "single_select";
  options: string[];
  optional?: boolean;
}
interface TextItem {
  id: string;
  text: string;
  kind: "text_short" | "text_long";
  optional?: boolean;
  placeholder?: string;
}
type FlatQuestion = LikertItem | SelectItem | TextItem;

interface InstrumentSchema {
  instrument_id: string;
  title: string;
  description?: string;
  background_block?: { items: Array<{ id: string; label: string; type: string; options?: string[]; research_team_only?: boolean }> };
  likert_dimensions: Array<{ id: string; label: string; definition: string; items: string[] }>;
  open_ended_block?: { prompts: Array<{ id: string; label: string; prompt: string }> };
  closing_block?: { text: string };
}

const project = mustEnv("GCP_PROJECT");
const studyId = mustEnv("STUDY_ID");
const bucketName = process.env.BUCKET ?? `${project}-data`;
const instrumentFile = process.env.INSTRUMENT_FILE;
const stimulusFile = process.env.STIMULUS_FILE;
const allowlist = (process.env.ALLOWLIST ?? "")
  .split(",").map((s) => s.trim()).filter(Boolean);
const openToAnyone = (process.env.OPEN_TO_ANYONE ?? "false") === "true";

const db = new Firestore();
const storage = new Storage();

async function readSource(localPath: string | undefined, gcsPath: string): Promise<string> {
  if (localPath) {
    return fs.promises.readFile(localPath, "utf8");
  }
  const [buf] = await storage.bucket(bucketName).file(gcsPath).download();
  return buf.toString("utf8");
}

function flatten(schema: InstrumentSchema): FlatQuestion[] {
  const out: FlatQuestion[] = [];

  // Background — skip research_team_only.
  for (const b of (schema.background_block?.items ?? [])) {
    if (b.research_team_only) continue;
    if (b.type === "single_select") {
      out.push({
        id: b.id,
        text: b.label,
        kind: "single_select",
        options: b.options ?? [],
      });
    } else {
      out.push({
        id: b.id,
        text: b.label,
        kind: "text_short",
        placeholder: "your answer",
      });
    }
  }

  // Likert dimensions — flatten to one item per dimension item.
  for (const d of schema.likert_dimensions) {
    d.items.forEach((stem, idx) => {
      out.push({
        id: `${d.id}_item${idx + 1}`,
        text: stem,
        kind: "likert_7",
        dimension_id: d.id,
        dimension_label: d.label,
      });
    });
  }

  // Open-ended prompts.
  for (const q of (schema.open_ended_block?.prompts ?? [])) {
    out.push({
      id: q.id,
      text: q.prompt,
      kind: "text_long",
      placeholder: `Your response to ${q.label}…`,
    });
  }

  // Optional closing email.
  out.push({
    id: "followup_email",
    text: "Optional: provide an email if you would like a summary of aggregate results when the study completes. (Not linked to your individual responses in publication.)",
    kind: "text_short",
    optional: true,
    placeholder: "you@example.org",
  });

  return out;
}

async function main() {
  const schemaJson = await readSource(
    instrumentFile,
    `studies/${studyId}/instrument.json`,
  );
  const schema = JSON.parse(schemaJson) as InstrumentSchema;

  const stimulusMd = await readSource(
    stimulusFile,
    `studies/${studyId}/stimulus.md`,
  );

  const questions = flatten(schema);
  const dimensionMeta = schema.likert_dimensions.map((d) => ({
    id: d.id, label: d.label, definition: d.definition,
  }));

  const studyRef = db.doc(`studies/${studyId}`);
  await studyRef.set({
    title: process.env.TITLE ?? schema.title,
    instrument: schema.instrument_id,
    // dimensions stays empty so the API/UI fall into questionsMode.
    dimensions: [],
    questions,
    dimension_meta: dimensionMeta,
    rater_allowlist: allowlist,
    open_to_anyone: openToAnyone,
    created_at: new Date(),
    closed_at: null,
  }, { merge: true });

  // Single session that holds the V4_R1 stimulus.
  await db.doc(`studies/${studyId}/sessions/v4r1`).set({
    payload: {
      session_id: "v4r1",
      version: "V4_R1",
      stimulus_markdown: stimulusMd,
      design_context: [
        "The guide is the output of a synthetic design laboratory in which 150 composite synthetic personas (combining clinical EHR trajectories with experiential narrative profiles) completed 300 AI-moderated synthetic interviews under a Balanced Incomplete Block Design across five candidate questionnaire versions.",
        "The selected version (V4 — Expectation–Perception Gap, SERVQUAL-inspired) was refined through a diagnostic-driven cycle that targeted seven latent-dimension blind spots, and consolidated by the research team from approximately thirty questions to twelve.",
        "The guide is intended to support semi-structured interviews of approximately 45–60 minutes covering preconception, pregnancy, birth, and post-partum, and is designed to surface goals, motivations, behaviours, and latent dimensions including power dynamics, identity tensions, structural barriers, and continuity of care.",
      ],
      pairs: [],  // Paper 2 has no Q&A pairs; the stimulus is the whole guide.
    },
    order: 0,
  });

  console.log(`Seeded /studies/${studyId}`);
  console.log(`  instrument:       ${schema.instrument_id}`);
  console.log(`  questions:        ${questions.length}`);
  console.log(`  likert items:     ${questions.filter((q) => q.kind === "likert_7").length}`);
  console.log(`  text items:       ${questions.filter((q) => q.kind === "text_long" || q.kind === "text_short").length}`);
  console.log(`  rater_allowlist:  ${allowlist.length} email(s)`);
  console.log(`  open_to_anyone:   ${openToAnyone}`);
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
