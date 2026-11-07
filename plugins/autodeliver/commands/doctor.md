---
description: Check that the autonomous delivery setup is healthy (config, docs, agents, hooks, label, routines, webhooks, staging gate) and fix what can be fixed safely
argument-hint: "[--fix]"
---

# /autodeliver:doctor

Check each item below. Report ✅, ⚠️ or ❌ with a one-line reason. With `--fix`, repair the safe ones: create missing files from the templates, copy missing agents, re-add the label. Confirm before anything persistent outside the repo.

| # | Check |
|---|---|
| 1 | `.autodeliver/config.json` exists, parses, and has `mode`, `profiles`, `proof_full`, `gates` and `paths` |
| 2 | Every file in `paths` exists. `HANDOFF.md` has the sections "Autonomy charter", "No dependency on the user", "Hard-limit gates" and "Hard limits". `DECISIONS_LOG.md` has "Open items", "Resolved by sessions" and "Hard-limit gates". `paths.system` (default `docs/delivery/SYSTEM.md`) exists; warn if it is still the empty template after the first merged phase. |
| 3 | `CLAUDE.md` points to the HANDOFF |
| 4 | `.claude/agents/` contains `delivery-reviewer`, `delivery-fixer`, `design-reviewer`, `researcher`, `visual-checker` and `translation-reviewer`, and they match the plugin's versions (warn if they are older). With `design-reviewer`, `EGM-LICENSE.txt` is there too |
| 5 | Every `proof_full` command runs (dry: `--help` or a quick invocation where possible; otherwise say it was not run) |
| 6 | `.gitignore` covers `.autodeliver/token_log*`. No secrets are tracked (grep for common token patterns in tracked files) |
| 7 | Cloud: GitHub: the label exists (`gh label list`); Azure DevOps: `ADO_PAT` works for the repo (list PRs) and the gate branch has no policy that blocks the Reviewer's merge. Both: the remote and default branch match the config, and `docs/delivery/HOST.md` matches the host |
| 8 | Cloud: each routine in `config.routines` exists, is enabled, and has the expected model, trigger and `persist_session`. Its last run succeeded. A 404 means the wrong account may be signed in (`/login`). |
| 9 | Cloud: the triggers are attached. GitHub: the webhooks (list them if the API allows). Azure DevOps: the service-hook subscriptions to the Reviewer and the Worker exist and are `enabled` (not on probation), and the environment has `FIXER_ROUTINE_ID`, `FIXER_FIRE_TOKEN` and `ANTHROPIC_VERSION` (names only). Otherwise check that a recent PR got a `<PFX>-REVIEW` within 15 minutes. |
| 10 | Cloud: there are no stalled PRs (the same rules as `/autodeliver:status`) |
| 11 | Staging, if configured: `tools/stg.sh status` returns 2xx |
| 12 | Token log (on unless `token_log` is false): `.autodeliver/token_log.csv` gets rows after a subagent run, and Python 3 is available for the hook |
| 13 | No unfilled `{{…}}` placeholders in `docs/delivery/`, `.claude/agents/` or `CLAUDE.md` (`grep -rn "{{"`) |
| 14 | If `second_opinion.command` is set: its executable is on the PATH (locally), and a one-line dry call returns within `timeout_s`. Otherwise ⚠️ (it never blocks a verdict) |
| 15 | No open loop PR has sat at a PASS head longer than `merge.pending_after_min` (default 20). With `merge.by: pipeline`, also check that the merge pipeline's last run succeeded |
| 16 | Skills: if `.claude/skills/` holds superpowers copies, `SUPERPOWERS-LICENSE.txt` is there, and none of the excluded skills is (`subagent-driven-development`, `executing-plans`, `finishing-a-development-branch`, `using-git-worktrees`, `brainstorming`, `using-superpowers`). If superpowers is installed locally, compare its version with `.claude/skills/SUPERPOWERS-VERSION` and warn if the copies are older. If it can't compare (no plugin or no version file), say ⚠️ "not checked". Missing skills are ⚠️ only: every step has a fallback |

End with the counts of ✅, ⚠️ and ❌, plus the exact next actions for anything left ❌.
