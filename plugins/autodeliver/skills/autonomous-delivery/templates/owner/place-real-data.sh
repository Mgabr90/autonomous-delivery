#!/usr/bin/env bash
# ONE-TIME owner step: place a decrypted copy of real data on the server for the rehearsal and the final restore.
# Run it yourself in a terminal: your decryption tool prompts for the passphrase; this script never sees it.
# Edit the four variables. Only the one dump file leaves your PC; local plaintext is shredded.
set -euo pipefail
ENCRYPTED="/path/to/backup.tar.gz.gpg"       # encrypted backup archive
MEMBER="backup/db/app-postgres.sql.gz"       # the one DB dump inside it
SERVER="my-server"                           # ssh host alias (root, or a user allowed to write the folder)
DEST="/opt/myproject-stg/rehearsal"          # root-only (chmod 700) folder the gate reads
T="$(mktemp -d)"; cleanup() { find "$T" -type f -exec shred -u {} + 2>/dev/null || true; rm -rf "$T"; }; trap cleanup EXIT
gpg --quiet --decrypt "$ENCRYPTED" | tar -xzf - -C "$T" "$MEMBER"
gunzip -c "$T/$MEMBER" > "$T/backup.sql"
head -c 200000 "$T/backup.sql" | grep -q "PostgreSQL database dump" || { echo "not a pg_dump file; nothing uploaded"; exit 1; }
scp -q "$T/backup.sql" "$SERVER:$DEST/backup.sql.part"
ssh "$SERVER" "set -e; cd $DEST; chmod 600 backup.sql.part; mv backup.sql.part backup.sql; ls -l backup.sql"
echo "placed; the rehearsal runs when its roadmap row is next, and the copy is kept until a verified production restore"
