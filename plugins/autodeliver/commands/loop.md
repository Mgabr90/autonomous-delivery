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
- **Design review before building** (skip it only for a task the user describes as trivial, and say so): dispatch the `design-reviewer` agent once per lens in `design_review.lenses` (default `zoom-out`, `comprehension`, `critic`, `readiness`), in parallel. Each brief holds only the lens, the plan path, the research brief path if any, the round, and the closing line "Deliver your full report as the final text of your reply.". Never send your reasoning. Resolve each Blocking and Should-fix by changing the plan or by a ruling with its cost if wrong; re-run only the lenses with findings, up to `design_review.rounds` (default 2). An open Blocking that crosses a hard limit or fails unsafe must be fixed in the plan, never ruled away. **Close the review before any build starts:** every round has run, and its plan changes and rulings are written into the plan. Never start a builder while a round is open, and never send plan amendments to a builder that is already running. Log each round in the ledger. Use `autodeliver:design-reviewer` if `.claude/agents/` doesn't have it.
- **Keep the resume note current** (the ledger's "Resume here", or `.autodeliver/loop-log.md` when there is no ledger) at each milestone, not only when a usage limit is near: each design-review round closed, each builder dispatched and returned (its worktree, branch and last commit), each gate round. Commit it each time. A session can end at a usage limit at any moment, and only what is committed lets the next session resume.
- **Model tier** (`HANDOFF.md` "Models"). This session is on a planning-tier model if its own model id contains a name in `models.plan` (default `fable`, `mythos`); if it can't tell its model, it is not. Write `Model tier: planning` or `Model tier: strong`, with the model id or `unknown`, as the first line of this loop's entry in the ledger or `.autodeliver/loop-log.md`. On a planning-tier session one thing changes in the bullets below: who builds and who simplifies. Everything else in them applies on every session: skip building for existing work, the simplify limits, record the scope.
  - **Hand the build** to one `general-purpose` subagent. Set its `model` to the family name in `models.strong` (`claude-opus-5-5` gives `opus`). Use `opus` when the field is unset, when no family name fits, or when the name is itself in `models.plan`. Never dispatch without an explicit `model`: the subagent would inherit this session's model.
  - **The build brief** has these items and none of your reasoning: the goal; the plan path; the file boundary; the hard limits and gates (from `HANDOFF.md`, or from `hard_limits` and `gates` in the config when there is no HANDOFF); build test-first or check-first, following the profile; use the skills in HANDOFF "Skills" when they are available, and never `subagent-driven-development`, `executing-plans`, `finishing-a-development-branch` or `using-git-worktrees`; run `proof_touched` with each command on its own, never through a pipe (with `| tail` the shell reports `tail`'s exit code, not the proof's), and quote its output and exit code; run every proof in the builder's own tree with its own dependency install (never a dependency folder linked from another tree, never a throwaway checkout that is force-removed after a build); commit only when that exit code is 0, staging explicit paths (never `git add -A` or `git add .`); don't push.
  - **Hand the simplify pass** to a fresh subagent of the same kind and model. Its brief: the range `<base>...HEAD`; the simplify limits in the bullet below; the hard limits and gates; run `proof_touched` the same way and quote its output and exit code; one `refactor(simplify)` commit, made only on exit code 0, staging explicit paths; don't push.
  - **Check each return** before going on: the commit exists, the changed files are inside the boundary (for the simplify pass: inside the files the build changed), and the quoted proof is green with exit code 0. The gate reruns the proof itself; this check only catches an unfinished hand-over. If a check fails, or the dispatch itself fails, send a fresh subagent the exact gap, at most twice. Then stop and report as at the cap, naming the limit as a failed hand-over. Never finish the build here.
- **Parallel builds** (local mode only, when this session hands several planned phases to builders at once):
  - each builder works in its own git worktree, made by this session or by the Agent tool's worktree isolation; the `using-git-worktrees` skill stays excluded. Each builder gets the build brief above (commit, don't push) and is dispatched and checked on return as in the bullets above, and each phase goes through its own gate;
  - **shared helpers first:** a helper that several phases need (for example a database helper or a named lock) is built first, as one small commit to an exact spec written in the plan, and the dependent phases branch from that commit;
  - **staging and the worktree folder:** before the first builder starts, make sure `.gitignore` covers the folder the worktrees live in (`.claude/worktrees/` for the Agent tool's worktree isolation). Builders stage explicit paths, never `git add -A` or `git add .`: those stage the other builders' worktrees as gitlinks;
  - **roster:** give each builder the list of the other builders (name, phase, file boundary), and let them message each other directly about interfaces, shared files, commit hashes and merge order only. Plan changes go to this session, never to another builder. A builder never edits another builder's files, never sends secrets, and never pushes or merges;
  - **cross-plan requests:** when one phase's plan asks another phase for a change (an interface, a shared file), the requesting plan's current text wins. The applying plan or builder copies that text verbatim, with its path and section, never a paraphrase, a summary or an older version; a conflict between the two plans goes to this session for a ruling;
  - **shared files:** in files that several phases edit (service units, install scripts, server config), keep one directive per concern, and write the merge rules against what the gated tests assert.
- **Quiet slot for measurements** (a performance or time-budget run on a shared machine):
  - before claiming the slot, check what is running on the machine (processes by CPU, other agent sessions); if heavy work you can't hold is running, wait or record it, never claim a quiet slot;
  - hold this session's heavy agent work for the slot's length: builders, test suites, and the gate's mutant runs;
  - each sample records machine-wide CPU, and a scenario whose other-process load passes the plan's threshold is invalid and is run again;
  - keep the slot short: only a scenario that failed a limit needs it; a scenario far below its limit is judged on its quiet samples.
- Then build it in this session: test-first or check-first (`test-driven-development` if available), following the profile, inside the plan's file boundary.
- **Commit the build** only when the proof's own exit code is 0 (each command on its own, never through a pipe; stage explicit paths), then **simplify once** (only for work built here, never for existing work you were pointed at). Run `/simplify <base>...HEAD` on the build's range; where it isn't available, review that diff yourself for reuse, simplification, efficiency and altitude. Commit its fixes as one `refactor(simplify)` commit, limited to files the build already changed. Don't simplify again in later rounds: fixes stay minimal.
- If it names existing work (files, a branch or a diff range), skip building.
- Record the scope precisely, after any simplify commit: the files, the range and the brief. The reviewer gets exactly this.

## Rounds 1…cap

At the start of each round, update `round` in `.autodeliver/loop_state.json` to N (same `loop_id`). Mark it ended only after the final report (see round 0).

Agent names: use `delivery-reviewer` and `delivery-fixer` if `.claude/agents/` has them (as `init` sets up). Otherwise use the plugin-scoped names, `autodeliver:delivery-reviewer` and `autodeliver:delivery-fixer`.

1. **Review.** Dispatch the `delivery-reviewer` agent with:
   - the scope;
   - the brief or plan (with its file boundary and the design-review record);
   - the round number;
   - for later rounds, the previous verdict's Blocking and Should-fix items;
   - the closing line "Deliver your full report as the final text of your reply.".

   Don't review the work yourself.
2. **Parse** the first line: `VERDICT: PASS` or `VERDICT: FAIL`.
   - **PASS:** stop.
   - **FAIL:** fix exactly the Blocking and Should-fix items, either in this session (it already holds the context) or by dispatching the `delivery-fixer` agent if the config sets `"fixer": "agent"` or this session is on a planning-tier model (then always the agent). Then run `proof_touched`, each command on its own and never through a pipe, and commit a fix only when its exit code is 0. A planning-tier session runs it too: it is a check, not a fix.
3. **Log the round** in the active ledger (`paths.ledgers`), or in `.autodeliver/loop-log.md` if there is no ledger: round, verdict, counts, files changed.
4. **Loop.** If a finding comes back unchanged, use systematic debugging for the root cause before the next fix.
5. **Stop guards**, checked before each new round:
   - **No progress:** stop when the same finding (same location and problem) is open for a third round, or when the number of open Blocking plus Should-fix findings hasn't fallen across two rounds in a row. More rounds of the same fix rarely converge: report it as below and propose a re-plan or a split.
   - **Budget:** if `loop.token_budget` is set, sum `input_tokens + output_tokens + cache_write_tokens` for this `loop_id` in the token log (rows from round 0 on, so the plan, design review and build count). The main session's own row is written when its turn ends, so in a single-turn loop the sum covers subagents only until then; say so when you report a budget stop. At or over the budget, stop and report. At 80%, say so in the round log. No budget is set by default; quality comes first, so a budget stops the loop and never makes the review shallower.

## At the cap, or when a stop guard fires

Stop. Report which limit stopped the loop (round cap, no progress, budget or a failed hand-over), and:
- what still fails;
- what was tried;
- the most promising next approach (re-plan, split, or a different design).

Do not mark the task done.

## `--baseline`

Build the same task once **without** the loop (no reviewer rounds), logged the same way, so the user can compare tokens and defects later (the token log captures both runs). On a planning-tier session, hand this build over the same way, with the same brief and checks.

## Final report

- verdict and rounds;
- findings fixed per round;
- proof counts;
- evidence paths;
- tokens per role and round from `.autodeliver/token_log.csv` (on by default; skip this if the config sets `token_log` to false) (a handed-over build shows as role `general-purpose`).
