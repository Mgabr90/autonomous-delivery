# Changelog

## Unreleased

Lessons from the loops of 12 to 26 November, consolidated from the open lessons branches. The rule changes below are written into every copy that carries the rule; the remaining lessons are rows in the lessons table (playbook section 10).

**Design review and the plan**

- **Measure first:** every signal the design assumes is measured on the real inputs before round 1, and a feature that depends on a measurable quality gets its spike (a minimal artifact on the real platform, or a probe of the riskiest external assumption) before the first design round; unmeasured platform facts are marked `unmeasured`, and measuring them is the first build task (HANDOFF step 1, `/autodeliver:loop`, Worker prompt, critic and readiness lenses, playbook 5a).
- **Close the design review before any build starts**, and never send plan amendments to a running builder (`/autodeliver:loop`, HANDOFF step 2, Worker prompt, playbook 5a).
- **Cut before a third patch:** a feature or rule that gets a Blocking in two design-review rounds in a row is cut by a ruling, or the cut is put to the owner; an unattended run moves it to its own roadmap row and never waits; a guard that something kept still needs is never cut (HANDOFF step 2, `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt, playbook 5a).
- **A ruling that adds a guard names its test and its mutant** (HANDOFF "Autonomy charter", `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt, readiness lens, playbook 5a).
- **Guards on irreversible or privacy-relevant acts:** the plan lists, per guard term, what can change between the check and the act and what re-checks it; an accepted residual is worded by its real-world precondition, never by one example sequence (HANDOFF step 1 "Risks and fail-safe", `design-reviewer` critic lens, playbook 5a).
- **Security state:** rate limits, lockout counters and audit de-duplication live in their own store with expiry bound to their window, never in a cache that evicts entries or applies a default timeout; a multi-step counter sequence runs in one transaction; a phase that touches authentication, authorization, rate limits, lockouts, audit records or secrets is marked security-heavy (HANDOFF step 1 and "Review gate", critic lens, `delivery-reviewer`, Reviewer prompt).
- **One ways-in table** per rule about an action, a row for every way into it, which the critic lens checks against the repo (HANDOFF step 1 "Decisions", critic lens, playbook 5a).
- **Data contract:** when the work reads data inputs, the plan decides the inputs, their shape, the point at which they freeze and where outputs go; the readiness lens checks it (HANDOFF step 1 "Decisions", `design-reviewer`, playbook 5a).
- **Cross-plan requests** are applied from the requesting plan's current text, copied verbatim (`/autodeliver:loop` "Parallel builds", HANDOFF step 1 "Context", readiness lens, playbook 5a and section 8).
- **Product facts stated once:** documents that say what the product does point to one numbered fact block, tied to the code by a claims table and a test; before the gate, an agent that did not write the documents checks each fact against the code, and the builder runs the claims sweep (`grep -niwE` for `never`, `only`, `all`, `no`, `not recorded`, `deleted`) and commits its list (HANDOFF step 1 test plan and step 4, readiness lens, `/autodeliver:loop` "Claims check" and build brief, Worker prompt, playbook 5a).
- **People-facing texts** (consent, notice and warning texts, and texts that make a promise or ask for agreement) are in the plan word for word in every locale and pass the `translation-reviewer` before the design review closes; after each fix, to the plan or the work, every people-facing sentence that depends on what changed is re-read, and each such sentence has a behaviour test (HANDOFF "No dependency on the user", test plan, steps 1 and 2 and "Review gate", `/autodeliver:loop`, `/autodeliver:design-review`, `translation-reviewer`, `delivery-fixer`, `delivery-reviewer`, Worker, Reviewer and Fixer prompts, readiness lens, playbook 5a).
- **Test plan** (HANDOFF step 1 and the `design-reviewer` readiness lens, now the same items in the same order in both; the readiness lens states each item as what the plan must have, and a missing one is a finding):
  - a traced data path and a planted-fact dry run for an output that must reflect source facts; deep links that rely on another product's undocumented search or filter clicked in the dry run; a test that personal data and credentials are stripped from data newly sent to an outside service;
  - a figure that must match numbers already sent gets the exact source query or script and its window as its spec and the sent counts as its oracle; a figure compared with an outside number or shown for every tenant gets the store's coverage and each field's distinct values and fill rate checked per tenant;
  - a change to a live system with no staging copy gets its dry-run cases and the live-vs-source check;
  - a test that pins a formula, an ordering rule or a guard condition covers each term alone, the tie-break and each filter (one case per guard term, written with the guard); each argument a caller computes for a guarded pure function has an integration-level test that fails on a plausible wrong value;
  - a seeded, model-based test with its own oracle for a privacy or safety guard over events that can be lost or reordered; worst-case-shape tests for "at most N per window" rules and a test that a cap still produces the record it must; a counter sequence tested from real concurrent threads; measurements that record machine-wide CPU per sample;
  - a test that pins a document section other files point to; a test on a file that later phases also edit asserts only the lines it owns.

