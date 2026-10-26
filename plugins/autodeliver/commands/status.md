---
description: Report delivery progress — roadmap phases, open PRs and review verdicts, open items, gates waiting for the owner, and (cloud) routine runs
argument-hint: "[--brief]"
---

# /autodeliver:status

Read `.autodeliver/config.json` and the files in `paths`. Produce a concise report. With `--brief`, give five lines at most.

1. **Phases:** from `ROADMAP.md`, give done, in progress and next. For the active phase, give the ledger's "Resume here" block and the last three entries.
2. **Loop** (cloud mode, via `gh api` REST):
   - open and recently merged PRs from `branch_prefix` into `main_branch`;
   - for each PR, the latest `<PFX>-REVIEW` verdict and round, `<PFX>-FIXER` and `<PFX>-RETRY` markers, whether the label is present, and the time since the last activity.

   Flag a stall: no verdict 45 minutes after a push, or a FAIL with no fixer reply after 45 minutes.
3. **Routines** (cloud mode): for each id in `config.routines`, use RemoteTrigger `get` for enabled, last run and next run.
   - If a call returns 404, say a different account may be signed in (`/login`).
   - Report the latest `<PFX>-USAGE` and `<PFX>-SECURITY` headlines from their issues.
4. **Items:**
   - "Open items (sessions resolve)" from `DECISIONS_LOG.md`, which sessions should be clearing;
   - "Hard-limit gates", the only things waiting for the owner.

   Never present session-resolvable work as a task for the user.
5. **Health:** branches merged but not deleted, and failing or flaky proof noted in the ledger.

End with one line: the current phase, its state, and the next expected event (for example "PR #12 in review, round 2" or "Worker resumes at 20:12 UTC").
