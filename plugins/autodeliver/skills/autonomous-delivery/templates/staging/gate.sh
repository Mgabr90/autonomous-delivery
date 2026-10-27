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
# ---- Staging configuration without an operator --------------------------------------------------------------------
CFG=$ROOT/config.env   # read by the app (env_file in compose); chmod 600
CLI=$ROOT/cli.env      # read only by run-cli: secrets the app must never hold; chmod 600
APP_SECRETS="DATA_ENCRYPTION_KEYS"        # secrets the app needs (generated here, never printed)
CLI_SECRETS="EXPORT_KEY"                  # secrets only the operator CLI may hold
CLI_SCRIPTS="data:encrypt-backfill admin:data"   # app CLIs run-cli may start (package.json script names)
is_secret() { [[ " $APP_SECRETS $CLI_SECRETS " == *" ${1:-} "* ]] && [ -n "${1:-}" ]; }
secret_file() { [[ " $CLI_SECRETS " == *" ${1:-} "* ]] && echo "$CLI" || echo "$CFG"; }
gen_value() {  # how each secret is generated: edit to match your app's expected format
  case "$1" in
    DATA_ENCRYPTION_KEYS) echo "stg$(date -u +%Y%m%d):$(openssl rand -base64 32)";;
    *) openssl rand -base64 48 | tr -d '\n';;
  esac
}
config_rule() {  # allow-listed settings: bool | int:min:max | dec:min:max | slug
  case "${1:-}" in
    FEATURE_DRY_RUN|REQUIRE_DATA_ENCRYPTION|DISABLE_SIGNUPS) echo bool;;
    TRUST_PROXY_HOPS) echo int:0:5;;
    RETENTION_DAYS) echo int:1:3650;;
    QUALITY_THRESHOLD) echo dec:0:1;;
    EXPORT_BUCKET) echo slug;;
    *) return 1;;
  esac
}
config_valid() {
  local rule="$1" v="$2" min max
  case "$rule" in
    bool) [[ "$v" =~ ^(true|false)$ ]];;
    int:*) IFS=: read -r _ min max <<< "$rule"; [[ "$v" =~ ^[0-9]{1,6}$ ]] && (( 10#$v >= min && 10#$v <= max ));;
    dec:*) IFS=: read -r _ min max <<< "$rule"; [[ "$v" =~ ^[0-9]{1,4}(\.[0-9]{1,4})?$ ]] && python3 -c "import sys; sys.exit(0 if $min <= float(sys.argv[1]) <= $max else 1)" "$v";;
    slug) [[ "$v" =~ ^[a-z0-9][a-z0-9-]{2,62}$ ]];;
    *) return 1;;
  esac
}
email_ok() { [[ "${1:-}" =~ ^[A-Za-z0-9._%+-]+@example\.com$ ]]; }

