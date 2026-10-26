---
description: Check that the autonomous delivery setup is healthy (config, docs, agents, hooks, label, routines, webhooks, staging gate) and fix what can be fixed safely
argument-hint: "[--fix]"
---

# /autodeliver:doctor

Check each item below. Report ✅, ⚠️ or ❌ with a one-line reason. With `--fix`, repair the safe ones: create missing files from the templates, copy missing agents, re-add the label. Confirm before anything persistent outside the repo.

| # | Check |
|---|---|
| 1 | `.autodeliver/config.json` exists, parses, and has `mode`, `profiles`, `proof_full`, `gates` and `paths` |
| 2 | Every file in `paths` exists. `HANDOFF.md` has the sections "Autonomy charter", "No dependency on the user", "Hard-limit gates" and "Hard limits". `DECISIONS_LOG.md` has "Open items", "Resolved by sessions" and "Hard-limit gates". |
| 3 | `CLAUDE.md` points to the HANDOFF |
| 4 | `.claude/agents/` contains `delivery-reviewer`, `delivery-fixer`, `researcher`, `visual-checker` and `translation-reviewer`, and they match the plugin's versions (warn if they are older) |
| 5 | Every `proof_full` command runs (dry: `--help` or a quick invocation where possible; otherwise say it was not run) |
| 6 | `.gitignore` covers `.autodeliver/token_log*`. No secrets are tracked (grep for common token patterns in tracked files) |
| 7 | Cloud: the label exists (`gh label list`), and the remote and default branch match the config |
| 8 | Cloud: each routine in `config.routines` exists, is enabled, and has the expected model, trigger and `persist_session`. Its last run succeeded. A 404 means the wrong account may be signed in (`/login`). |
| 9 | Cloud: the webhooks are attached. List them if the API allows; otherwise check that a recent PR got a `<PFX>-REVIEW` within 15 minutes. |
| 10 | Cloud: there are no stalled PRs (the same rules as `/autodeliver:status`) |
| 11 | Staging, if configured: `tools/stg.sh status` returns 2xx |
| 12 | Token log (on unless `token_log` is false): `.autodeliver/token_log.csv` gets rows after a subagent run, and Python 3 is available for the hook |
| 13 | No unfilled `{{…}}` placeholders in `docs/delivery/`, `.claude/agents/` or `CLAUDE.md` (`grep -rn "{{"`) |

End with the counts of ✅, ⚠️ and ❌, plus the exact next actions for anything left ❌.
