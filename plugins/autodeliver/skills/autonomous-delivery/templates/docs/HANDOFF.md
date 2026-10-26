# {{PROJECT}}: handoff (read first)

Every session reads this file before doing anything else. It is the charter: what we're doing, how we work, and what must never happen.

## Goal

{{GOAL}}

## Where things live

- Config: `.autodeliver/config.json` (mode, profiles, proof commands, gates).
- Roadmap: `{{ROADMAP}}` (phases, dependencies, done-when). Gate rows are marked **GATE**.
- Phase plans: `{{PLANS}}`. Ledgers: `{{LEDGERS}}<phase>.md` (tasks done, rulings, evidence).
- Decisions: `{{DECISIONS}}`. Evidence: `{{EVIDENCE}}<phase>/`.

## Autonomy charter

- **Decide on your own.** Don't stop to ask. Log every ruling in the ledger as `R<n> — decision — why — cost if wrong`, and index product, data or scope rulings in `{{DECISIONS}}`.
- **Quality first.** Never trade proof, review depth or verification for tokens.
- Commit and push the ledger after every task, and at least every 60 minutes.

## No dependency on the user

Sessions resolve everything themselves. The user acts only at the hard-limit gates below.

- **Visual checks:**
  - take Playwright screenshots of every touched page or rendered output, in each locale ({{LOCALES}}), at desktop and mobile widths;
  - assert layout facts in code;
  - have the `visual-checker` agent review them;
  - commit the evidence under `{{EVIDENCE}}<phase>/`.

  A FAIL is a defect: fix it.
- **Session-written translations:** a `translation-reviewer` agent pass, with the fixes made.
- **Product and policy questions:** a ruling with its cost if wrong. Prefer the safest reversible option, made configurable where that is cheap.
- **Owner-only facts** (legal name, address, hosting): derive them from the repo, docs, config and public sources, or use wording that is true without them. Never ship `TODO(user)`.
- **Stalls, caps and blockers:** the Worker takes the work over (systematic-debugging, re-plan, or split it), never the user.
- `{{DECISIONS}}` has "Open items (sessions resolve)", "Resolved by sessions" and "Hard-limit gates". Only the last is for the user.

## Hard-limit gates (the only user actions)

{{GATES_LIST}}

Prepare each gate fully so that it is a single action: gather the evidence, rehearse the runbook, and write one notice line under "Hard-limit gates".

## Hard limits (never crossed)

{{HARD_LIMITS_LIST}}

## Phase workflow (fixed order)

1. **Research, then plan.** Get a sourced brief from the `researcher` agent into `{{PLANS}}<phase>-research.md`. Then write the phase plan in `{{PLANS}}`, with tasks that each have a done-when.
2. **Each task:**
   - test-first or check-first work;
   - guard skills if available (clean-code, test, docs);
   - a per-task review;
   - a commit with its ledger line.
3. **End of phase:**
   - ONE simplify pass over the whole phase diff (its own `refactor(simplify)` commit), then the full proof: `{{PROOF_FULL}}`;
   - the final whole-phase review.
4. **Staging** (if the project has it): ship; run the phase checks; then run the **log scan**, where any error the phase caused is a Should-fix. Record the results.
5. **Evidence and write-up:**
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
  - an undelivered plan item.
- Accepted decisions (cite them) and later-phase items (cite the roadmap row) are not findings.
- **Fail safe:** never treat an unsent notice as sent, and never take an irreversible step that relies on a call that didn't happen.

## Security sweep intake

At the start of each phase, and whenever a new `{{PFX}}-SECURITY` report or `{{PFX}}-SECURITY-NOTE` lands:
- route every confirmed finding into the current phase (if it touches its area) or into the roadmap follow-ups, with a ruling;
- never drop one.

## Environment

{{ENVIRONMENT_NOTES}}
