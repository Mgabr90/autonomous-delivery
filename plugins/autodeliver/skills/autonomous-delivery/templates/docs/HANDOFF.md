# {{PROJECT}}: handoff (read first)

Every session reads this file before doing anything else. It is the charter: what we're doing, how we work, and what must never happen.

## Goal

{{GOAL}}

## Where things live

- Config: `.autodeliver/config.json` (mode, profiles, proof commands, gates).
- Roadmap: `{{ROADMAP}}` (phases, dependencies, done-when). Gate rows are marked **GATE**.
- Phase plans: `{{PLANS}}`. Ledgers: `{{LEDGERS}}<phase>.md` (tasks done, rulings, evidence).
- Decisions: `{{DECISIONS}}`. Evidence: `{{EVIDENCE}}<phase>/`.
- System (living doc, what is built now): `{{SYSTEM}}`.

## Autonomy charter

- **Decide on your own.** Don't stop to ask. Log every ruling in the ledger as `R<n> — decision — why — cost if wrong`, and index product, data or scope rulings in `{{DECISIONS}}`.
- **Quality first.** Never trade proof, review depth or verification for tokens.
- Commit and push the ledger after every task, and at least every 30 minutes, with the exact next step written down. Each Worker tick is a fresh session that resumes only from what is pushed. Write each task's close-out (review result plus 'task N complete; next') as ONE commit.
- **Restart safety.** The cloud container can restart at any time and kill running subagents, and a session that ends keeps only what was pushed.
  - Commit each finished step, and push before every long step: the full e2e, the full test suite, or a staging ship. While no phase PR is open, a push fires nothing. Once the PR is open, keep to one push per fix round.
  - Write review findings into the committed ledger as soon as a review returns: the full text, by id, not only in a git-ignored workspace.
  - After a restart, in order:
    1. Run `git status` and `git log origin/<branch>..HEAD`, and push any stranded commits.
    2. Check uncommitted edits before keeping them.
    3. Restart local services such as the test database.
    4. Restore files that a cut-off run regenerated.
    5. Re-run the interrupted step in full.
    6. Record the incident in the ledger.

## No dependency on the user

Sessions resolve everything themselves. The user acts only at the hard-limit gates below.

- **Visual checks:**
  - take Playwright screenshots of every touched page or rendered output, in each locale ({{LOCALES}}), at desktop and mobile widths;
  - assert layout facts in code;
  - have the `visual-checker` agent review them;
  - commit the evidence under `{{EVIDENCE}}<phase>/`.

  A FAIL is a defect: fix it.
- **Session-written translations:** a `translation-reviewer` agent pass, with the fixes made.
- **Product and policy questions:** a ruling with its cost if wrong, citing a `researcher` brief when it depends on external facts (laws, platform rules, vendor terms). Prefer the safest reversible option, made configurable where that is cheap.
- **Owner-only facts** (legal name, address, hosting): derive them from the repo, docs, config and public sources (a `researcher` brief, with sources), or use wording that is true without them. Never ship `TODO(user)`.
- **Stalls, caps and blockers:** the Worker takes the work over (systematic-debugging, re-plan, or split it), never the user.
- `{{DECISIONS}}` has "Open items (sessions resolve)", "Resolved by sessions" and "Hard-limit gates". Only the last is for the user.

## Hard-limit gates (the only user actions)

{{GATES_LIST}}

Prepare each gate fully so that it is a single action: gather the evidence, rehearse the runbook, and write one notice line under "Hard-limit gates".

**Make the owner's part one-time and early.** Give the owner the scripts in `templates/owner/`:
- real data is placed once and kept root-only until a verified final restore;
- owner-only credentials are staged in a root-only file through hidden prompts.

Then the remaining owner action is just the go-ahead in chat.

## Hard limits (never crossed)

{{HARD_LIMITS_LIST}}

## Phase workflow (fixed order)