**Building and the proof**

- **A check covers the rule, not one instance of it:** every value, view, layout, entry route and input method the rule or finding names is mapped to an assertion; class members are found from the output, never from a fixed list; behaviour is exercised, not presence; one mutation per distinct way the rule can break. Expected values come from the source data or a hand-written table; a new view of rendered output gets its fit, contrast and text checks before it is built; no output is written into an input folder, and inputs change only as declared changes (HANDOFF "Phase workflow" step 3, `/autodeliver:loop`, `delivery-fixer`, Worker and Fixer prompts).
- **Values the plan pins are recomputed from the data before building**, and the builder stops on a disagreement; a builder that stops because a measurement contradicts the plan is not a failed hand-over (HANDOFF step 3, `/autodeliver:loop`, Worker prompt).
- **Hard limits over files** name their file set and exceptions, and the proof scans exactly that set (HANDOFF "Hard limits", `config.md` `hard_limits`).
- **Proof runs:** a probe-gated chain (new and changed checks, then the full proof, then the mutation chain; a proof-file change restarts from the probe); each check in its own process with a time limit, where a timeout, crash or missing completeness line reads as FAIL; one proof or mutation run at a time, with the work files' hashes compared after a mutation run; after a fix, only the mutations the change touches, with the full chain once before the gate; a result names the hash manifest of the file state it ran on (HANDOFF step 3, `/autodeliver:loop`, Worker prompt).
- **Proof commands:** each command runs as its own step after the previous one has finished, never chained in one shell command, never through a pipe, never beside another heavy process; it is judged by its own exit code, and a commit is made only on exit code 0, staging explicit paths; any heap or memory flag a step needed is recorded. On a shared machine, heavy work runs one process at a time at below-normal priority, as resumable sweeps with one spec file per item (`/autodeliver:loop` build and simplify briefs, return check and fix step, HANDOFF steps 3 and 4, "Skills" and "Review gate", `delivery-reviewer`, `delivery-fixer`, Worker, Reviewer and Fixer prompts). The Reviewer routine has no below-normal-priority rule: a cloud container is not a shared machine.
- **Agents:** apart from the design-review lenses and the parallel builds of local mode, one build or fix agent at a time, the unit closest to done first; only the main session starts runs on shared infrastructure (HANDOFF "Autonomy charter", `/autodeliver:loop`, Worker prompt).
- **Own dependency install:** every tree that runs a build or a proof has its own clean install, never a dependency folder linked from another tree, and is never force-removed after a build (`/autodeliver:loop` build brief).
- **Parallel builds in local mode:** a worktree per builder, shared helpers first, a roster for direct messages between builders, explicit staging with the worktree folder git-ignored, and merge rules written against the gated tests (`/autodeliver:loop` "Parallel builds", `/autodeliver:init`, HANDOFF "Models", playbook section 8).
- **Quiet slot for measurements:** a performance or budget run on a shared machine claims a short quiet slot only after checking what is running, and the gate runs no mutants during one (HANDOFF test plan and "Review gate", `/autodeliver:loop`, `delivery-reviewer`, Reviewer prompt).
- **Live systems with no staging copy:** before go-live, a dry run on the platform's own runner with real inputs covering each changed path; after deploy, the deployed version read back and compared with the reviewed source, test switch off. Missing evidence is a Should-fix (playbook section 9, HANDOFF step 5 and "Review gate", `/autodeliver:loop` build brief, `delivery-reviewer`, Worker and Reviewer prompts).
- **Product gaps** found while writing about the product go to the roadmap as product items at once and are listed in the document's gap list and the gate notice line (HANDOFF step 3, Worker prompt).
- **A refactor or simplify pass** that moves a per-key guarantee from a query into an in-memory lookup adds a test with an item whose own key differs from the key it is looked up for (`/autodeliver:loop` simplify limits, HANDOFF step 4, Worker prompt, both reviewers).
- **Restart safety:** after a restart, or after stopping any agent that edits files before it reports, check `git status` and `git diff` and undo only what that agent left, never by a whole-file or whole-tree checkout over your own uncommitted work; files a cut-off run regenerated or mutated are restored by comparing hashes saved before the run (`/autodeliver:loop`, HANDOFF "Restart safety").
- **Resume notes** are kept current at each milestone in local runs too, not only near a usage limit (`/autodeliver:loop`, HANDOFF "Autonomy charter").

**The gate and the fixer**

