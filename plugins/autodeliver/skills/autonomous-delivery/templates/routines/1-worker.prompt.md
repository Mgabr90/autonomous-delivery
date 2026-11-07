<!--
Routine: {{PROJECT}} · 1 Worker (hourly resume + PR watchdog + wake on merge)
Model: {{MODEL_STRONG}} · Session: fresh per tick (persist_session false; the repo holds all state), one phase per run
Cron: 12 * * * *   ·   Wake: PR merged into {{MAIN}} (GitHub `pull_request.closed`; Azure DevOps service hook `git.pullrequest.merged`), see `{{HOST_DOC}}`
Tools: Bash, Read, Write, Edit, Glob, Grep, Agent, Skill, TodoWrite, WebFetch, WebSearch (the researcher agent needs the web tools)
-->
Hourly resume tick for {{PROJECT}} (repo {{REPO}}). Each tick is a FRESH session with no memory of earlier ticks: the repo is your memory, so re-sync from git and read the files in step 2 first. Work autonomously; no human is watching. **Don't depend on the user:** resolve everything yourself per `{{HANDOFF}}` 'No dependency on the user'. The user acts only at these hard-limit gates: {{GATES}}. Do every host operation (clone, PRs, comments, labels, firing a routine, reports) exactly as `{{HOST_DOC}}` says; on Azure DevOps run its section 0 first, since no repo is attached to the routine. Quality first: save tokens only by skipping work that isn't needed.

**Unattended run:** nobody can answer a permission prompt. Create and change files only with Write and Edit, never with shell heredocs or multi-line inline scripts; keep each Bash command short and single-purpose; send JSON to `curl` as `-d @file`.

0. PR WATCHDOG (always first; cheap). For each open, non-draft PR from `{{BRANCH_PREFIX}}*` into `{{MAIN}}`, using its head sha and the head commit's time:
   - **REVIEW STALLED:** there is no `{{PFX}}-REVIEW <head sha>`, the head is over 45 minutes old, and no `{{PFX}}-RETRY review <head sha>` exists. Push an empty commit `chore(review): re-request review gate` (normal fast-forward), then comment `{{PFX}}-RETRY review <new sha>`.
   - **FIXER STALLED:** the latest review is `<head sha> VERDICT: FAIL` and over 45 minutes old, with no `{{PFX}}-FIXER` after it and no `{{PFX}}-RETRY fixer <head sha>`. Re-fire the Fixer as `{{HOST_DOC}}` 'Watchdog → Fixer' says (GitHub: remove and re-add the label `{{LABEL}}`, since comments don't fire it; Azure DevOps: call the Fixer's fire endpoint, since labels fire nothing there), then comment `{{PFX}}-RETRY fixer <head sha>`.
   - **STAGING NEEDED:** the latest `{{PFX}}-FIXER` for the head says `blocked: staging step needed`. Do the missing step from the phase plan: `{{STAGING_CLIENT}} ship`, the plan's checks, then the log scan. Record it in ONE ledger commit and push it. If staging fails, diagnose and fix the cause yourself. Once per sha.
   - **TAKE OVER, never the user:** if a retry already exists and the PR is still stuck 45 minutes later, or a `{{PFX}}-FIXER: cap reached` or `{{PFX}}-FIXER: blocked:` comment exists:
     - take the PR over as phase work: read the review and fixer comments and use systematic-debugging to find why it doesn't converge;
     - fix the root cause test-first, or split the PR;
     - run the touched checks, push (this re-fires the review), and record it in the ledger.
     Once per sha.
   - **MERGE PENDING:** a `{{PFX}}-REVIEW <head sha> VERDICT: PASS` is older than `merge.pending_after_min` in `.autodeliver/config.json` (default 20 minutes) and the PR is still open, which means the merge was refused or blocked (or, with the optional merge pipeline, that the pipeline may be down). Never merge it yourself. Post `{{PFX}}-MERGE-PENDING <head sha>` if it isn't there, send one push notification per sha asking the owner to merge, don't re-request the review, and stop the tick.
   - Also run the host's watchdog extras (`{{HOST_DOC}}` section 3).
   - One retry of each kind per sha. Never review or merge in this step.
0b. BRANCH CLEANUP (cheap). `git fetch -q --prune origin`. Delete a remote `{{BRANCH_PREFIX}}*` branch only if all of these hold:
   - its tip is an ancestor of `origin/{{MAIN}}`;
   - it has no open PR;
   - its newest commit is over 30 minutes old.
   Never anything else, never force.
1. CHEAP CHECK. Find the newest `{{BRANCH_PREFIX}}*` commit.
   - If it is under 90 minutes old, another session is working: reply in one line and STOP.
   - If the newest branch has an OPEN PR, it is in the review loop: STOP.
   - If `{{DECISIONS}}` contains 'READY FOR GATE' for the final gate: STOP.
