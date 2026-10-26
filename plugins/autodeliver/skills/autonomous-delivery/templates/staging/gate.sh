#!/usr/bin/env bash
# Forced-command gate for the ops service's SSH key. In authorized_keys:
#   restrict,command="/opt/myproject-stg/gate.sh" ssh-ed25519 AAAA... ops
# The key can ONLY run the verbs below, scoped to this project's STAGING directory.
# Edit the variables below and the deploy/app details for your stack. Keep each verb small and validated.
set -euo pipefail
# ---- Edit these for your project -------------------------------------------------------------------------------
PROJECT=myproject                  # short name; used as a prefix for every directory, container, network and volume
ROOT=/opt/${PROJECT}-stg           # chmod 700 root; holds .env (chmod 600), compose files, deploy.sh
APP=${PROJECT}-stg-app             # app container name
DB=${PROJECT}-stg-postgres         # database container name (delete the sql-ro and rehearsal verbs if you have none)
NET=${PROJECT}-stg_internal        # internal Docker network shared by the app and the DB
IMAGE=${PROJECT}-app               # app image name; deploy.sh tags builds as ${IMAGE}:<sha>
MIGRATE_CMD=(npx prisma migrate deploy)   # your migration command, run inside the app image
# ----------------------------------------------------------------------------------------------------------------
cd "$ROOT"
read -r -a ARGV <<< "${SSH_ORIGINAL_COMMAND:-help}"
VERB="${ARGV[0]:-help}"
echo "$(date -u +%FT%TZ) ${SSH_CLIENT%% *} ${SSH_ORIGINAL_COMMAND:-}" >> "$ROOT/gate.log"
sha_ok() { [[ "${1:-}" =~ ^[0-9a-f]{7,40}$ ]]; }
email_ok() { [[ "${1:-}" =~ ^[A-Za-z0-9._%+-]+@example\.com$ ]]; }

