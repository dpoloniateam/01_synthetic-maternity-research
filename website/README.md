# IRR / Paper-2 elicitation website

Two-part workspace:

- `api/` — Cloud Run service (Hono + TypeScript). Receives scoring submissions, verifies Identity Platform ID tokens, and writes to Firestore.
- `web/` — Next.js 14 app (App Router). Login, rating queue, scoring page.

The end-to-end deployment recipe — every gcloud command, IAM binding, and Firestore rule — lives in `../docs/human_irr_website.md`. The `DEPLOY.md` here is the short runbook: prerequisites, the exact order of commands, and verification checks.

The same site serves Paper 1 (two-coder IRR over 30 transcripts, 5-dimension rubric) and Paper 2 (participant elicitation with a different instrument), partitioned by `study_id` in Firestore.
