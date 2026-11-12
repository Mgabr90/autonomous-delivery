---
description: Loop metrics from the token log and the ledgers - tokens per role, round and model, rounds to PASS, findings per round, and the cost of the design review versus the gate
argument-hint: "[loop id] [--since YYYY-MM-DD] [--baseline <loop id>]"
---

# /autodeliver:report

Arguments: $ARGUMENTS

Show what the loop costs and what it catches, so the user can judge whether it pays for itself.

1. **Tokens.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/loop_report.py" <token_log_path> [--loop <id>] [--since <date>]`, using `python` if `python3` is missing. `token_log_path` comes from `.autodeliver/config.json` (default `.autodeliver/token_log.csv`). Show its Markdown as it is. If the log is missing or `token_log` is false, say so in one line and continue with step 2.
2. **Outcomes.** Read the ledgers under `paths.ledgers` (or `.autodeliver/loop-log.md`) and count:
   - per phase or loop: rounds to PASS, and Blocking and Should-fix findings per round;
   - the design review: rounds, findings per lens, and how many were resolved by changing the plan versus by a ruling;
   - findings first raised at the gate that a design-review lens could have caught (a missing decision, an unlisted file, a fail-safe gap). This is the signal for whether the design review is earning its tokens.
3. **Baseline.** With `--baseline <loop id>`, put the two loops side by side (a run made with `/autodeliver:loop --baseline` has no reviewer rounds): tokens, rounds, and defects found after the fact.
4. End with three lines:
   - the most expensive role, and whether that is expected (the reviewer running the full proof usually is);
   - the waste you can see (duplicate reviews, rounds without new findings, a lens that never finds anything);
   - one concrete suggestion under the quality-first rule: never a cheaper model or fewer checks for judgement work. Handing building or fixing from a planning-tier model to the strong tier (HANDOFF "Models") is not a cheaper model in this sense, and you may suggest it when the token log's `model` column shows the main session on a planning-tier model and no strong-tier build row.

Read-only. Never print secrets or row-level data from the project.
