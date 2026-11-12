# Changelog

## 0.10.0 (2026-11-12)

- **The security sweep uses Cloudflare's `security-audit` skill** ([cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), MIT) when the project has it in `.claude/skills/`. It covers the sweep's first two bullets (entry points and their guards; auth, crypto, secrets, injection, uploads, SSRF). Without it, or without Node.js, or when its output folder is not git-ignored, the sweep does those bullets by hand as before and says why.
  - Fixed settings in routine 5, so the skill has nothing to ask: full audit, profile `quick`, a budget of 40 agent calls, source review only (no target code run, nothing installed), run files only under the git-ignored `.autodeliver/security-audit/`.
  - Its records are leads. The sweep verifies them, checks them on staging and classifies them by its own scale. `needs_validation` records are never dropped for having no severity; at most 10 of them are checked on staging per sweep. A failed validator or an unfinished run falls back to work by hand for what the records do not cover.
  - Still one `<PFX>-SECURITY` report, now saying whether the skill ran and how it ended.
- **No other role uses it.** HANDOFF "Skills" says so for the Worker, Fixer and local loop, and the Reviewer prompt names it among the skills the gate never uses.
- **`init`** (cloud mode) offers to copy the skill from the pinned commit `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`, with its licence and a `SECURITY-AUDIT-VERSION` file, and always adds `.autodeliver/security-audit/` to `.gitignore`. **`doctor`** checks the copy: ❌ when the live routine 5 predates these rules; ⚠️ for missing files, another version, the folder not ignored, or no sweep report for 8 days.
- **Existing projects:** update routine 5 before adding the skill, and add `.autodeliver/security-audit/` to `.gitignore` (without that line the sweep does not run the skill).
- **Playbook:** four lessons (a check that passed only because of a machine-wide git ignore file; safety claims about a third-party skill that rested on its top file; a skill copied for one role that every role could use; exact rule text in the plan from the first draft).
- **A planning-tier model plans; the strong tier builds** (local sessions; HANDOFF "Models", playbook section 11, `/autodeliver:loop`):
  - a session whose model id matches `models.plan` (new, optional; default `fable`, `mythos`) keeps planning, rulings and checks, and hands the build, the simplify pass and every fix to strong-tier subagents;
  - a fixed brief that carries the hard limits, test-first working and the excluded skills, an explicit `model` on every dispatch, checks on return, and at most two re-dispatches before the loop stops;
  - the strong tier is the floor, and the usage inspector and `/autodeliver:report` may suggest the hand-over;
  - cloud routines keep their tiers;
  - existing projects: copy the "Models" section from the HANDOFF template into your own HANDOFF.

## 0.9.1 (2026-11-11)

- **Merge gate on a server you control:** `templates/merge-gate/server/` adds a systemd timer and service for `merge_gate.py`. They run every 10 minutes as an unprivileged user with a memory cap, and add no ports, no containers and no CI minutes.
  - `install-token.sh` takes the owner's token over SSH on stdin, stores it root-only, dry-runs once, and goes live only on a clean run.
  - The README has the install steps and a check against real PR history.
- **Worker template:** the MERGE PENDING stop now runs the branch cleanup first.
- **Playbook:** three lessons (a PASS left unmerged for 13 days on a missed notice; cleanup skipped by the early stop; an idle hourly Worker while the loop waits on the owner).
- **cloud-setup.md and config.md:** the server option, and `merge.pending_after_min` of about 30 for it.

## 0.9.0 (2026-11-07)

- **Superpowers and `/simplify` built into the steps** (HANDOFF "Skills", playbook section 5b). They are used when available, and each step falls back to the playbook's own text:
  - `writing-plans` writes the phase plan, kept in our format, and answers its execution question itself;
  - `test-driven-development` for each task, and `requesting-code-review` for the per-task review;
  - Claude Code's `/simplify` is the one simplify pass per phase (and runs once before review round 1 in `/autodeliver:loop`);
  - `verification-before-completion` before anything is called done;
  - the Fixer uses `receiving-code-review`;
  - `systematic-debugging` as before.
