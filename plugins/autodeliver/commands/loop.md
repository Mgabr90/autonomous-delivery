---
description: Run the local closed loop on one task — build, independent review, fix — until PASS or the round cap, logging every round
argument-hint: "<task, file or diff range>  [--baseline]"
---

# /autodeliver:loop

Task: $ARGUMENTS

Read `.autodeliver/config.json`. If it is missing, use defaults: the profile inferred from the project, a proof from the detected test, lint and build commands, and `loop.cap` 5. Say that you used defaults, and suggest `/autodeliver:init`.

## Round 0: build

- If the task describes new work, build it in this session: test-first or check-first, following the profile.
- If it names existing work (files, a branch or a diff range), skip building.
- Record the scope precisely: the files, the range and the brief. The reviewer gets exactly this.

## Rounds 1…cap

At the start of each round, write `.autodeliver/loop_state.json` as `{"loop_id": "<short slug of the task>", "round": N}`. The opt-in token log uses it to label rows. Delete the file when the loop ends.

Agent names: use `delivery-reviewer` and `delivery-fixer` if `.claude/agents/` has them (as `init` sets up). Otherwise use the plugin-scoped names, `autodeliver:delivery-reviewer` and `autodeliver:delivery-fixer`.

1. **Review.** Dispatch the `delivery-reviewer` agent with:
   - the scope;
   - the brief or plan;
   - the round number;
   - for later rounds, the previous verdict's Blocking and Should-fix items.

   Don't review the work yourself.
2. **Parse** the first line: `VERDICT: PASS` or `VERDICT: FAIL`.
   - **PASS:** stop.
   - **FAIL:** fix exactly the Blocking and Should-fix items, either in this session (it already holds the context) or by dispatching the `delivery-fixer` agent if the config sets `"fixer": "agent"`. Then run `proof_touched`.
3. **Log the round** in the active ledger (`paths.ledgers`), or in `.autodeliver/loop-log.md` if there is no ledger: round, verdict, counts, files changed.
4. **Loop.** If a finding comes back unchanged, use systematic debugging for the root cause before the next fix.

## At the cap

Stop. Report:
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
