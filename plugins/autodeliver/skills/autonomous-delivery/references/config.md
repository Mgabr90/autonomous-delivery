# `.autodeliver/config.json`

`/autodeliver:init` writes this file and every other command reads it. Commit it to the repo, since it holds no secrets.

```json
{
  "version": 1,
  "project": "Acme Portal",
  "mode": "cloud",
  "host": "github",
  "profiles": ["software"],
  "repo": "acme/portal",
  "main_branch": "main",
  "branch_prefix": "work/",
  "marker_prefix": "ACME",
  "label": "acme-review-fail",
  "work_dir": ".",
  "paths": {
    "handoff": "docs/delivery/HANDOFF.md",
    "decisions": "docs/delivery/DECISIONS_LOG.md",
    "roadmap": "docs/delivery/ROADMAP.md",
    "ledgers": "docs/delivery/ledgers/",
    "plans": "docs/delivery/plans/",
    "evidence": "docs/delivery/evidence/",
    "system": "docs/delivery/SYSTEM.md",
    "host_doc": "docs/delivery/HOST.md"
  },
  "ado": {
    "org": "https://dev.azure.com/acme",
    "project": "Portal",
    "repo": "portal",
    "git_name": "Delivery Bot",
    "git_email": "delivery@acme.example",
    "reports_branch": "delivery-reports"
  },
  "proof_full": ["npm test", "npx tsc --noEmit", "npm run build"],
  "proof_touched": ["npx vitest related --run", "npx tsc --noEmit"],
  "e2e": "npx playwright test",
  "review_checklist": [],
  "locales": ["en"],
  "staging": { "client": "tools/stg.sh", "test_account_domain": "example.com" },
  "gates": ["Production deploy needs the owner's approval in chat"],
  "hard_limits": [
    "Never push or merge to the main branch except the gate merging on PASS",
    "Never touch production without the owner's approval in chat",
    "Test accounts and test data only outside production",
    "Never commit or print secrets"
  ],
  "loop": { "cap": 5, "fail_review_cap": 10, "token_budget": null, "phase_tick_cap": 12 },
  "second_opinion": null,
  "design_review": { "lenses": ["zoom-out", "comprehension", "critic", "readiness"], "rounds": 2 },
  "models": { "strong": "claude-opus-5-5", "mid": "claude-sonnet-5-5" },
  "token_log": true,
  "token_log_path": ".autodeliver/token_log.csv",
  "routines": {
    "environment_id": "env_…",
    "worker": "trig_…",
    "reviewer": "trig_…",
    "fixer": "trig_…",
    "usage_inspector": "trig_…",
    "security_sweep": "trig_…"
  }
}
```

| Field | Meaning |
|---|---|
| `mode` | `local` (subagents in one session) or `cloud` (routines fired by host events) |
| `host` | `github` (default) or `ado` (Azure DevOps). Picks the host-operations doc copied to `paths.host_doc` (`templates/docs/HOST-<host>.md`); the routine prompts stay the same for both |
| `ado` | Only for `host: "ado"`: the org URL, project, repo, the git identity commits are made as, and the branch that holds the usage and security reports (Azure DevOps has no issues the loop uses) |
| `profiles` | Built-in profile names, or inline objects (see `profiles.md`) |
| `marker_prefix` / `label` | The machine-readable markers in PR comments, and the label that fires the Fixer |
| `proof_full` | Run by the reviewer before **any** PASS, never scoped down |
| `proof_touched` | Run by the fixer on what it changed |
| `gates` | The only actions that wait for a human |
| `paths.system` | The living system doc (`templates/docs/SYSTEM.md`): what is built now. Default `docs/delivery/SYSTEM.md` when an older config lacks it. Phases that change the system's shape update it; the weekly sweep checks it for drift |
| `design_review` | The fresh-eyes review of each phase plan before building (`design-reviewer` agent). `lenses`: which lenses run (default all four; `drift` is for the sweep, not here). `rounds`: re-review rounds before open findings become rulings (default 2). Missing block = these defaults. Read by the Worker and `/autodeliver:loop` from this file, so it needs no placeholder |
| `loop.cap` | Local loop rounds before it stops and reports (default 5) |
| `loop.token_budget` | Optional. Local loop: stop and report when this loop's tokens (input + output + cache write, from the token log) reach it. Unset by default. It stops the loop; it never makes a review shallower |
| `loop.phase_tick_cap` | Cloud: Worker ticks a phase may take before opening its PR; past it, or when the ledger's "Next" hasn't moved for three ticks, the Worker re-plans or splits the phase (default 12) |
| `second_opinion` | Optional reviewer from another model vendor: `{"command": "<CLI that reads a prompt on stdin and prints findings>", "timeout_s": 600}`, for example a read-only, non-interactive Codex or Gemini CLI call. The gate verifies each item itself; a failure never blocks a verdict. In cloud mode the CLI and its key must be installed in the environment |
| `loop.fail_review_cap` | Cloud FAIL reviews per PR before the Worker takes over (default 10) |
| `token_log` | **On by default.** The plugin hook appends token usage per role and round to `token_log_path` (CSV, git-ignored). Set it to `false` to turn it off. It only runs in projects that have this config. |
| `routines` | Filled in by init in cloud mode; used by `status` and `doctor`. On Azure DevOps the routine ids are also needed by the service-hook script and the `FIXER_ROUTINE_ID` environment variable |