1. **Research, then plan.** Get a sourced brief from the `researcher` agent into `{{PLANS}}<phase>-research.md`. Then write the phase plan in `{{PLANS}}<phase>-plan.md`. The plan is a design document as well as a task list, with these sections:
   - **Goal and why:** the roadmap row, the problem it solves, and what done looks like.
   - **Context:** the parts of `{{SYSTEM}}` this phase touches, and links to the research brief and the rulings it relies on. If `{{SYSTEM}}` is still the empty template, the plan's first task fills it from the code as it stands.
   - **Design:** components, interfaces and data flow, at that level only.
   - **Alternatives considered:** each with the reason it was rejected.
   - **Risks and fail-safe:** failure modes, absent services, security and privacy, rollback.
   - **Decisions:** every choice a builder would otherwise have to make (schemas, API shapes, file locations, dependencies, error handling, edge cases), each as a ruling with its cost if wrong.
   - **File boundary:** the exact repository-relative paths to create, change or delete. Use globs only for generated output. The delivery files listed under "Where things live", lockfiles and the evidence folder are exempt and need no listing.
   - **Tasks:** each with steps and a done-when. Include the end-of-phase steps below and the `{{SYSTEM}}` update when the phase changes the system's shape.
   - **Test plan:** named cases, happy path and edge cases (for non-software profiles, the profile's checks).
2. **Design review (goldfish), before any building.** Dispatch the `design-reviewer` agent once per lens, in parallel: `zoom-out`, `comprehension`, `critic` and `readiness` (or the lenses set in `design_review.lenses` in `.autodeliver/config.json`).
   - **Isolation is the point.** Each brief contains only the lens, the plan path, the research brief path, the paths of this file, the roadmap and `{{SYSTEM}}`, and the round number. Never send a summary of your reasoning, the alternatives you liked, or why you think the plan is right.
   - Resolve every Blocking and Should-fix finding yourself: change the plan, or write a ruling with its cost if wrong. Re-dispatch only the lenses that had findings, with their previous findings.
   - Stop after `design_review.rounds` rounds (default 2). Anything still open becomes a ruling with its cost if wrong, and building starts. The design review never waits for the user.
   - **Except:** an open Blocking that crosses a hard limit or makes the design fail unsafe can't be accepted by ruling. Change the plan or split the phase, even past the round cap.
   - Record each round in the ledger as ONE commit, pushed as soon as the lenses return: each lens's verdict and findings, what changed in the plan, and the rulings made.
3. **Each task:**
   - test-first or check-first work;
   - guard skills if available (clean-code, test, docs);
   - a per-task review;
   - a commit with its ledger line.
4. **End of phase:**
   - ONE simplify pass over the whole phase diff (its own `refactor(simplify)` commit), then the full proof: `{{PROOF_FULL}}`;
   - the final whole-phase review.
5. **Staging** (if the project has it): ship; run the phase checks; then run the **log scan**, where any error the phase caused is a Should-fix. Record the results.
6. **Evidence and write-up:**
   - commit the evidence;
   - update the roadmap;
   - open the PR (cloud) or run `/autodeliver:loop` (local).

## Review gate

- The gate classifies findings as Blocking, Should-fix or Nit.
- **PASS = zero Blocking, zero Should-fix, full proof green, no flaky failures.**
- These are Should-fix:
  - a flaky test;
  - missing fail-safe handling of an absent service;
  - a missing translation;
  - a `TODO(user)`;
  - a parked item;
  - an undelivered plan item;
  - a missing design-review record in the ledger;
  - a file changed outside the plan's file boundary with no ruling that extends it (delivery files, lockfiles and the evidence folder are exempt);
  - an implementation that departs from the plan's design or decisions with no ruling recording the change;
  - a change to the system's shape (components, interfaces, data, outside services) without the matching `{{SYSTEM}}` update.
- Accepted decisions (cite them) and later-phase items (cite the roadmap row) are not findings.
- **The boundary grows by ruling, not by accident.** When a task needs a file outside the boundary, add it with a ruling in the ledger (why, and the cost if wrong) before changing it. The simplify pass stays within files the phase already changed.
- **Fail safe:** never treat an unsent notice as sent, and never take an irreversible step that relies on a call that didn't happen.

## Security sweep intake

At the start of each phase, and whenever a new `{{PFX}}-SECURITY` report or `{{PFX}}-SECURITY-NOTE` lands:
- route every confirmed finding into the current phase (if it touches its area) or into the roadmap follow-ups, with a ruling;
- route each item in the report's `## Drift` section the same way: fix the code, or correct `{{SYSTEM}}` with a ruling saying the doc was stale;
- never drop one.

## Environment

- **Staging settings and secrets:** use the gate verbs (`config-show`, `gen-secret`, `set-config`, `apply-config`, `run-cli`). Don't wait for an operator.
- **Server file changes** (gate, deploy script, compose): list them under "Pending installs" in the staging README. The operator installs them.

{{ENVIRONMENT_NOTES}}
