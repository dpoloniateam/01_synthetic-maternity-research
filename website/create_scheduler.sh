#!/usr/bin/env bash
set -euo pipefail
gcloud scheduler jobs create http irr-export-nightly \
  --schedule="0 2 * * *" \
  --location="${REGION}" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/irr-export:run" \
  --oauth-service-account-email="irr-exporter@${PROJECT_ID}.iam.gserviceaccount.com" \
  --http-method=POST \
  --time-zone="Europe/Lisbon"