## Template placeholders

`/autodeliver:init` fills every `{{…}}` in `templates/` from the config, or from the answers it collects. **No `{{` may remain** in the files it writes; `init` and `doctor` both check this.

| Placeholder | Filled from |
|---|---|
| `{{PROJECT}}` | `project` |
| `{{REPO}}` | `repo` (`owner/name`) |
| `{{MAIN}}` | `main_branch` |
| `{{BRANCH_PREFIX}}` | `branch_prefix` |
| `{{PFX}}` | `marker_prefix` |
| `{{LABEL}}` | `label` |
| `{{HANDOFF}}`, `{{DECISIONS}}`, `{{ROADMAP}}`, `{{LEDGERS}}`, `{{PLANS}}`, `{{EVIDENCE}}` | `paths.handoff`, `paths.decisions`, `paths.roadmap`, `paths.ledgers`, `paths.plans`, `paths.evidence` |
| `{{SYSTEM}}` | `paths.system` |
| `{{WORK_DIR}}` | `work_dir` |
| `{{HOST}}` | `host` |
| `{{HOST_DOC}}` | `paths.host_doc` |
| `{{ADO_ORG}}`, `{{ADO_PROJECT}}`, `{{ADO_REPO}}` | `ado.org`, `ado.project`, `ado.repo` (host `ado` only) |
| `{{GIT_NAME}}`, `{{GIT_EMAIL}}` | `ado.git_name`, `ado.git_email` |
| `{{REPORTS_BRANCH}}` | `ado.reports_branch` |
| `{{PROOF_FULL}}` | `proof_full`, joined with `; ` |
| `{{PROOF_TOUCHED}}` | `proof_touched`, joined with `; ` |
| `{{E2E}}` | `e2e`, or "none" |
| `{{REVIEW_CHECKLIST}}` | `review_checklist` plus each profile's built-in checklist, joined with `; ` |
| `{{LOCALES}}` | `locales`, joined with `, ` |
| `{{STAGING_CLIENT}}` | `staging.client`, or "(no staging)", in which case the prompt's staging steps are skipped |
| `{{GATES}}` | `gates`, joined with `; ` |
| `{{GATES_LIST}}` | `gates` as a numbered Markdown list |
| `{{HARD_LIMITS}}` | `hard_limits`, joined with `; ` |
| `{{HARD_LIMITS_LIST}}` | `hard_limits` as a numbered Markdown list |
| `{{FAIL_REVIEW_CAP}}` | `loop.fail_review_cap` |
| `{{MODEL_STRONG}}`, `{{MODEL_MID}}` | `models.strong`, `models.mid` |
| `{{DATE}}` | today's date (YYYY-MM-DD) |
| `{{GOAL}}` | asked at init, or drafted from the README and marked as a draft |
| `{{FIRST_PHASE_SCOPE}}`, `{{FIRST_PHASE_DONE_WHEN}}` | asked at init, or drafted |
| `{{FINAL_GATE}}` | the last entry of `gates` |
| `{{ENVIRONMENT_NOTES}}` | detected tooling, the test-DB setup and staging access, written by init |
| `{{PHASE}}`, `{{PLAN_PATH}}`, `{{BRANCH}}` | filled per phase, when a session creates a ledger from `LEDGER.md` |

