#!/usr/bin/env bash
# Owner, once per project: wire Azure DevOps service hooks to the Reviewer and Worker routines.
# The Fixer has no hook: the Reviewer fires it (labels fire nothing on Azure DevOps).
#
# Needs: az CLI signed in as a project admin (az login), bash, python3.
# Asks for the routine ids and fire tokens through hidden prompts; tokens never reach argv, logs or the screen.
# Generate each token at claude.ai/code/routines -> routine -> API trigger -> Generate token (shown once).
#
# Usage: ado-service-hooks.sh <org url> <project> <repo> <gate branch>
#   e.g. ado-service-hooks.sh https://dev.azure.com/acme Portal portal qa
# Optional env: BRANCH_FILTER (default: the gate branch's short name; set to refs/heads/<b> if the hook never fires),
#               ANTHROPIC_VERSION (default 2026-10-21, check the routines fire API page).
set -euo pipefail
ORG=${1:?org url}; PROJECT=${2:?project}; REPO=${3:?repo}; GATE=${4:?gate branch}
BRANCH_FILTER=${BRANCH_FILTER:-$GATE}
ANTHROPIC_VERSION=${ANTHROPIC_VERSION:-2026-10-21}
ADO=499b84ac-1321-427f-aa17-267ca6975798
FIRE=https://api.anthropic.com/v1/claude_code/routines

PID=$(az rest --resource $ADO --url "$ORG/_apis/projects/$PROJECT?api-version=7.1" --query id -o tsv)
RID=$(az rest --resource $ADO --url "$ORG/$PROJECT/_apis/git/repositories/$REPO?api-version=7.1" --query id -o tsv)
echo "project $PID, repo $RID, target-branch filter '$BRANCH_FILTER'"

read -rp  "Reviewer routine id (trig_...): " REVIEWER_ID
read -rsp "Reviewer fire token: " REVIEWER_TOKEN; echo
read -rp  "Worker routine id (trig_...): " WORKER_ID
read -rsp "Worker fire token: " WORKER_TOKEN; echo
[ ${#REVIEWER_TOKEN} -gt 20 ] && [ ${#WORKER_TOKEN} -gt 20 ] || { echo "a token looks empty"; exit 1; }

TMP=$(mktemp -d); chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT

make_sub() { # event routine_id token extra_publisher_json
  EVENT=$1 ROUTINE=$2 TOKEN=$3 EXTRA=$4 PID=$PID RID=$RID BRANCH=$BRANCH_FILTER FIRE=$FIRE VER=$ANTHROPIC_VERSION \
  python3 - > "$TMP/body.json" <<'PY'
import json, os
pub = {"projectId": os.environ["PID"], "repository": os.environ["RID"], "branch": os.environ["BRANCH"]}
pub.update(json.loads(os.environ["EXTRA"]))
print(json.dumps({
  "publisherId": "tfs", "eventType": os.environ["EVENT"], "resourceVersion": "1.0",
  "consumerId": "webHooks", "consumerActionId": "httpRequest",
  "publisherInputs": pub,
  "consumerInputs": {
    "url": f'{os.environ["FIRE"]}/{os.environ["ROUTINE"]}/fire',
    "httpHeaders": f'Authorization:Bearer {os.environ["TOKEN"]}\nanthropic-version:{os.environ["VER"]}',
    "resourceDetailsToSend": "none", "messagesToSend": "none", "detailedMessagesToSend": "none",
  }}))
PY
  chmod 600 "$TMP/body.json"
  az rest --resource $ADO --method post --url "$ORG/_apis/hooks/subscriptions?api-version=7.1" \
    --body @"$TMP/body.json" --query "{id:id,event:eventType,status:status}" -o tsv
  rm -f "$TMP/body.json"
}

make_sub git.pullrequest.created "$REVIEWER_ID" "$REVIEWER_TOKEN" '{}'
make_sub git.pullrequest.updated "$REVIEWER_ID" "$REVIEWER_TOKEN" '{"notificationType":"PushNotification"}'
make_sub git.pullrequest.merged  "$WORKER_ID"   "$WORKER_TOKEN"   '{"mergeResult":"Succeeded"}'
unset REVIEWER_TOKEN WORKER_TOKEN

cat <<EOF

Done. Next (one time, in the browser):
1. Project settings -> Service hooks: press "Test" on each new subscription; each should start a routine run that exits early.
2. claude.ai/code -> the environment -> Environment variables: add
     FIXER_ROUTINE_ID=<the Fixer's trig_ id>
     FIXER_FIRE_TOKEN=<the Fixer's fire token>
     ANTHROPIC_VERSION=$ANTHROPIC_VERSION
   (the Reviewer and the Worker's watchdog fire the Fixer with these).
EOF
