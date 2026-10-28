# Changelog

## 0.4.3 (2026-10-28)

- **Fixer template:** answers the union of every FAIL review on the current head, not only the latest, and lists the review ids it answered.
- **Reviewer template:** a claim step (`<PFX>-REVIEW-CLAIM <sha>`, expires after 30 minutes) that stops a duplicate run before it reviews. The step-7 guard still stops a duplicate post.
- **Worker and HANDOFF templates:** one ledger commit per task close-out.
- **cloud-setup.md:** always `get` and edit the live routine prompt; never rebuild it from an older copy.
- **Playbook:** two lessons (duplicate reviews reaching the Fixer; a stale-copy update reverting another session's changes).

## 0.4.2 (2026-10-27)

- **Reviewer template:** a duplicate guard. Before posting, it re-checks for a review of the same sha and for a moved head, so two webhook events on one PR produce one review.
- **Fresh sessions everywhere:**
  - `cloud-setup.md` now sets `persist_session: false` for the Worker too, with the reason;
  - the Worker and HANDOFF templates push the ledger at least every 30 minutes, with the exact next step.
- **Usage-inspector template:** a Worker fresh-run health check (tick time, resume gaps, lost work, ledger cadence, merged branches left behind) and duplicate-review detection, replacing the session-size check.
- **Playbook:** two lessons (a persistent Worker blocking cleanup; duplicate reviews from two webhook events).

## 0.4.1 (2026-10-27)

- **Roadmap template:** a production-readiness phase (capacity plan, encrypted backups with a restore test, a production-watch routine, a dependency batch) and a rehearsal row, both before the go-live gate.
- **Playbook:** the guidance and a lesson for this; the rehearsal text now keeps the data copy until the final restore.

## 0.4.0 (2026-10-27)

- **Owner steps made one-time and early:** `templates/owner/place-real-data.sh` (hidden decryption prompt, a single dump uploaded root-only) and `templates/owner/stage-production-secrets.sh` (hidden prompts into a root-only file).
- **Staging gate:** `rehearsal-down` keeps the real-data copy for the final restore (`shred` destroys it).
- **Worker template:**
  - a fresh session per tick;
  - nits from the last PASS are carried into the next phase;
  - a rehearsal runs only when its own roadmap row is next.
- **Reviewer template:**
  - e2e on every PASS when the whole PR touches the UI;
  - operator CLIs must load from the built image;
  - nits listed precisely.
- **Playbook:** five new lessons, and the gates guidance updated.

## 0.3.0 (2026-10-27)

- **Staging kit: configuration without an operator.**
  - New gate verbs `config-show`, `gen-secret` (generate-once, never printed), `set-config` / `unset-config` (allow-listed, typed and range-checked), `apply-config`, `run-cli` (allow-listed app CLIs in a throwaway container) and `prune-images`.
  - Two env files: `config.env` for the app and a CLI-only `cli.env`.
  - `prune-images.sh` removes only this project's images.
  - The ops service and client support the new verbs.
- **The "Pending installs" convention** for server-file changes that only an operator may install.
- **Playbook:** five new lessons (operator dependency, CLI-only secrets, disk growth on shared hosts, CLIs missing from images, pending installs).

## 0.2.0 (2026-10-26)

- **New agent `researcher`:**
  - `brief` mode: sourced facts before a phase or task;
  - `fact-check` mode: verifies the claims in docs, plans and PRs;
  - every claim carries a URL, date and quote, or is marked UNVERIFIED; read-only, and never decides.
- **Wired in:**
  - the Worker runs a research brief at each new phase;
  - the Reviewer and `delivery-reviewer` fact-check docs, research and fact-asserting PRs;
  - `/autodeliver:loop` researches first when a task depends on external facts;
  - the docs and research profiles use the fact-check as proof;
  - `init` and `doctor` include the new agent.

## 0.1.0 (2026-10-26)

First public release.
- **Commands:** `/autodeliver:init`, `/autodeliver:loop`, `/autodeliver:status` and `/autodeliver:doctor`.
- **Agents:** `delivery-reviewer`, `delivery-fixer`, `visual-checker`, `translation-reviewer` and `usage-inspector`.
- **Skill:** `autonomous-delivery`, with the playbook, the profiles (software, docs, data, infra, migration, research), and config and cloud-setup references.
- **Templates:** the five cloud routine prompts (Worker, Reviewer, Fixer, Usage inspector, Security sweep), the charter docs, and the staging ops gate.
- **Token log:** records token usage per role and round. It is on by default in new configs; set `"token_log": false` to turn it off.
- **Community:** issue and PR templates, a Code of Conduct, the CI validate workflow, and the plugin icon.
- **Docs:** GitHub trigger filters, the supported events, and dropped-event limits (cloud setup and lessons).