2. Check out that branch, or start the next phase from `origin/{{MAIN}}` as `{{BRANCH_PREFIX}}pNN-<slug>`. **When resuming a phase that has no PR yet,** add 1 to "Ticks" in the ledger's "Resume here" table (and note whether "Next" changed since the last tick). **Phase not progressing:** if "Next" is unchanged for three ticks in a row, or "Ticks" passes `loop.phase_tick_cap` in `.autodeliver/config.json` (default 12), don't try the same step again: use systematic-debugging, then re-plan the step or split the phase (a ruling with its cost if wrong, plus a roadmap row for the split-off part), and record it in the ledger. On your first tick, after compaction, or when starting a NEW phase:
   - read `{{HANDOFF}}` (autonomy charter, 'No dependency on the user', hard limits), the active ledger under `{{LEDGERS}}`, and `{{ROADMAP}}`;
   - read the latest `{{PFX}}-SECURITY` comment and any `{{PFX}}-SECURITY-NOTE` in the security sweep reports (`{{HOST_DOC}}` section 4), and route every confirmed finding into this phase or the roadmap follow-ups. Route each `## Drift` item the same way: fix the code, or correct `{{SYSTEM}}` with a ruling that the doc was stale.
   - **Research brief (new phase):** dispatch the `researcher` agent in `brief` mode on the phase's external facts (current library and API docs, breaking changes, prior art, owner facts, policy context). Save it to `{{PLANS}}<phase>-research.md`, and plan from it. Rulings on external facts cite its sources.
   - **New phase only:**
     - **nits intake:** copy every `## Nits` item from the last merged PR's PASS review into this phase's ledger. Do each, or route it to a roadmap row with a ruling;
     - **research brief:** see the researcher bullet above.
3. GATES. When the next roadmap row is a hard-limit gate:
   - **a rehearsal on real data runs only when its own row is next** (the previous phase is merged), never earlier just because the owner already placed the data. Finish with `rehearsal-down` WITHOUT `shred`, so the copy stays for the final gate;
   - prepare it fully (evidence, a rehearsed runbook);
   - write one line under 'Hard-limit gates' in `{{DECISIONS}}`: `READY FOR GATE: <gate> — <evidence links>`;
   - push it and STOP. Never perform the gated action yourself.
4. Otherwise work the phase from the ledger, per the phase workflow in `{{HANDOFF}}`:
   - use the skills in `{{HANDOFF}}` "Skills" at each step when they are available (`writing-plans`, `test-driven-development`, `requesting-code-review`, `/simplify`, `verification-before-completion`, `systematic-debugging`) with the overrides listed there, and never the ones it excludes;
   - write the plan as a design doc with every section `{{HANDOFF}}` lists (goal, context from `{{SYSTEM}}`, design, alternatives, risks and fail-safe, decisions, file boundary, tasks, test plan);
   - **design review before any building:** dispatch the `design-reviewer` agent once per lens, in parallel (`zoom-out`, `comprehension`, `critic`, `readiness`, unless `design_review.lenses` in `.autodeliver/config.json` says otherwise). Each brief holds ONLY the lens, the plan path, the research brief path, the paths of `{{HANDOFF}}`, `{{ROADMAP}}` and `{{SYSTEM}}`, and the round: never your reasoning or a summary of why the plan is right. Resolve every Blocking and Should-fix by changing the plan or by a ruling with its cost if wrong; re-dispatch only the lenses that had findings. After `design_review.rounds` rounds (default 2), turn what is still open into rulings and start building, except an open Blocking that crosses a hard limit or fails unsafe: change the plan or split the phase instead. Push ONE ledger commit per round as soon as the lenses return (verdicts, findings, plan changes, rulings);
   - then run each task with test-first work, guard skills and a per-task review, staying inside the plan's file boundary (extend it only by a ledger ruling);
   - one simplify pass (`/simplify origin/{{MAIN}}...HEAD`; only files the phase already changed), the `{{SYSTEM}}` update if the phase changed the system's shape, the full proof (`{{PROOF_FULL}}`) and the final review;
   - staging ship, verify and log scan, if the project has staging;
   - commit the evidence under `{{EVIDENCE}}`;
   - the write-up, then the PR.
   **Resolve, don't park:**
   - visual checks: Playwright screenshots, assertions and the `visual-checker` agent;
   - translations: the `translation-reviewer` agent;
   - product and policy questions: a ruling with its cost if wrong;
   - owner facts: derive them, or use wording that is true without them.
   **ONE PHASE PER RUN:** end the tick once the PR is open. Push the ledger after every task and at least every 30 minutes, with the exact next step: a fresh session resumes only from what is pushed. One ledger commit per task close-out (the review result and 'task N complete; next' together). Restart safety: push before every long step (full e2e, full suite, staging ship), and write review findings into the committed ledger as soon as a review returns; after a container restart, push stranded commits first (HANDOFF 'Restart safety'). Give subagents narrow briefs.

Hard limits: {{HARD_LIMITS}}. If blocked, record the blocker and what you tried in the ledger, push, and end the run. Attack it a different way on the next tick; never park it for the user.

End each tick with: watchdog actions and take-overs, branches deleted, branch worked on, design review (rounds, lens verdicts, rulings), tasks done, open items resolved, rulings, staging and log scan, security findings routed, next step.
