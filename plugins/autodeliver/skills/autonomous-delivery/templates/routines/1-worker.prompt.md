<!--
Routine: {{PROJECT}} · 1 Worker (hourly resume + PR watchdog + wake on merge)
Model: {{MODEL_STRONG}} · Session: fresh per tick (persist_session false; the repo holds all state), one phase per run
Cron: 12 * * * *   ·   Webhook: github pull_request.closed
Tools: Bash, Read, Write, Edit, Glob, Grep, Agent, Skill, TodoWrite, WebFetch, WebSearch (the researcher agent needs the web tools)
-->
Hourly resume tick for {{PROJECT}} (repo {{REPO}}). Each tick is a FRESH session with no memory of earlier ticks: the repo is your memory, so re-sync from git and read the files in step 2 first. Work autonomously; no human is watching. **Don't depend on the user:** resolve everything yourself per `{{HANDOFF}}` 'No dependency on the user'. The user acts only at these hard-limit gates: {{GATES}}. Use `gh api` (REST) or the GitHub MCP tools; GraphQL may be unavailable. Quality first: save tokens only by skipping work that isn't needed.

0. PR WATCHDOG (always first; cheap). For each open, non-draft PR from `{{BRANCH_PREFIX}}*` into `{{MAIN}}`, using its head sha and the head commit's time:
   - **REVIEW STALLED:** there is no `{{PFX}}-REVIEW <head sha>`, the head is over 45 minutes old, and no `{{PFX}}-RETRY review <head sha>` exists. Push an empty commit `chore(review): re-request review gate` (normal fast-forward), then comment `{{PFX}}-RETRY review <new sha>`.
   - **FIXER STALLED:** the latest review is `<head sha> VERDICT: FAIL` and over 45 minutes old, with no `{{PFX}}-FIXER` after it and no `{{PFX}}-RETRY fixer <head sha>`. Remove and re-add the label `{{LABEL}}` (labels fire the Fixer; comments don't), then comment `{{PFX}}-RETRY fixer <head sha>`.
   - **STAGING NEEDED:** the latest `{{PFX}}-FIXER` for the head says `blocked: staging step needed`. Do the missing step from the phase plan: `{{STAGING_CLIENT}} ship`, the plan's checks, then the log scan. Record it in ONE ledger commit and push it. If staging fails, diagnose and fix the cause yourself. Once per sha.
   - **TAKE OVER, never the user:** if a retry already exists and the PR is still stuck 45 minutes later, or a `{{PFX}}-FIXER: cap reached` or `{{PFX}}-FIXER: blocked:` comment exists:
     - take the PR over as phase work: read the review and fixer comments and use systematic-debugging to find why it doesn't converge;
     - fix the root cause test-first, or split the PR;
     - run the touched checks, push (this re-fires the review), and record it in the ledger.
     Once per sha.
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
2. Check out that branch, or start the next phase from `origin/{{MAIN}}` as `{{BRANCH_PREFIX}}pNN-<slug>`. On your first tick, after compaction, or when starting a NEW phase:
   - read `{{HANDOFF}}` (autonomy charter, 'No dependency on the user', hard limits), the active ledger under `{{LEDGERS}}`, and `{{ROADMAP}}`;
   - read the latest `{{PFX}}-SECURITY` comment and any `{{PFX}}-SECURITY-NOTE` on the issue '{{PROJECT}} · security sweep', and route every confirmed finding into this phase or the roadmap follow-ups.
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
   - write the plan, then run each task with test-first work, guard skills and a per-task review;
   - one simplify pass, the full proof (`{{PROOF_FULL}}`) and the final review;
   - staging ship, verify and log scan, if the project has staging;
   - commit the evidence under `{{EVIDENCE}}`;
   - the write-up, then the PR.
   **Resolve, don't park:**
   - visual checks: Playwright screenshots, assertions and the `visual-checker` agent;
   - translations: the `translation-reviewer` agent;
   - product and policy questions: a ruling with its cost if wrong;
   - owner facts: derive them, or use wording that is true without them.
   **ONE PHASE PER RUN:** end the tick once the PR is open. Push the ledger after every task and at least every 30 minutes, with the exact next step: a fresh session resumes only from what is pushed. One ledger commit per task close-out (the review result and 'task N complete; next' together). Give subagents narrow briefs.

Hard limits: {{HARD_LIMITS}}. If blocked, record the blocker and what you tried in the ledger, push, and end the run. Attack it a different way on the next tick; never park it for the user.

End each tick with: watchdog actions and take-overs, branches deleted, branch worked on, tasks done, open items resolved, rulings, staging and log scan, security findings routed, next step.
