---
description: Run the local closed loop on one task — build, independent review, fix — until PASS or the round cap, logging every round
argument-hint: "<task, file or diff range>  [--baseline]"
---

# /autodeliver:loop

Task: $ARGUMENTS

Read `.autodeliver/config.json`. If it is missing, use defaults: the profile inferred from the project, a proof from the detected test, lint and build commands, and `loop.cap` 5. Say that you used defaults, and suggest `/autodeliver:init`.

## Round 0: build

Before anything else (including for `--baseline`), write `.autodeliver/loop_state.json` as `{"loop_id": "<short slug of the task>", "round": 0}`. The token log labels each row with it, so the plan, the design review and the build count towards this loop and its budget. When the loop ends, after the final report, set `"ended": true` in the file instead of deleting it: the main session's own tokens are logged when its turn stops, and the token-log hook labels that row with this loop and then removes the file. If there is no `.autodeliver/config.json`, or `token_log` is false, the hook doesn't run: delete the file yourself.

If the task depends on external facts (library or API behaviour, versions, standards, laws, prior art), first dispatch the `researcher` agent in `brief` mode, and build from its sourced findings. Use `autodeliver:researcher` if `.claude/agents/` doesn't have it.

- Use the skills in `HANDOFF.md` "Skills" when they are available, with the overrides listed there. Never use the skills it excludes, even with the user present: `subagent-driven-development`, `executing-plans`, `finishing-a-development-branch` and `using-git-worktrees` would bypass this loop's design review and gate.
- If the task describes new work, first write a short plan (with `writing-plans` if available) with the sections in `HANDOFF.md` → "Phase workflow" step 1 (scaled to the task: design, decisions, file boundary, tasks, test plan), into `paths.plans` or `.autodeliver/plan.md` if there is no plans folder.
- **Design review before building** (skip it only for a task the user describes as trivial, and say so): dispatch the `design-reviewer` agent once per lens in `design_review.lenses` (default `zoom-out`, `comprehension`, `critic`, `readiness`), in parallel. Each brief holds only the lens, the plan path, the research brief path if any, and the round. Never send your reasoning. Resolve each Blocking and Should-fix by changing the plan or by a ruling with its cost if wrong; re-run only the lenses with findings, up to `design_review.rounds` (default 2). An open Blocking that crosses a hard limit or fails unsafe must be fixed in the plan, never ruled away. Log each round in the ledger. Use `autodeliver:design-reviewer` if `.claude/agents/` doesn't have it.
- Then build it in this session: test-first or check-first (`test-driven-development` if available), following the profile, inside the plan's file boundary.
- **Commit the build**, then **simplify once** (only for work built here, never for existing work you were pointed at). Run `/simplify <base>...HEAD` on the build's range; where it isn't available, review that diff yourself for reuse, simplification, efficiency and altitude. Commit its fixes as one `refactor(simplify)` commit, limited to files the build already changed. Don't simplify again in later rounds: fixes stay minimal.
- If it names existing work (files, a branch or a diff range), skip building.
- Record the scope precisely, after any simplify commit: the files, the range and the brief. The reviewer gets exactly this.

## Rounds 1…cap

At the start of each round, update `round` in `.autodeliver/loop_state.json` to N (same `loop_id`). Mark it ended only after the final report (see round 0).

Agent names: use `delivery-reviewer` and `delivery-fixer` if `.claude/agents/` has them (as `init` sets up). Otherwise use the plugin-scoped names, `autodeliver:delivery-reviewer` and `autodeliver:delivery-fixer`.

1. **Review.** Dispatch the `delivery-reviewer` agent with:
   - the scope;
   - the brief or plan (with its file boundary and the design-review record);
   - the round number;
   - for later rounds, the previous verdict's Blocking and Should-fix items.

   Don't review the work yourself.
2. **Parse** the first line: `VERDICT: PASS` or `VERDICT: FAIL`.
   - **PASS:** stop.
   - **FAIL:** fix exactly the Blocking and Should-fix items, either in this session (it already holds the context) or by dispatching the `delivery-fixer` agent if the config sets `"fixer": "agent"`. Then run `proof_touched`.
3. **Log the round** in the active ledger (`paths.ledgers`), or in `.autodeliver/loop-log.md` if there is no ledger: round, verdict, counts, files changed.
4. **Loop.** If a finding comes back unchanged, use systematic debugging for the root cause before the next fix.
5. **Stop guards**, checked before each new round:
   - **No progress:** stop when the same finding (same location and problem) is open for a third round, or when the number of open Blocking plus Should-fix findings hasn't fallen across two rounds in a row. More rounds of the same fix rarely converge: report it as below and propose a re-plan or a split.
   - **Budget:** if `loop.token_budget` is set, sum `input_tokens + output_tokens + cache_write_tokens` for this `loop_id` in the token log (rows from round 0 on, so the plan, design review and build count). The main session's own row is written when its turn ends, so in a single-turn loop the sum covers subagents only until then; say so when you report a budget stop. At or over the budget, stop and report. At 80%, say so in the round log. No budget is set by default; quality comes first, so a budget stops the loop and never makes the review shallower.

## At the cap, or when a stop guard fires

Stop. Report which limit stopped the loop (round cap, no progress or budget), and:
- what still fails;
- what was tried;
- the most promising next approach (re-plan, split, or a different design).

Do not mark the task done.

## `--baseline`

Build the same task once **without** the loop (no reviewer rounds), logged the same way, so the user can compare tokens and defects later (the token log captures both runs).

## Final report

- verdict and rounds;
- findings fixed per round;
- proof counts;
- evidence paths;
- tokens per role and round from `.autodeliver/token_log.csv` (on by default; skip this if the config sets `token_log` to false).
