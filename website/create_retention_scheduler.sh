#!/usr/bin/env bash
set -euo pipefail
gcloud scheduler jobs create http irr-retention-monthly \
  --schedule="0 3 1 * *" \
  --location="${REGION}" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/irr-retention:run" \
  --oauth-service-account-email="irr-exporter@${PROJECT_ID}.iam.gserviceaccount.com" \
  --http-method=POST \
  --time-zone="Europe/Lisbon"