- **Fixed means every part asserted:** a fixed finding with a part that no check asserts is a Should-fix; the Fixer maps each part of a finding to an assertion and reports the map and the mutations run (`delivery-reviewer`, `delivery-fixer`, Reviewer and Fixer prompts, HANDOFF "Review gate").
- **A broken proof is Blocking:** a check that crashed, timed out or is missing is a failure, and counts that don't add up (checks run against expected; mutations caught, survived and retired against those planted) are a broken proof. Every deliverable derived from the work is in scope and must match it (`delivery-reviewer`, Reviewer prompt, HANDOFF "Review gate"). HANDOFF's fail-safe rule adds: verify an upload or send at the destination before reporting it done.
- **Mutation sweeps:** in the first round that sees a formula, ordering rule or guard condition, the gate checks the whole matrix (one mutant per guard term, dropped or inverted) and reports every gap together; model-based guard tests are proven with planted leaks, and an oracle that allows more than the ruling is a Should-fix; call-site arguments of guarded pure functions are mutated, not only the function body; a security-heavy phase gets a sweep over its security code in every round. Both reviewers may run mutants only in a throwaway copy outside the work under review, never with a checkout, restore or stash in the work dir; the copy for call-site mutants has its own dependency install, runs one mutant at a time and is never force-removed recursively (`delivery-reviewer`, Reviewer prompt, HANDOFF "Review gate").
- **Closing checks:** a finding in a test or its oracle names a planted case that must fail once the fix is in, and the fixer runs it and quotes the result; a fix that adds a cap or bound tests both sides (`delivery-reviewer` and Reviewer prompt reply format, `delivery-fixer`, Fixer prompt, HANDOFF "Review gate").
- **Documents:** the gate diffs each changed document against the base branch in every round, and the fixer reads the diff of each document it edited; on one false claim the gate sweeps every changed document; a regex ban on false claims is only a smoke check (a gap in its breadth is a Nit); a sentence a fix round added that fails review twice is removed, not rewritten a third time (`delivery-reviewer`, `delivery-fixer`, Reviewer and Fixer prompts, `/autodeliver:loop` step 4, HANDOFF "Review gate").
- **Review reports are saved verbatim** in the round they arrive, one file per report in `<phase>-reviews/` beside the ledger, or `.autodeliver/reviews/` without one; each round is logged as soon as its verdict returns, and a fix made after the last round is reviewed before the work is shown (HANDOFF "Restart safety" and step 2, `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt, playbook 5a).
- **A review that stops without a verdict** (for example on a usage limit) is logged at once with the agent id, sha and reset time, and the same reviewer is resumed after the reset (a fresh review only if the head moved); it is not a round (`/autodeliver:loop`).
- **The cap report** marks each open finding as a defect in the work or a gap in the proof, with the count per round, and a stop is never a PASS (`/autodeliver:loop`, Fixer prompt).
- **Reviewer briefs end with "Deliver your full report as the final text of your reply."** (`loop.md`, `design-review.md`): in a session that is not in auto mode the hand-back tool can be refused, and reviewers then ended with no report.
- **`visual-checker` checks its blur boxes:** a table of the areas each picture must hide, a code check that the boxes cover them with a planted fault, and a zoomed look at every delivered picture before it reports.

**Existing projects:** copy the changed parts of HANDOFF ("Hard limits", "Autonomy charter", "Restart safety", "Phase workflow" steps 1 to 5 and "Review gate") into your own HANDOFF, update routines 1, 2 and 3 from the templates, and re-copy the `delivery-fixer`, `delivery-reviewer`, `design-reviewer`, `translation-reviewer` and `visual-checker` agents.

**Lessons table (playbook section 10)**

- **New rows** from loops on: live-data counts and hosted write paths; right-to-left output and review budgets; proof gaps and checks that cover the rule; AI retries, alert classifiers and output guards; base files, positional tests and role briefs; vendor data, secret locations and fork inventories; per-item recounts and rendered-chart checks; tenant-twin and report-fix loops; dry runs across units, shared types and foreign repo config; platform spikes, patch order and frozen artifacts; reconciling reported figures; unasked visible changes and dropped-column tests; source fidelity, closing owners and diagram labels; an operator shell (test paths, traps, process matching, lock waits); a skill-building loop; ops scripts; fault upkeep and reader passes; parallel multi-phase and multi-builder deliveries; guards, oracles and residuals; product claims; security state; design-review stretches; document conversion; diagram export; AI-judged mail intake; content replay and guard scope; asset scope and approvals; export resolvers; call-site arguments and refactored lookups; a parity port with third-party HTML; typed-state classification; alert endings and figures that must match numbers already sent. Also from main since 0.10.0: settings features, backfills and photo reading, data paths and deep links, a data pipeline, and writing jobs.
- **Near-duplicate rows merged into one rule each:** mutation hygiene (a scratch copy for mutants; commit your own work first; after stopping an agent, undo only its own changes, never by a whole-file or whole-tree checkout); file edits through the file-editing tool or a script file only, never a shell heredoc or a PowerShell double-quoted here-string; reference cases and counts already sent are the oracle before building; call-site arguments; proof commands (own step, exit code, no pipe, one heavy process at a time, heap flags); own dependency install per tree; reconcile disputed figures against the source; raw records before designing a rule; supersede every statement of a changed rule; a shorter proof per fix; order and precedence tests; measure and spike before the design; work folders for parallel agents; rulings made after the design closed; checks proven on known-good input.

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
