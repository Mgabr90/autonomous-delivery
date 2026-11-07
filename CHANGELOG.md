# Changelog

## 0.6.0 (2026-11-07)

- **Design review before building**, adapted from Google's [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model) (Apache 2.0): the Worker, with full context, writes each phase plan as a design doc; fresh `design-reviewer` agents that never see its reasoning review it before anything is built.
  - **New agent `design-reviewer`** with five lenses: `zoom-out` (simplicity, YAGNI, reuse found by searching the repo), `comprehension` (a naive reader who must paraphrase the plan), `critic` (failure modes, fail-safe, security, cost), `readiness` (no design decision left to the builder, a file boundary, a test plan) and `drift` (the system doc against the code). Licence in `licenses/EGM-LICENSE.txt`.
  - **Phase plan = design doc** with fixed sections: goal, context, design, alternatives, risks and fail-safe, decisions, file boundary, tasks, test plan (HANDOFF "Phase workflow").
  - **No waiting on the user:** the Worker resolves findings by changing the plan or by a ruling; only lenses with findings re-run; after `design_review.rounds` (default 2) open items become rulings, except a Blocking that crosses a hard limit or fails unsafe. Each round is pushed to the ledger.
- **Gate checks (Reviewer routine and `delivery-reviewer`):** the file boundary (an unruled file outside it is a Should-fix; delivery files and lockfiles are exempt), design conformance, the system doc updated when the system's shape changed, and the design review recorded. Phases planned before this version are exempt. The Fixer keeps to the boundary.
- **Living system doc and drift:** `templates/docs/SYSTEM.md` (`paths.system`); the weekly security sweep adds a `## Drift` section, and the Worker routes it like security findings.
- **Commands:** `init` writes `SYSTEM.md`, copies `design-reviewer` and its licence, and adds `paths.system` and `design_review` to the config; `loop` runs the design review in round 0 for new work; `doctor` checks both.
- **Playbook:** principle 10, the design-reviewer role, the phase flowchart, and a new section 5a; `profiles.md` says what each lens looks for per profile.
- **README:** the design review, credits, and Azure DevOps in the requirements.

## 0.5.0 (2026-11-06)

- **Azure DevOps as a code host**, beside GitHub (`"host": "github" | "ado"` in the config, plus an `ado` block).
  - **Host-operations docs:** `templates/docs/HOST-github.md` and `templates/docs/HOST-ado.md`, copied to `docs/delivery/HOST.md` at init. The routine prompts now say *what* to do and point at the host doc for *how* (clone, PR list, marker comments, labels, sha-pinned merge, firing the next routine, reports, dependency alerts), so there is still one copy of each prompt.
  - **Azure DevOps plumbing:** routines with `sources: []` that clone with `$ADO_PAT`; service hooks (`git.pullrequest.created`, `.updated` PushNotification, `.merged`) call the routine fire endpoint; the Reviewer fires the Fixer itself (label changes emit no Azure DevOps event); the PR is completed with `lastMergeSourceCommit` pinned to the reviewed sha; reports go to a reports branch; dependency alerts come from the package manager's audit.
  - **Owner script** `templates/owner/ado-service-hooks.sh`: creates the service-hook subscriptions with the routine fire tokens read through hidden prompts.
  - **cloud-setup.md:** an "Azure DevOps host" section (what changes, fire endpoint facts, setup checklist, hook filters, the bootstrap block every routine needs).
  - **init, doctor, status:** detect the host from the remote, write HOST.md, check service hooks and probation, read reports from the host; init also removes connectors the server attached that the routines don't need.
- **Playbook:** six lessons (labels fire nothing on Azure DevOps; a plain clone works where the docs say GitHub only; the fire body carries no PR context; one PAT identity; no source-branch hook filter; silent hook probation).
- **Example:** `examples/ado-cloud.config.json`.

## 0.4.5 (2026-10-29)

- **Reviewer template:** merge through the REST endpoint pinned to the reviewed sha, after stating that the merge carries out the posted PASS. If the merge is blocked, post `<PFX>-MERGE-PENDING` and send a push notification, never retry another way.
- **Worker template:** a MERGE PENDING watchdog check flags a PASS left unmerged and notifies the owner. It never merges.
- **Playbook:** one lesson (a permission check blocked the gate's merge after its own PASS).

## 0.4.4 (2026-10-28)

- **Worker and HANDOFF templates:** restart safety. Push before every long step, put review findings in the committed ledger as soon as a review returns, and follow a fixed recovery order after a container restart.
- **Playbook:** two lessons (container restarts that lost work; a routine API call made from the wrong account looks like the routine is gone).

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
