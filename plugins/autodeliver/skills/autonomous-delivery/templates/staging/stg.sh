#!/usr/bin/env bash
# Staging client over HTTPS: https://<staging-host>/_ops/*
#   status | logs [n] | logs-since [min] | sql-ro <stdin | upload <stdin | ship | deploy <sha>
#   verify-test-user <x@example.com> | rehearsal-status|up|restore|check|down | rehearsal-migrate <sha>
#   api METHOD /api/... [curl args]   (calls the staging app; cookies persist in $STG_COOKIES)
# Auth: header $OPS_HEADER. In Claude Code cloud, a Network secret adds it for <staging-host>/_ops/ and the
# session never sees the value. Locally, export STG_OPS_TOKEN (keep it outside git).
set -euo pipefail
BASE="${STG_OPS_URL:-https://<staging-host>/_ops}"
OPS_HEADER="${OPS_HEADER:-X-Ops-Token}"
HDR=(); [ -n "${STG_OPS_TOKEN:-}" ] && HDR=(-H "${OPS_HEADER}: ${STG_OPS_TOKEN}")

call() {  # call METHOD PATH [curl args] -> prints the body, fails on non-2xx
  local m="$1" p="$2"; shift 2
  local out code
  out="$(curl -sS -X "$m" "${HDR[@]}" -w $'\n%{http_code}' "$@" "$BASE/$p")"
  code="${out##*$'\n'}"; printf '%s\n' "${out%$'\n'*}"
  [[ "$code" == 2* ]] || { echo "HTTP $code" >&2; return 1; }
}

job() {  # job VERB [QUERY] -> start a background job and poll until it is done
  local resp id state
  resp="$(call POST "$1${2:+?$2}")"; echo "$resp" >&2
  id="$(printf '%s' "$resp" | sed -n 's/.*"job": *"\([0-9a-f]*\)".*/\1/p')"
  [ -n "$id" ] || return 1
  while :; do
    sleep 10
    resp="$(call GET "jobs/$id")" || return 1
    state="$(printf '%s' "$resp" | sed -n 's/.*"state": *"\([a-z]*\)".*/\1/p')"
    [ "$state" = done ] && break
    echo "… $1 still running" >&2
  done
  python3 -c 'import json,sys; j=json.loads(sys.stdin.read()); print(j.get("output","")); sys.exit(0 if j.get("exit")==0 else 1)' <<< "$resp"
}

verb="${1:-help}"; shift || true
case "$verb" in
  status|rehearsal-status) call GET "$verb" ;;
  logs) call GET "logs?n=${1:-200}" ;;
  logs-since) call GET "logs-since?m=${1:-60}" ;;
  sql-ro) call POST sql-ro --data-binary @- ;;
  upload) call POST upload --data-binary @- -H 'Content-Type: application/gzip' ;;
  deploy|rehearsal-migrate) job "$verb" "sha=${1:?sha required}" ;;
  rehearsal-up|rehearsal-restore|rehearsal-check|rehearsal-down) job "$verb" ;;
  verify-test-user) call POST "$verb?email=${1:?email required}" ;;
  config-show) call GET config-show ;;
  gen-secret|unset-config) call POST "$verb?name=${1:?NAME required}" ;;
  set-config) call POST "set-config?name=${1:?NAME required}&value=${2:?value required}" ;;
  apply-config|prune-images) job "$verb" ;;
  run-cli) s="${1:?sha required}" c="${2:?script required}"; shift 2; a="$(IFS=,; echo "$*")"; job run-cli "sha=$s&script=$c${a:+&args=$a}" ;;
  api)
    m="${1:?method}" p="${2:?/api/... path}"; shift 2
    JAR="${STG_COOKIES:-/tmp/stg.cookies}"
    curl -sS -X "$m" "${HDR[@]}" -b "$JAR" -c "$JAR" -H 'Content-Type: application/json' -w $'\nHTTP %{http_code}\n' "$@" "$BASE/app/${p#/}" ;;
  ship)   # archive HEAD of the app directory (never dumps or .env), upload it, then deploy that sha
    ROOT="$(git rev-parse --show-toplevel)"; SHA="$(git -C "$ROOT" rev-parse --short=7 HEAD)"
    APP_DIR="${STG_APP_DIR:-.}"
    TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
    git -C "$ROOT" archive --format=tar.gz -o "$TMP/src.tgz" "HEAD:${APP_DIR#./}" 2>/dev/null || git -C "$ROOT" archive --format=tar.gz -o "$TMP/src.tgz" HEAD
    call POST upload --data-binary @"$TMP/src.tgz" -H 'Content-Type: application/gzip'
    job deploy "sha=$SHA" ;;
  *) echo "usage: stg.sh status | logs [n] | logs-since [min] | sql-ro | upload | ship | deploy <sha> | verify-test-user <email> | rehearsal-* | api METHOD /api/..." ;;
esac
