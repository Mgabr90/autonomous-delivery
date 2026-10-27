# Staging access from Claude Code cloud

Cloud sessions should reach staging through a narrow HTTPS gate, never with SSH keys or broad credentials.

```
cloud session ── HTTPS + header token ──► reverse proxy /_ops/* ──► ops.py ── SSH (forced command) ──► gate.sh
```

| File | Where it runs | What it does |
|---|---|---|
| `stg.sh` | in the repo, under `tools/` | The client sessions call: `status`, `logs-since`, `ship`, `api`, `sql-ro`, `rehearsal-*` |
| `ops.py` | a small container behind your reverse proxy, route `/_ops/*` | Checks the token's sha256 against a per-client hash file, then relays an allow-listed verb over SSH |
| `gate.sh` | the host, as the forced command of the ops key | The only things the key can do, each validated |
| `prune-images.sh` | the host, next to `gate.sh` | Removes this project's old images only |

## Setup checklist

1. **Directory:** create `/opt/<project>-stg` (chmod 700, owned by root), holding a `.env` (chmod 600), the compose files and your `deploy.sh`.
2. **SSH key:** generate a key for the ops container. Add its public key to the host's `authorized_keys` as:

   ```
   restrict,command="/opt/<project>-stg/gate.sh" ssh-ed25519 …
   ```

   Pin `known_hosts`.
3. **Ops container:** run `ops.py` with no Docker socket, a read-only root filesystem and `mem_limit`. Mount `/run/ops`, containing `key`, `known_hosts` and `token_sha256`, read-only. Route `/_ops/*` to it through the reverse proxy over TLS.
4. **Tokens:** use one token per client, for example your PC and the cloud environment.
   - Store only `sha256(token)` in `token_sha256`.
   - In claude.ai/code, add a **Network secret** that sends the header to `https://<staging-host>/_ops/`.
   - Verify a token by its length and hash. Never print it.
5. **Read-only SQL:** create a role with SELECT only (`app_ro`), and put its password in `.env`.
6. **Hardening:**
   - security headers;
   - a rate limit on auth routes;
   - fail2ban;
   - no secrets in argv (`docker run -e NAME`);
   - every container under `mem_limit`;
   - no host ports.

   On a shared host, keep strict name prefixes and take the shared deploy lock.
7. **Mirror:** keep a copy of the server files in the repo under `tools/staging-ops/`, so sessions can read how staging works. Editing the copy changes nothing on the server.
8. **Test it:** call every verb once (`status`, `logs-since 5`, `rehearsal-up`, then `rehearsal-restore`, which should refuse while no backup is present, then `rehearsal-down`), and confirm nothing is left behind.

## Configure staging without an operator

New settings and secrets are the most common reason a cloud session would need a human with server access. These verbs remove that need without giving sessions code execution as root:

| Verb | What it does |
|---|---|
| `config-show` | Lists settings; secrets appear only as a fingerprint |
| `gen-secret NAME` | Generates an allow-listed secret, once, never printed. App secrets go to `config.env` (the app reads it through `env_file`); **CLI-only secrets go to `cli.env`, which the app never sees** |
| `set-config NAME VALUE` / `unset-config NAME` | Allow-listed, typed and range-checked settings (bool, int:min:max, dec:min:max, slug) |
| `apply-config` | Recreates the app with the current image and settings |
| `run-cli <sha> <script> [args]` | Runs an allow-listed app CLI (for example a backfill or export) in a throwaway container from the built image, with the app's environment, against staging only |
| `prune-images` | Removes this project's old images (keeps the running one plus 2). Also run it at the end of `deploy.sh`. Never use a global prune on a shared host |

Add to the app service in compose:

```yaml
    env_file:
      - path: ./config.env
        required: false
```

**Server file changes** (`gate.sh`, `deploy.sh`, compose, `ops.py`) stay operator-only. When a session changes the repo copy, it lists the change under **"Pending installs"** in this README, and the operator installs it during the next progress check.

**Test that every app CLI loads from the built image** (`run-cli <sha> <script> --help` or `--dry-run`). A `.dockerignore` that excludes the scripts folder silently breaks operator steps.

## Rehearsal before a cutover gate

1. `rehearsal-up`.
2. **The owner** places the decrypted dump at `rehearsal/backup.dump`. Its presence is their consent.
3. `rehearsal-restore`.
4. `rehearsal-migrate <sha>` (timed).
5. `rehearsal-check` (counts only).
6. `rehearsal-down` (removes everything and shreds the copy).

The rehearsal DB sits on an internal network that is joined to nothing else, and no verb ever returns row contents.
