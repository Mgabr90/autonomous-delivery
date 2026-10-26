# Cloud mode setup (Claude Code on the web + GitHub)

## Prerequisites

1. **A GitHub repo**, with the Claude GitHub app installed on it (claude.ai/code prompts you for this on the first connection).
2. **A Claude Code environment** for the repo at claude.ai/code. Note its id (`env_…`).
   - Allow network access for package managers.
   - Add a **Network secret** for any staging host, so the header is injected and sessions never see the token.
3. **The `RemoteTrigger` tool** in your local Claude Code. Load it with `ToolSearch` (`select:RemoteTrigger`). Check the signed-in account first: a 404 for a known trigger usually means a different account is logged in, so run `/login`.
4. **The `gh` CLI**, authenticated, for labels and settings.

## Create a routine

`RemoteTrigger` `action: "create"`, with this body:

```json
{
  "name": "<Project> · 2 Reviewer (PR gate, labels FAIL, merges on PASS)",
  "cron_expression": "",
  "enabled": true,
  "persist_session": false,
  "job_config": { "ccr": {
    "environment_id": "env_…",
    "session_context": {
      "model": "claude-opus-5-5",
      "sources": [ { "git_repository": { "url": "https://github.com/<owner>/<repo>" } } ],
      "allowed_tools": ["Bash", "Read", "Glob", "Grep", "Agent", "Skill", "TodoWrite"]
    },
    "events": [ { "data": {
      "uuid": "<fresh uuid4>", "session_id": "", "type": "user", "parent_tool_use_id": null,
      "message": { "role": "user", "content": "<the filled prompt template>" }
    } } ]
  } }
}
```

- **Empty `cron_expression`:** the routine is webhook-only (Reviewer, Fixer).
- **Cron:** for example `12 * * * *` (Worker), `0 5 * * *` (usage inspector), `0 3 * * 1` (security sweep).
- **`persist_session: true`** (Worker only) sends every run into one session, so it keeps context across ticks.
- **Updates:** `action: "update"` with `trigger_id` and the same `job_config` shape. Use a **new uuid** in `events[0].data.uuid` whenever the prompt changes. The change takes effect at the next run.
- **Testing:** `action: "run"` triggers it once by hand. Do this for every new routine. Then read `list_runs` and `get_run_log`.

| Routine | Model | Trigger | persist_session | Tools |
|---|---|---|---|---|
| 1 Worker | strong | cron `12 * * * *` + webhook `pull_request.closed` | true | Bash, Read, Write, Edit, Glob, Grep, Agent, Skill, TodoWrite, WebFetch, WebSearch |
| 2 Reviewer | strong | webhook `pull_request.opened`, `.reopened`, `.synchronize`, `.ready_for_review` | false | Bash, Read, Glob, Grep, Agent, Skill, TodoWrite, WebSearch, WebFetch |
| 3 Fixer | strong | webhook `pull_request.labeled` | false | Bash, Read, Write, Edit, Glob, Grep, Agent, Skill, TodoWrite, WebSearch, WebFetch |
| 4 Usage inspector | mid | cron `0 5 * * *` | false | Bash, Read, Glob, Grep, TodoWrite |
| 5 Security sweep | strong | cron `0 3 * * 1` | false | Bash, Read, Glob, Grep, Agent, Skill, TodoWrite, WebSearch, WebFetch |

The web tools are needed because the routines dispatch the `researcher` agent, and a subagent can only use tools its session allows.

## Attach a GitHub webhook

`RemoteTrigger` `action: "create_webhook_trigger"`:

```json
{ "hook_type": "app", "source": "github", "scope_id": "<owner>/<repo>",
  "events": ["pull_request.opened", "pull_request.reopened", "pull_request.synchronize", "pull_request.ready_for_review"],
  "routine_trigger_id": "trig_…" }
```

**Add filters** to cut wasted runs. They are set in the trigger's edit dialog at claude.ai/code/routines; the API also accepts a structured filter. All conditions must match:

| Routine | Event | Filters |
|---|---|---|
| Reviewer | `pull_request.opened`, `.reopened`, `.synchronize`, `.ready_for_review` | base branch equals `<main>`; head branch starts with `<branch_prefix>`; is draft = false |
| Fixer | `pull_request.labeled` | labels include `<label>`; base branch equals `<main>` |
| Worker (wake) | `pull_request.closed` | is merged = true; base branch equals `<main>` |

Keep the event, branch and marker checks in the prompts anyway, as defence in depth.

**Supported events** are pull request, release and issue. Comment events are not supported, which is why the loop uses a label to fire the Fixer.

**Limits:**
- GitHub events beyond the per-task and per-account hourly caps are **dropped**, so the Worker's watchdog is required.
- Schedules can't run more often than hourly.
- Scheduled runs are capped at 100 per hour per account.
- Every run counts against your subscription usage.

## GitHub settings

- **Label:** `gh label create <pfx>-review-fail --color B60205 --description "Review gate FAIL; fires the fixer"`.
- **Dependency alerts** (free; no Actions minutes): `gh api -X PUT repos/<owner>/<repo>/vulnerability-alerts`.
- **Branch protection** is optional. Free plans can't protect private repos; the gate being the only merger is the hard limit either way.

## The deliberate loop test (do it before real work)

1. Open a tiny PR from a `<branch_prefix>loop-test` branch with a **planted defect** and a plan file that lists the fix as required.
2. Watch the chain:
   - the Reviewer comments FAIL and adds the label;
   - the Fixer fixes, pushes and removes the label;
   - the Reviewer comments PASS and merges;
   - the Worker deletes the branch at its next tick.
3. If any step stalls, read `get_run_log` for that routine. The most common causes are the wrong signed-in account, a missing GitHub app permission, or a prompt that skipped the event.

## Plugins don't load in cloud sessions

Cloud sessions load the repo's committed `.claude/` folder (agents, skills, commands, and `settings.json` hooks), but not plugins. `/autodeliver:init` therefore copies the plugin's agents into `.claude/agents/`. Copy any skills your prompts rely on into `.claude/skills/` too, keeping their licence files.