case "$VERB" in
  help)
    echo "verbs: status | logs [n<=500] | logs-since [min<=1440] | upload (tgz on stdin) | deploy <sha> | verify-test-user <x@example.com> | sql-ro (SQL on stdin) | rehearsal-status|up|restore|migrate <sha>|check|down";;
  status)
    docker ps --filter "name=${PROJECT}-stg" --format '{{.Names}} {{.Image}} {{.Status}}';;
  logs)
    n="${ARGV[1]:-200}"; [[ "$n" =~ ^[0-9]+$ ]] && (( n <= 500 )) || n=200
    docker logs --tail "$n" "$APP" 2>&1;;
  logs-since)   # the post-deploy log scan window
    m="${ARGV[1]:-60}"; [[ "$m" =~ ^[0-9]+$ ]] && (( m >= 1 && m <= 1440 )) || m=60
    docker logs --since "${m}m" "$APP" 2>&1 | tail -n 5000;;
  upload)       # stdin = a git-archive tarball of the app (no dumps, no .env)
    head -c 200000000 > src.tgz.part && tar -tzf src.tgz.part >/dev/null && mv src.tgz.part src.tgz && echo "uploaded $(stat -c %s src.tgz) bytes";;
  deploy)
    sha_ok "${ARGV[1]:-}" || { echo "usage: deploy <git-sha>"; exit 2; }
    ./deploy.sh "${ARGV[1]}";;   # your build + migrate + restart; wrap it in any shared host lock (flock)
  verify-test-user)
    email_ok "${ARGV[1]:-}" || { echo "only @example.com test accounts"; exit 2; }
    echo "TODO(operator): mark ${ARGV[1]} verified in your app's DB"; exit 2;;
  sql-ro)       # read-only by privilege: a SELECT-only role, in a throwaway locked-down client container
    set -a; . ./.env; set +a; export PGPASSWORD="$RO_PASSWORD"   # passed by name, never in argv
    { echo "begin transaction read only;"; head -c 100000; echo; echo "rollback;"; } | \
      docker run --rm -i --network "$NET" --read-only --cap-drop ALL --security-opt no-new-privileges \
        --memory 128m --pids-limit 64 --user 65534:65534 -e PGPASSWORD postgres:16-alpine \
        psql -h "$DB" -U app_ro -d app -v ON_ERROR_STOP=1 -q;;
  # ---- Rehearsal: a throwaway DB holding a COPY OF PRODUCTION, isolated from staging. Counts only, never rows. ----
  rehearsal-status)
    docker ps -a --filter name=${PROJECT}-rehearsal --format '{{.Names}} {{.Status}}'
    [ -f "$ROOT/rehearsal/backup.dump" ] && echo "backup.dump present"; true;;
  rehearsal-up)
    install -d -m 700 "$ROOT/rehearsal"; [ -f "$ROOT/rehearsal/.pw" ] || { umask 077; openssl rand -hex 24 > "$ROOT/rehearsal/.pw"; }
    docker network inspect ${PROJECT}-rehearsal >/dev/null 2>&1 || docker network create --internal ${PROJECT}-rehearsal >/dev/null
    docker ps -a --format '{{.Names}}' | grep -qx ${PROJECT}-rehearsal-pg || {
      export POSTGRES_PASSWORD="$(cat "$ROOT/rehearsal/.pw")"
      docker run -d --name ${PROJECT}-rehearsal-pg --network ${PROJECT}-rehearsal --memory 1g --restart no \
        -e POSTGRES_DB=app -e POSTGRES_USER=app -e POSTGRES_PASSWORD -v ${PROJECT}_rehearsal_pg:/var/lib/postgresql/data postgres:16-alpine >/dev/null; }
    for i in $(seq 1 30); do docker exec ${PROJECT}-rehearsal-pg pg_isready -U app -d app >/dev/null 2>&1 && break; sleep 2; done
    docker exec ${PROJECT}-rehearsal-pg pg_isready -U app -d app;;
  rehearsal-restore)   # the OWNER places rehearsal/backup.dump (pg_dump -Fc); its presence is their consent
    [ -f "$ROOT/rehearsal/backup.dump" ] || { echo "no backup: the owner must place rehearsal/backup.dump first"; exit 2; }
    docker cp "$ROOT/rehearsal/backup.dump" ${PROJECT}-rehearsal-pg:/tmp/b.dump
    docker exec ${PROJECT}-rehearsal-pg sh -c 'pg_restore --no-owner --no-acl -U app -d app /tmp/b.dump; rc=$?; rm -f /tmp/b.dump; exit $rc' 2>&1 | tail -n 40;;
  rehearsal-migrate)
    sha_ok "${ARGV[1]:-}" || { echo "usage: rehearsal-migrate <sha>"; exit 2; }
    export DATABASE_URL="postgresql://app:$(cat "$ROOT/rehearsal/.pw")@${PROJECT}-rehearsal-pg:5432/app"
    time docker run --rm --memory 1g --network ${PROJECT}-rehearsal -e DATABASE_URL "${IMAGE}:${ARGV[1]}" "${MIGRATE_CMD[@]}" 2>&1 | tail -n 60;;
  rehearsal-check)     # aggregate checks only
    docker exec ${PROJECT}-rehearsal-pg psql -U app -d app -tAc "select relname, n_live_tup from pg_stat_user_tables order by relname";;
  rehearsal-down)
    docker rm -f ${PROJECT}-rehearsal-pg >/dev/null 2>&1 || true
    docker volume rm ${PROJECT}_rehearsal_pg >/dev/null 2>&1 || true
    docker network rm ${PROJECT}-rehearsal >/dev/null 2>&1 || true
    [ -f "$ROOT/rehearsal/backup.dump" ] && shred -u "$ROOT/rehearsal/backup.dump"
    echo "rehearsal removed (container, volume, network, backup copy)";;
  *)
    echo "verb not allowed: ${VERB}"; exit 2;;
esac
