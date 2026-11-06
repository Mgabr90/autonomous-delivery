# Host operations: GitHub

Every routine prompt says *what* to do on the host. This file says *how* on GitHub. `/autodeliver:init` copies it to `{{HOST_DOC}}` with the placeholders filled. Routines read it at the start of every run.

- Repo `{{REPO}}` · gate branch `{{MAIN}}`. Use `gh api` (REST) or the GitHub MCP tools; GraphQL may be unavailable in cloud sessions.

## 0. Start of every run

The routine has the repo as a `sources` entry; the platform clones it. The triggering event is in the session; still decide from the PR's state, never from the trigger text.

## 1. Pull requests

| Operation | Call |
|---|---|
| Open loop PRs | `gh api repos/{{REPO}}/pulls?state=open&base={{MAIN}}`, keep `head.ref` starting with `{{BRANCH_PREFIX}}` and `draft == false` |
| Head sha | `head.sha` |
| Open a PR | `gh api -X POST repos/{{REPO}}/pulls -f head=<branch> -f base={{MAIN}} -f title=… -f body=…` |
| Read comments | `gh api repos/{{REPO}}/issues/<n>/comments` |
| Post a marker comment | `gh api -X POST repos/{{REPO}}/issues/<n>/comments -f body=…` |
| Label | add `gh api -X POST repos/{{REPO}}/issues/<n>/labels -f "labels[]={{LABEL}}"`; remove `gh api -X DELETE repos/{{REPO}}/issues/<n>/labels/{{LABEL}}`. **Adding the label fires the Fixer.** |
| Merge pinned to the sha | `gh api -X PUT repos/{{REPO}}/pulls/<n>/merge -f merge_method=merge -f sha=<reviewed sha> -f commit_title="Merge <title> (#<n>)"` |
| Re-request a review | push an empty commit (fires `pull_request.synchronize`) |

## 2. Firing the next routine

| From → to | How |
|---|---|
| PR opened / updated → Reviewer | webhook `pull_request.opened`, `.reopened`, `.synchronize`, `.ready_for_review` |
| Reviewer FAIL → Fixer | adding the label `{{LABEL}}` (`pull_request.labeled`) |
| Watchdog → Fixer | remove and re-add the label |
| PR merged → Worker | webhook `pull_request.closed` (merged) |

## 3. Watchdog extras

None beyond the Worker prompt.

## 4. Reports

One comment per run on the issue named in the prompt (create it if missing).

## 5. Dependency alerts

`gh api repos/{{REPO}}/dependabot/alerts`; on 403, the package manager's audit.
