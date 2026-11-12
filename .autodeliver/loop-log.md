# Round log

## Loop: security-audit skill in the security sweep (0.10.0), started 2026-11-12

### Design review round 1 (plan revision 1) — four lenses, all with findings

| Lens | Blocking | Should-fix | Nits |
|---|---|---|---|
| zoom-out | 0 | 5 | 4 |
| comprehension | 0 | 8 | 6 |
| critic | 1 | 6 | 4 |
| readiness | 0 | 10 | 8 |

Resolved by changing the plan (revision 2):

- **Blocking (critic): safety of an unattended full audit was unbacked.** Read the skill's README and its three workflow files; recorded what they make agents do (plan section 3). Design changes: source review only, writes only inside a git-ignored folder in the checkout, the unattended rule added to every brief, fixed settings so the skill has nothing to ask, doctor flags a sweep with no report for 8 days.
  - **Ruling D9:** no test in this loop runs the full audit unattended, because that needs a cloud routine and a target repo. Cost if wrong: a stall on a project's first unattended sweep, seen at init's hand-fired run or by doctor, and removed by deleting the vendored folder.
- Reviewer prompt allowed "vendored security" skills (three lenses): `2-reviewer.prompt.md` lines 5 and 9 now in the boundary and name the skill.
- `needs_validation` handling weakened the sweep (critic, readiness, comprehension): they are now leads the sweep verifies, checks on staging and classifies; the "owner facts" intake change is dropped.
- No behaviour for an incomplete or failed skill run, and no fallback wording: decided per case (4.1 point 7, step 5).
- Unbounded cost: profile `quick`, budget 40 agent calls (D4).
- Unpinned copy in init: one pinned commit, single source, licence from the repo root; doctor compares (D7).
- Worker and Fixer guidance-mode use: dropped (D1).
- Overrides in three places: they live once, in routine 5 (D8).
- Vendored-skills slot, ordering, Write wording, scope of `.claude/`, the "ask" wording, the two severity scales, the conditionals in the boundary, missing "how it works today", test cases: all written into revision 2.

### Design review round 2 (plan revision 2) — last round; no Blocking

| Lens | Blocking | Should-fix | Nits |
|---|---|---|---|
| zoom-out | 0 | 1 | 3 |
| comprehension | 0 | 1 | 6 |
| critic | 0 | 4 | 6 |
| readiness | 0 | 2 | 7 |

All Should-fix resolved by changing the plan (revision 3), none by ruling:

- A `quick` run that ends "complete" still leaves deferred units (zoom-out, critic): they are covered by hand or listed by name in every case.
- End states not covered (comprehension, critic): the three cases are now exhaustive (clean, usable, unusable).
- An existing project could vendor the skill while its live routine 5 is old (critic): init updates routine 5 first or does not vendor; doctor shows ❌.
- Claims wider than what was read (critic): the two validators and the eleven companion files were scanned at the pinned commit; section 3 states exactly what was read, scanned and not read.
- `git check-ignore` on a folder that does not exist yet (readiness): tested in a scratch repo; works with the trailing slash; an executed case is in the test plan.
- Routine 5's role sentence (line 7) disagreed with the new write rule (readiness): new sentence given.

Nits taken: scope excludes only `.claude/skills/` and `.autodeliver/`; a ceiling of 10 extra staging checks per sweep; "a secure-review skill" dropped on purpose; CHANGELOG contents listed; init cleanup and re-run behaviour; doctor's "no report yet"; sha grep scoped to `plugins/`.
Nit not taken: the 8-day report check stays in doctor row 16 (it is there to catch a stall caused by the skill).

### Second plan: model tiers (`plan-model-tiers.md`) — design review round 1, no Blocking

| Lens | Blocking | Should-fix | Nits |
|---|---|---|---|
| zoom-out | 0 | 4 | 4 |
| comprehension | 0 | 7 | 6 |
| critic | 0 | 9 | 5 |
| readiness | 0 | 8 | 6 |

Resolved by changing the plan (revision 2):