case "$VERB" in
  help)
    echo "verbs: status | logs [n<=500] | logs-since [min<=1440] | upload (tgz on stdin) | deploy <sha> | verify-test-user <x@example.com> | sql-ro (SQL on stdin) | rehearsal-status|up|restore|migrate <sha>|check|down | config-show | gen-secret <NAME> | set-config <NAME> <v> | unset-config <NAME> | apply-config | run-cli <sha> <script> [args] | prune-images";;
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
    # The owner places real data ONCE; keep the copy for the final gate's restore. `shred` destroys it.
    if [ "${ARGV[1]:-}" = shred ]; then
      for f in backup.dump backup.sql; do [ -f "$ROOT/rehearsal/$f" ] && shred -u "$ROOT/rehearsal/$f"; done
      echo "rehearsal removed and the backup copy shredded"
    else echo "rehearsal removed (container, volume, network); backup copy kept (root-only) for the final gate"; fi;;
  config-show)
    touch "$CFG" "$CLI"; chmod 600 "$CFG" "$CLI"
    for f in "$CFG" "$CLI"; do
      [ "$f" = "$CFG" ] && echo "[app: config.env]" || echo "[cli only: cli.env]"
      while IFS='=' read -r k v; do [ -z "$k" ] && continue
        if is_secret "$k"; then echo "  $k = <set, fingerprint $(printf '%s' "$v" | sha256sum | cut -c1-12)>"; else echo "  $k = $v"; fi
      done < "$f"
    done;;
  gen-secret)     # generate-once; never prints the value; rotation stays operator-only
    k="${ARGV[1]:-}"; is_secret "$k" || { echo "allowed secrets: $APP_SECRETS $CLI_SECRETS"; exit 2; }
    sf="$(secret_file "$k")"; touch "$sf"; chmod 600 "$sf"
    grep -q "^$k=" "$sf" && { echo "$k already set; not overwritten (rotation is operator-only)"; exit 0; }
    val="$(gen_value "$k")"; printf '%s=%s\n' "$k" "$val" >> "$sf"
    echo "$k generated (fingerprint $(printf '%s' "$val" | sha256sum | cut -c1-12)) into $(basename "$sf")";;
  set-config)
    k="${ARGV[1]:-}"; v="${ARGV[2]:-}"; rule="$(config_rule "$k")" || { echo "not an allowed setting: $k"; exit 2; }
    config_valid "$rule" "$v" || { echo "invalid value for $k ($rule)"; exit 2; }
    touch "$CFG"; tmp="$(mktemp)"; grep -v "^$k=" "$CFG" > "$tmp" || true; printf '%s=%s\n' "$k" "$v" >> "$tmp"
    install -m 600 "$tmp" "$CFG"; rm -f "$tmp"; echo "$k = $v (applies at the next deploy or apply-config)";;
  unset-config)
    k="${ARGV[1]:-}"; config_rule "$k" >/dev/null || { echo "not an allowed setting: $k"; exit 2; }
    tmp="$(mktemp)"; grep -v "^$k=" "$CFG" > "$tmp" || true; install -m 600 "$tmp" "$CFG"; rm -f "$tmp"; echo "$k removed";;
  apply-config)   # recreate the app with the current image and config.env
    docker compose up -d app 2>&1 | tail -n 3;;
  run-cli)        # allow-listed app CLI in a throwaway container from a built image, against STAGING only
    sha_ok "${ARGV[1]:-}" || { echo "usage: run-cli <sha> <script> [args]"; exit 2; }
    script="${ARGV[2]:-}"; [[ " $CLI_SCRIPTS " == *" $script "* ]] || { echo "allowed scripts: $CLI_SCRIPTS"; exit 2; }
    args=("${ARGV[@]:3}"); [ "${#args[@]}" -le 8 ] || { echo "too many arguments"; exit 2; }
    for a in "${args[@]}"; do [[ "$a" =~ ^-{0,2}[A-Za-z0-9][A-Za-z0-9:=._/-]{0,63}$ ]] || { echo "argument not allowed: $a"; exit 2; }; done
    envf="$(mktemp)"; chmod 600 "$envf"; trap 'rm -f "$envf"' EXIT
    docker compose config --format json | python3 -c 'import json,sys; e=json.load(sys.stdin)["services"]["app"].get("environment",{}); [print(f"{k}={v}") for k,v in e.items() if v is not None and "\n" not in str(v)]' > "$envf"
    cat "$CFG" "$CLI" >> "$envf" 2>/dev/null || true
    docker run --rm --env-file "$envf" --network "$NET" --memory 1g --pids-limit 256 --security-opt no-new-privileges \
      "${IMAGE}:${ARGV[1]}-build" pnpm "$script" "${args[@]}" 2>&1 | tail -n 200;;
  prune-images)   # only this project's tags; never a global prune on a shared host
    ./prune-images.sh;;
  *)
    echo "verb not allowed: ${VERB}"; exit 2;;
esac
