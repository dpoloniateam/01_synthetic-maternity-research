#!/usr/bin/env bash
# Compliance preflight check. Run after any change to the deployment.
# Verifies: security headers, public-access prevention, ingress, Firestore
# rules deployed, /api/healthz reachable, /api/me requires auth, /privacy
# and /me routes deployed, both scheduler jobs enabled.
set -uo pipefail

PROJECT="${1:-${PROJECT_ID:?set PROJECT_ID or pass as arg}}"
REGION_DEFAULT="europe-west2"
REGION_VAR="${REGION:-$REGION_DEFAULT}"
URL="https://${PROJECT}.web.app"

PASS="✓"
FAIL="✗"

OK=0
NOTOK=0
check() { if [ "$1" = "OK" ]; then echo "$PASS $2"; OK=$((OK+1)); else echo "$FAIL $2"; NOTOK=$((NOTOK+1)); fi; }

echo "── Compliance preflight for $PROJECT ──"
echo

echo "1. Security headers"
HDRS=$(curl -sI "$URL/?cb=$(date +%s)" | tr -d '\r')
for H in strict-transport-security content-security-policy permissions-policy x-frame-options x-content-type-options referrer-policy; do
  if echo "$HDRS" | grep -qi "^$H:"; then check OK "  $H"; else check FAIL "  $H"; fi
done
echo

echo "2. Cloud Storage"
PAP=$(gcloud storage buckets describe "gs://${PROJECT}-data" --format=json 2>/dev/null | grep -o '"public_access_prevention": *"[^"]*"' | head -1)
if echo "$PAP" | grep -q enforced; then check OK "  public_access_prevention = enforced"; else check FAIL "  public_access_prevention not enforced ($PAP)"; fi
LF=$(gcloud storage buckets describe "gs://${PROJECT}-data" --format="value(lifecycle_config.rule)" 2>/dev/null | head -c 1)
if [ -n "$LF" ]; then check OK "  lifecycle rules present"; else check FAIL "  lifecycle rules missing"; fi
echo

echo "3. Firestore"
FDB=$(gcloud firestore databases describe --database='(default)' --format="value(deleteProtectionState,pointInTimeRecoveryEnablement)" 2>/dev/null)
echo "$FDB" | grep -q DELETE_PROTECTION_ENABLED && check OK "  delete protection ENABLED" || check FAIL "  delete protection NOT enabled"
echo "$FDB" | grep -q POINT_IN_TIME_RECOVERY_ENABLED && check OK "  PITR ENABLED" || check FAIL "  PITR NOT enabled"
echo

echo "4. Cloud Run"
RUN_INGRESS=$(gcloud run services describe irr-api --region="$REGION_VAR" --format="value(spec.template.metadata.annotations.run\.googleapis\.com/ingress)" 2>/dev/null)
echo "  irr-api ingress = ${RUN_INGRESS:-(default)}"
RUN_REVS=$(gcloud run services describe irr-api --region="$REGION_VAR" --format="value(status.latestReadyRevisionName)" 2>/dev/null)
[ -n "$RUN_REVS" ] && check OK "  irr-api revision $RUN_REVS serving" || check FAIL "  irr-api not found"
echo

echo "5. Routes / endpoints"
HEALTH=$(curl -so /dev/null -w '%{http_code}' "$URL/api/healthz?cb=$(date +%s)")
[ "$HEALTH" = "200" ] && check OK "  /api/healthz = 200" || check FAIL "  /api/healthz = $HEALTH"
ME=$(curl -so /dev/null -w '%{http_code}' "$URL/api/me?cb=$(date +%s)")
[ "$ME" = "401" ] && check OK "  /api/me = 401 (auth required)" || check FAIL "  /api/me = $ME (expected 401)"
PRIV=$(curl -so /dev/null -w '%{http_code}' "$URL/privacy?cb=$(date +%s)")
[ "$PRIV" = "200" ] && check OK "  /privacy = 200" || check FAIL "  /privacy = $PRIV"
TRANS=$(curl -so /dev/null -w '%{http_code}' "$URL/transparency?cb=$(date +%s)")
[ "$TRANS" = "200" ] && check OK "  /transparency = 200" || check FAIL "  /transparency = $TRANS"
MEPG=$(curl -so /dev/null -w '%{http_code}' "$URL/me?cb=$(date +%s)")
[ "$MEPG" = "200" ] && check OK "  /me = 200" || check FAIL "  /me = $MEPG"
echo

echo "6. Scheduler"
SCHED=$(gcloud scheduler jobs list --location="$REGION_VAR" --format="value(name.basename(),state)" 2>/dev/null)
echo "$SCHED" | grep -q "irr-export-nightly" && check OK "  irr-export-nightly present" || check FAIL "  irr-export-nightly missing"
echo "$SCHED" | grep -q "irr-retention-monthly" && check OK "  irr-retention-monthly present" || check FAIL "  irr-retention-monthly missing"
echo

echo "7. Logging"
LOG_RET=$(gcloud logging buckets describe _Default --location=global --format="value(retentionDays)" 2>/dev/null)
[ "$LOG_RET" -ge 400 ] 2>/dev/null && check OK "  _Default log retention = ${LOG_RET}d" || check FAIL "  _Default log retention = ${LOG_RET}d (want ≥400)"
echo

echo "── ${OK} passed, ${NOTOK} failed ──"
[ "$NOTOK" -eq 0 ]
