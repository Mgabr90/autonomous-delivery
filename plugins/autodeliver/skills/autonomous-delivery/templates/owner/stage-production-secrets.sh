#!/usr/bin/env bash
# ONE-TIME owner step: store production credentials that only the owner holds (mail, third-party API keys) on the
# server ahead of the go-live, so no session has to ask later. Hidden prompts; values travel over SSH stdin (never a
# command line) into a root-only file; nothing is printed or written locally. Edit SERVER/DEST and the names.
set -euo pipefail
SERVER="my-server"; DEST="/root/myproject-prod-secrets/prod.env"
out=""
for name in SMTP_URL THIRD_PARTY_API_KEY; do
  read -r -s -p "$name (empty to skip): " v; echo
  [ -n "$v" ] && out+="$name=$v"$'\n'
done
[ -z "$out" ] && { echo "nothing entered"; exit 0; }
printf '%s' "$out" | ssh "$SERVER" "set -e; umask 077; mkdir -p \"$(dirname "$DEST")\"; cat > \"$DEST.new\"; mv \"$DEST.new\" \"$DEST\"; echo stored: \$(cut -d= -f1 \"$DEST\" | tr '\\n' ' ')"
unset out v
