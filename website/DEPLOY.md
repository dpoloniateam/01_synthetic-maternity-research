# DEPLOY.md — short runbook

The full reference (every flag, every IAM binding) is in `../docs/human_irr_website.md`. This file is the concise sequence of commands you run on a fresh laptop to bring the site up.

```
website/
├── api/                  Cloud Run service (Hono + TS)
├── web/                  Next.js 14 app, exported as static site
├── firebase.json         Hosting + rules + rewrites
├── firestore.rules       Per-rater isolation, allowlist enforcement
├── firestore.indexes.json
└── .firebaserc           Project id (replace REPLACE-WITH-YOUR-PROJECT-ID)
```

## 1. One-time setup

```bash
PROJECT_ID="synthetic-mat-irr"          # change me
REGION="europe-west2"

gcloud projects create "$PROJECT_ID" --name="Synthetic Maternity IRR"
gcloud config set project "$PROJECT_ID"
gcloud beta billing projects link "$PROJECT_ID" --billing-account="<BILLING-ID>"

gcloud services enable \
  firestore.googleapis.com run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com identitytoolkit.googleapis.com \
  secretmanager.googleapis.com storage.googleapis.com \
  cloudscheduler.googleapis.com

# Service accounts (least privilege).
gcloud iam service-accounts create irr-runtime --display-name "IRR runtime"
gcloud iam service-accounts create irr-exporter --display-name "IRR export"

for ROLE in roles/datastore.user roles/secretmanager.secretAccessor; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:irr-runtime@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="$ROLE"
done
for ROLE in roles/datastore.viewer roles/storage.objectAdmin; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:irr-exporter@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="$ROLE"
done

# Firestore in Native mode.
gcloud firestore databases create --location="$REGION" --type=firestore-native

# Cloud Storage bucket for the transcript packet and nightly exports.
gsutil mb -l "$REGION" "gs://${PROJECT_ID}-data"
```

In the **Console** → Identity Platform → Providers, enable **Email/Password** and **Email link (passwordless)**. Note the API key under "Application setup details".

Edit `website/.firebaserc` and replace `REPLACE-WITH-YOUR-PROJECT-ID` with `$PROJECT_ID`.

## 2. Seed the transcript packet

```bash
# Build the packet (already produced once; re-run if transcripts change).
cd /home/dpolonia/01_synthetic-maternity-research
python -m src.evaluation.build_coder_kit

gsutil cp data/evaluation/coder_kit/transcripts.json \
    "gs://${PROJECT_ID}-data/studies/paper1_irr/transcripts.json"
gsutil cp data/evaluation/coder_kit/MANIFEST.json \
    "gs://${PROJECT_ID}-data/studies/paper1_irr/MANIFEST.json"

# Run the seed locally (impersonates the runtime SA via ADC).
cd website/api
npm install
npm run build
GCP_PROJECT="$PROJECT_ID" \
  STUDY_ID=paper1_irr \
  TITLE="Paper 1 — IRR baseline" \
  ALLOWLIST="coderA@uni.edu,coderB@uni.edu" \
  npm run seed
```

## 3. Deploy the Cloud Run service

```bash
cd website/api
GCIP_API_KEY="<the Identity Platform Web API key from the console>"
gcloud run deploy irr-api \
  --source . \
  --service-account="irr-runtime@${PROJECT_ID}.iam.gserviceaccount.com" \
  --set-env-vars="GCIP_API_KEY=${GCIP_API_KEY}" \
  --region="$REGION" \
  --no-allow-unauthenticated \
  --ingress=internal-and-cloud-load-balancing
```

The Firebase Hosting rewrite in `firebase.json` is the only ingress that should be allowed to invoke the service.

## 4. Deploy frontend + rules + rewrites

```bash
cd ../web
cp .env.example .env.local       # fill in the three NEXT_PUBLIC_* values
npm install
npm run build                    # static export → web/out/

cd ..
firebase login
firebase use "$PROJECT_ID"
firebase deploy --only hosting,firestore:rules,firestore:indexes
```

The hosting URL Firebase prints (`https://${PROJECT_ID}.web.app`) is the link you send to the two coders.

## 5. Daily export job

```bash
# Build the export image.
cd website/api
gcloud artifacts repositories create jobs --repository-format=docker --location="$REGION"
gcloud builds submit --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/jobs/irr-export:latest" \
  --file Dockerfile.export

gcloud run jobs create irr-export \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/jobs/irr-export:latest" \
  --service-account="irr-exporter@${PROJECT_ID}.iam.gserviceaccount.com" \
  --region="$REGION" \
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},STUDY_ID=paper1_irr"

gcloud scheduler jobs create http irr-export-nightly \
  --schedule="0 2 * * *" --location="$REGION" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/irr-export:run" \
  --oauth-service-account-email="irr-exporter@${PROJECT_ID}.iam.gserviceaccount.com" \
  --http-method=POST
```

## 6. Pull responses and run the analysis

After both coders have submitted (you can monitor `submitted` columns in the queue UI):

```bash
DATE=$(date -u +%F)
gsutil cp "gs://${PROJECT_ID}-data/exports/paper1_irr/${DATE}.json" \
    data/evaluation/human_baseline/raw_responses.json

python -m src.evaluation.merge_human_responses
python -m src.evaluation.extended_irr      # auto-detects human_scores.json
```

The 5-rater report (anthropic, google, openai, deterministic, **human**) is written to `data/evaluation/human_baseline/extended_irr_report.md`.

## 7. Reuse for Paper 2

```bash
# Build a Paper-2 stimulus packet (whatever your stimuli are).
python -m src.analysis.build_paper2_kit       # write this when ready

gsutil cp <p2_transcripts.json> \
    "gs://${PROJECT_ID}-data/studies/paper2_users/transcripts.json"

cd website/api
GCP_PROJECT="$PROJECT_ID" STUDY_ID=paper2_users \
  TITLE="Paper 2 — user evaluation" \
  INSTRUMENT="p2_user_questionnaire_v1" \
  DIMENSIONS="" \
  OPEN_TO_ANYONE=true \
  npm run seed
```

When `DIMENSIONS=""`, the backend skips integer-score validation and accepts a free-form `answers` object instead. The frontend's scoring page already detects `study.dimensions` vs `study.questions` and renders the appropriate form.

## 8. Pre-launch verification

- [ ] `curl -i https://<host>/api/healthz` returns 200.
- [ ] `firebase emulators:start --only firestore` + the Rules tab passes for: signed-in coderA can read sessions, can create their own response, cannot read coderB's response.
- [ ] Sign in as a non-allowlisted email → 403 on `/api/study/paper1_irr`.
- [ ] Submit one transcript end-to-end; the document appears in Firestore at `studies/paper1_irr/responses/{uid}__{sid}` with both `started_at` and `submitted_at`.
- [ ] Force-run the nightly export job once: `gcloud run jobs execute irr-export --region=$REGION`. A file appears in `gs://${PROJECT_ID}-data/exports/paper1_irr/`.
- [ ] Billing budget alert at €5/month is active.

## 9. Tear down

```bash
gcloud projects delete "$PROJECT_ID"
```

Firestore, Cloud Run, Identity Platform, Cloud Storage, IAM, scheduled jobs all go with the project.