- **Guardrails:**
  - Never used: `subagent-driven-development` and `executing-plans`, which bypass the build, ledger and design review, and `finishing-a-development-branch` and `using-git-worktrees`, which merge or move work outside the gate.
  - `brainstorming` and `using-superpowers` are used only at `init`, where the owner is present.
  - `writing-plans` runs without its execution handoff.
  - "Ask your human partner" becomes a ledger ruling, and the design review replaces a skill's human plan review.
  - Skill severities map to Blocking, Should-fix and Nit.
  - The Reviewer uses none of these skills.
  - When a skill and HANDOFF disagree, HANDOFF wins.
- **`init`** offers to copy the unattended-safe superpowers skills into `.claude/skills/` for cloud sessions, with their MIT licence and a `SUPERPOWERS-VERSION` file. **`doctor`** checks the copies: licence present, no excluded skills, and version up to date when it can compare.
- **`/simplify` always gets an explicit range**, because its default diff can be empty on a pushed branch. In `/autodeliver:loop` it runs only on work built in that loop, after the build is committed.

## 0.8.0 (2026-11-07)

- **Unattended runs never wait on a permission prompt:** every routine prompt now forbids shell heredocs and multi-line inline scripts, keeps Bash commands short and single-purpose, and sends JSON to `curl` as `-d @file`. Shell heredocs had raised a prompt nobody could answer, which stalled runs. The Reviewer, usage inspector and security sweep now have Write, for request bodies and report files only. The Azure DevOps host doc states the `-d @file` convention once, for every call. CI checks that every prompt carries the rule.
- **Optional merge pipeline** (`templates/merge-gate/`, off by default, `"merge": {"by": "pipeline"}`): a workaround for when cloud permission checks keep refusing the Reviewer's own merge. A scheduled Azure Pipeline or GitHub Actions workflow, in a repo the routines never write to, completes only PRs whose current head has a trusted `<PFX>-REVIEW <sha> VERDICT: PASS` and no trusted FAIL, pinned to that sha. It skips forks, carries on past a refused merge, and fetches comments and mergeability only when needed. It has a dry-run default, stdlib-only code, and 44 tests. The default stays as it was: the Reviewer merges, or posts MERGE-PENDING for the owner.
- **`merge.pending_after_min`** (default 20): one setting for how long a PASS head may stay open before the Worker and `doctor` flag it.
- **Reviewer template:** the verdict line carries the full 40-character head sha.
- **cloud-setup.md:** a section on unattended runs (permission prompts, refused merges, the official org-managed fix, and the API dropping unknown `job_config` fields). Playbook: one new lesson (heredoc prompts), and the refused-merge lesson now names the official fix and the option. `init` mentions the option. CI runs the gate tests.
- **Playbook:** the plan-completeness lesson now says "15 of 21 done (2 partial, 4 not done)".

## 0.7.0 (2026-11-07)

- **Try it without setup:**
  - `/autodeliver:review [scope] [--fix] [--comment]` runs the independent gate once on the current changes, a branch, a PR or files. It detects the proof commands when there is no config.
  - `/autodeliver:design-review <doc> [--lens …] [--drift]` runs the four fresh-eyes lenses on any plan, spec or RFC, and writes a merged report beside it.
- **Loop metrics** (#3): `/autodeliver:report` and `scripts/loop_report.py`: tokens per loop, role, round and model from the token log, plus rounds to PASS, findings per round and design-review yield from the ledgers.
- **Stop guards** (#2): the local loop stops on no progress (the same finding open a third time, or no fall in open findings across two rounds) and at an optional `loop.token_budget`. In the cloud, the Worker re-plans or splits a phase whose ledger hasn't moved for three ticks or that passes `loop.phase_tick_cap` (default 12).
- **Optional second opinion** (#1): `second_opinion.command` runs another vendor's CLI on the diff; the gate verifies every item itself, and a failure never blocks a verdict. `doctor` checks it.
- **CI:** compiles and smoke-tests the report script.
- **Review fixes before release:** the report script never crashes (BOM, non-UTF-8, non-finite numbers, a folder path); the loop labels its tokens from round 0 so the budget and report include the plan, design review and build; the Worker's no-progress check moved to the resume step with a "Ticks" row in the ledger; ad-hoc reviews skip plan-based checks and include untracked files; the second-opinion tool is time-limited and checked for file changes (an edit is a Blocking safety finding). The loop marks its state file ended instead of deleting it, and the token-log hook labels the main session's last row before removing it, so `--baseline` and per-loop totals include the main session.
- **Repo:** `.github/assets/social-preview.png`, the source of the repository's social preview card.

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