- No decidable test for "planning tier", and no strong tier when `models` is unset: an optional `models.plan` name list with a default; Opus when `models.strong` is unset; the tier is written in the round log.
- How a subagent is put on the strong tier: a `general-purpose` subagent with an explicit family name; never without `model`.
- The brief differed between copies and carried no hard limits or skills rules: one six-item brief, word for word.
- No behaviour when the build subagent fails: checks on return, at most two re-dispatches, then stop.
- Cloud paths (Worker take-over, staging, doctor's model check, unattended briefs): the rule is local-only in this release (M7).
- `--baseline`, `commands/report.md`, the missing `models` row in `config.md`, the build order against the first plan, exact wording for HANDOFF, the playbook and the CHANGELOG: all written in.
- The floor wording contradicted a user-chosen lower local model: reworded to "never handed to a lower model" (M4).
- The usage inspector had no signal: the token-log signal is named; M5 says what it cannot see.

Dropped from scope after review: one-line copies in `SKILL.md` and the README.

### Second plan: design review round 2 (revision 2) — last round; no Blocking

| Lens | Verdict | Should-fix | Nits |
|---|---|---|---|
| zoom-out | CLEAR | 0 | 5 |
| comprehension | FINDINGS | 3 | 7 |
| critic | FINDINGS | 4 | 6 |
| readiness | FINDINGS | 1 | 5 |

All Should-fix resolved by changing the plan (revision 3), none by ruling:

- The brief relied on a HANDOFF that a local loop may not have (critic): it now states hard limits and gates, test-first working and the four excluded skills itself (M10).
- "The next bullets apply as written" left the planning-tier case undefined (comprehension, critic): only who builds and who simplifies changes; the rest applies on every session.
- The simplify hand-over had no brief or return check (comprehension, critic): both written.
- `models.strong` could name a planning-tier model (critic): hand-overs then use Opus.
- The inspector's token-log signal misfired both ways (critic): reworded ("built new work", "on a model outside `models.plan`", "may indicate").
- "First line of the round log" named no real place (comprehension): place and line format given.
- The `models.plan` grep failed against the prescribed `config.md` row (readiness): the literal is in the row.

Nits taken: the steps live once, in `loop.md`, and HANDOFF carries the rule and a pointer (M9); a fourth stop reason "failed hand-over"; the planning session still runs `proof_touched` after a fix; "for that work" in the inspector text; the cloud-setup table named; a CHANGELOG line for existing projects; a reason for `mythos` in the default.
Nit not taken: the inspector paragraph stays identical in the cloud copy, where its token-log half cannot apply (M11).

### Build 1 (first plan) — commit `6899444`, by an Opus subagent; its own proof green

- 12 files, all inside the boundary. Not pushed.
- **Found by the builder, outside what the plan foresaw:** `git check-ignore -q .autodeliver/security-audit/` exits 0 on the owner's machine in a repo with no ignore entry at all, because of a line in the machine-wide ignore file. Doctor would pass while a cloud sweep, which has no such file, skips the skill. Confirmed here: exit 0 plain, exit 1 with `-c core.excludesFile=`.
  - **Ruling:** the check becomes `git -c core.excludesFile= check-ignore -q .autodeliver/security-audit/` in routine 5 and doctor (plan decision D5a). Cost if wrong: none seen; the form was tested both ways in a scratch repo.
- Small wording departures the builder reported (bullet letters (a) to (g) added to routine 5; the test record left out of the prompt; "write no run files" added to the fallback): accepted, they follow the plan's intent. The gate judges them.

### Build 2 — commits `6eafd2b` (the ignore-check fix) and `c09f3a6` (second plan), by an Opus subagent; its own proof green

- Fix: 2 files. Second plan: 9 files, all inside its boundary. 17 files changed against `main` in total. Not pushed.
- The builder compared every fenced block and quoted sentence of the plan with the built files: 18 checks, 0 differences. Reported departures: list indentation in `loop.md`, a parenthesis placed before the full stop, CHANGELOG sub-bullets worded from the plan's list.

### Review gate round 1 — VERDICT: PASS (0 Blocking, 0 Should-fix, 5 Nits), full proof green

- Scope `main..HEAD`, 3 commits, 17 files. The reviewer ran the whole proof itself (plugin validation twice, 44 merge-gate tests, compile and syntax checks, and every CI grep and smoke test by hand), every read-through case of both plans (18 + 5 + 12), and its own fact-check against a clone of the upstream skill at the pinned commit.
- Nit taken after the gate: the CHANGELOG's "Existing projects" line now also says to add the ignore entry.
- Nits left: two back-to-back parentheses (routine 5, `loop.md`); the roles table's "Changes anything" for the sweep (outside the boundary); bullet (e) cannot start before (d) returns (as before this change); doctor's fixed host-doc path (existing convention).
- Unverified by anyone: that a handed-over build's token-log row is labelled `general-purpose` (no real log with subagent rows on this machine).

## Lessons

What the gate or the reviews caught that the plan, the build or the proof should have caught:

1. **A check that passed for the wrong reason.** The first plan's ignore check was tested only in the passing direction, on a machine whose machine-wide ignore file made it pass everywhere. The builder found it; no reviewer could, because none ran it without the entry. → Playbook lesson added; the check now reads only the repo's own rules.
2. **Safety claims wider than what was read.** The first draft claimed the third-party skill was safe to run unattended from its top file alone. The critic made it Blocking. → Playbook lesson added.
3. **A skill for one role, open to all.** Three lenses found that the Reviewer prompt already allowed vendored security skills. → Playbook lesson added.
4. **Summaries where exact text was needed.** Both plans lost a round to "the builder would be writing the rule", and text added between rounds drew most of round 2's findings. → Playbook lesson added.

Steps that cost more than they gave (this project only, not merged into the playbook):

- The second request arrived mid-loop and shared files with the first. Two plans, built one after the other on one branch and gated together, worked; stating the build order in the second plan from its first draft would have saved four findings.
- Sixteen design-review runs for two plans. Round 2 ran every lens because every lens had findings; for the second plan the zoom-out lens came back clear, so a narrower first draft would have let it be skipped.

Rules that were missing or unclear: none in the loop itself. The local loop had no rule for which model builds; that is the second plan.

### Earlier nits, first plan (round 1)

Nits taken: version file now checked by doctor; "Measure it" sentence; done-when lines; dedupe rule in step 3; local Node check dropped.
