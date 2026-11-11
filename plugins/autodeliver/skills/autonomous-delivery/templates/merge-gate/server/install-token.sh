#!/bin/bash
# Reads one line "MERGE_GATE_TOKEN=<token>" on stdin, stores it root-only, dry-runs the gate once,
# and turns it live only if that dry run came back clean. The owner runs it over SSH from their own
# machine (README "Run it on a server you control"), so the token never passes through a session.
set -euo pipefail
umask 077
tr -d '\r' > /etc/merge-gate/token.env.new
grep -qE '^MERGE_GATE_TOKEN=[A-Za-z0-9_.-]{20,}$' /etc/merge-gate/token.env.new || {
  rm -f /etc/merge-gate/token.env.new; echo 'Token line malformed; nothing changed.'; exit 1; }
chown root:root /etc/merge-gate/token.env.new
mv /etc/merge-gate/token.env.new /etc/merge-gate/token.env
sed -i 's/^MERGE_GATE_DRY_RUN=.*/MERGE_GATE_DRY_RUN=true/' /etc/merge-gate/config.env
since=$(date '+%Y-%m-%d %H:%M:%S')
systemctl start merge-gate.service || true
out=$(journalctl -u merge-gate.service --since "$since" --no-pager -o cat | tail -5)
echo "$out"
if grep -q ' 0 errors (dry run)' <<<"$out"; then
  sed -i 's/^MERGE_GATE_DRY_RUN=.*/MERGE_GATE_DRY_RUN=false/' /etc/merge-gate/config.env
  echo 'Dry run clean: the merge gate is now LIVE (every 10 minutes).'
else
  echo 'Dry run was not clean: the gate stays in dry-run mode. Check the token permissions.'
  exit 1
fi
