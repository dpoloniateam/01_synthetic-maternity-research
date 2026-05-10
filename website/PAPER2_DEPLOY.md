# Paper 2 — deployment runbook

End-to-end recipe for adding the Paper 2 expert-evaluation study to the existing IRR website (`synthetic-mat-irr-0134`). Reuses Identity Platform, Firestore, Cloud Run, and the daily Cloud Scheduler export job already deployed for Paper 1.

Prerequisite: CEIC-UA favourable opinion received (recruitment must not start before).

## 1. Build the API with the new endpoints + seeder

The `seed_paper2.ts` and the extended `export.ts` build into the same image as `index.ts`. Rebuild and push.

```bash
cd website/api
npm install
npm run build           # produces dist/{index,seed,seed_paper2,export,retention}.js

# Push the API image (already published as gcr.io/${PROJECT}/irr-api or similar)
gcloud builds submit --tag gcr.io/${PROJECT}/irr-api .
gcloud run deploy irr-api \
    --image gcr.io/${PROJECT}/irr-api \
    --region europe-west2 \
    --platform managed
```

## 2. Stage the Paper 2 source files

The seeder reads two inputs: the survey schema and the V4_R1 stimulus markdown. Stage them in Cloud Storage so the seeder Job can fetch them without bundling.

```bash
PROJECT=synthetic-mat-irr-0134
BUCKET=${PROJECT}-data

# 2a. Survey instrument (already exists in the repo)
gsutil cp \
    writing_outputs/20260320_JPIM_manuscript/RP/study2/study2_survey_instrument.json \
    gs://${BUCKET}/studies/paper2_users/instrument.json

# 2b. Stimulus markdown — extract V4_R1 from Annex 1 §A1.1
#     (manual one-time step: copy the §A1.1 block from annex_1.md to a standalone file)
gsutil cp \
    /tmp/annex_1_a1_1_v4r1_stimulus.md \
    gs://${BUCKET}/studies/paper2_users/stimulus.md
```

## 3. Run the seeder once (Cloud Run Job)

```bash
gcloud run jobs create seed-paper2 \
    --image gcr.io/${PROJECT}/irr-api \
    --command "node" --args "dist/seed_paper2.js" \
    --region europe-west2 \
    --service-account irr-api-sa@${PROJECT}.iam.gserviceaccount.com \
    --set-env-vars \
       "GCP_PROJECT=${PROJECT},STUDY_ID=paper2_users,BUCKET=${BUCKET},ALLOWLIST=expert1@uni.edu,expert2@uni.edu,...,OPEN_TO_ANYONE=false"

gcloud run jobs execute seed-paper2 --region europe-west2 --wait
```

Expected output:
```
Seeded /studies/paper2_users
  instrument:       study2_v1.0
  questions:        41   (4 background + 30 likert + 6 open-ended + 1 closing)
  likert items:     30
  text items:       11
  rater_allowlist:  N email(s)
  open_to_anyone:   false
```

Verify in the Firebase console: `/studies/paper2_users` exists with `dimensions: []` (empty), `questions` array of 41, `dimension_meta` of 6.

## 4. Schedule the daily CSV export

The existing daily-export Cloud Scheduler job already calls `dist/export.js` for `paper1_irr`. Add a parallel job for `paper2_users`:

```bash
gcloud scheduler jobs create http export-paper2 \
    --location europe-west2 \
    --schedule "15 02 * * *" \
    --time-zone "Europe/Lisbon" \
    --http-method POST \
    --uri "https://europe-west2-${PROJECT}.cloudfunctions.net/run-export?study=paper2_users" \
    --oidc-service-account-email irr-api-sa@${PROJECT}.iam.gserviceaccount.com
```

(If your existing setup uses a Cloud Run Job instead of a Cloud Function, mirror the `paper1_irr` scheduler — same image, same command, change `STUDY_ID=paper2_users` env var.)

The export will write three files per day to `gs://${BUCKET}/exports/paper2_users/${date}.{json, _likert.csv, _open_ended.csv}`. The two CSVs match the schema the `study2/study2_quant_analysis.py` and `study2/study2_qual_thematic.py` scripts expect.

## 5. Smoke-test the rater flow

1. Add your own email to the `rater_allowlist` in Firestore (`/studies/paper2_users`, field `rater_allowlist`).
2. Visit `https://synthetic-mat-irr-0134.web.app/?study=paper2_users` (replace with your hosting domain).
3. Enter your email → receive sign-in link → click it → land on `/queue?study=paper2_users`.
4. Confirm queue shows one session (`v4r1`).
5. Open the session → confirm the V4_R1 stimulus + design-context preface render correctly.
6. Confirm the form shows: 4 background items (single-select / text), 30 Likert items grouped by dimension, 6 open-ended (textarea), 1 optional follow-up email.
7. Submit a test response → confirm it lands at `/studies/paper2_users/responses/{your_uid}__v4r1`.
8. Trigger the export Job manually → confirm CSV files appear in the bucket.
9. Delete the test response from Firestore before live recruitment.

## 6. Open recruitment

Per `study2_recruitment.md`:
- Send wave 1 invitations to 24 candidates (12 per subpanel — to allow attrition while hitting n = 16 completed).
- Each invite includes the URL `https://synthetic-mat-irr-0134.web.app/?study=paper2_users`.
- Maintain `data/study2/recruitment_log.csv` outside the platform.
- Day-10 reminder for non-responders.

## 7. Run the analysis pipeline (when N ≥ 16 or theoretical saturation)

```bash
# Pull the most recent CSV exports
LATEST=$(gsutil ls gs://${BUCKET}/exports/paper2_users/*_likert.csv | tail -1)
gsutil cp "${LATEST}" data/study2/responses_likert.csv
gsutil cp "${LATEST/_likert/_open_ended}" data/study2/responses_open_ended.csv

# Quantitative
cd writing_outputs/20260320_JPIM_manuscript/RP/study2
python study2_quant_analysis.py \
    --input  ../../../../data/study2/responses_likert.csv \
    --outdir ../../../../data/study2/quant_results

# Qualitative (after two-coder coding session)
python study2_qual_thematic.py \
    --responses ../../../../data/study2/responses_open_ended.csv \
    --codings   ../../../../data/study2/codings.csv \
    --codebook  ../../../../data/study2/codebook.csv \
    --outdir    ../../../../data/study2/qual_results

# Integrated joint display
python study2_integrated_joint_display.py \
    --quant_dim_summary ../../../../data/study2/quant_results/per_dimension_descriptives.csv \
    --quant_compare     ../../../../data/study2/quant_results/subpanel_comparison.csv \
    --theme_freq        ../../../../data/study2/qual_results/theme_frequency.csv \
    --theme_rating_map  ../../../../data/study2/theme_rating_map.csv \
    --outdir            ../../../../data/study2/integrated_results
```

## 8. Substitute values into Paper 2

Search `writing_outputs/20260510_Paper2_preliminary/Paper2_v1_jpim_companion.md` for `[generously assumed]` / `expected and pre-registered` / placeholder cell markers and replace with the actual values from the analysis output.

## 9. Close the study

Once the manuscript update is in, set `closed_at` on `/studies/paper2_users` so the API rejects further submissions:

```bash
gcloud firestore documents set --project ${PROJECT} \
    --document=studies/paper2_users \
    --field=closed_at:timestamp:$(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --merge
```

## 10. Retention

The existing `retention.ts` job already deletes responses older than the retention window (12 months post-publication). It scans all studies — no Paper 2-specific change required.
