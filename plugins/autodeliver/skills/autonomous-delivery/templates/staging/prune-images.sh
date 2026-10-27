#!/usr/bin/env bash
# Remove old STAGING images of THIS project only, keeping the running one and the 2 newest other builds.
# Never run a global `docker image prune` or `builder prune` on a shared host: other projects own those images.
set -euo pipefail
PROJECT=myproject; IMAGE=${PROJECT}-app; APP=${PROJECT}-stg-app; keep_extra=2
running="$(docker inspect -f '{{.Config.Image}}' "$APP" 2>/dev/null | sed -n "s/^${IMAGE}:\([0-9a-f]\{7,40\}\)$/\1/p" || true)"
# Final-image SHAs, newest first ("<sha>-build" twins are skipped by the regex and removed with their final image).
mapfile -t shas < <(docker images "$IMAGE" --format '{{.CreatedAt}}	{{.Tag}}' \
  | sed -n 's/^\(.*\)	\([0-9a-f]\{7,40\}\)$/\1	\2/p' | sort -r | cut -f2 | awk '!s[$0]++')
keep=("$running"); n=0
for s in "${shas[@]}"; do
  [ "$s" = "$running" ] && continue
  if [ "$n" -lt "$keep_extra" ]; then keep+=("$s"); n=$((n + 1)); fi
done
for s in "${shas[@]}"; do
  printf '%s\n' "${keep[@]}" | grep -qx "$s" && continue
  for tag in "$s" "$s-build"; do docker rmi "$IMAGE:$tag" >/dev/null 2>&1 || true; done
done
echo "kept: ${keep[*]}"
