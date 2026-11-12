# Plan: a planning-tier model plans, the strong tier builds (autodeliver 0.10.0, second item)

Revision 3 (after design review rounds 1 and 2; the record is in `.autodeliver/loop-log.md`). Branch: `autodeliver-0.10.0-security-audit`. Placeholders are written here as `<NAME>`. Paths are under `plugins/autodeliver/` unless they start with "root".

**Build order:** this plan is built after tasks 1 to 5 of `.autodeliver/plan.md` are committed on the branch, never in parallel with it. That plan creates the `## 0.10.0` CHANGELOG entry and bumps both manifests; this plan adds to that entry. If the entry is absent, stop and report: do not create it here.

## 1. Goal

The owner's request: when a top model such as Fable is used, keep it for planning, and use Opus 5.5 or a similar model for execution, review, fixes and the rest. Write this into the playbook as a rule, and into every copy that carries model rules.

Scope: **local sessions**. Out of scope: cloud routines (they keep their tiers; decision M7); a new agent; a new placeholder; any change for a session that is not on a planning-tier model.

## 2. How models are set today

- `references/playbook.md` section 11, first bullet: "**Strongest model** for building, design review, reviewing, fixing and security. A **mid-tier model** only for the usage inspector, which makes no quality judgements."
- `references/config.md`: the example JSON has `"models": { "strong": "claude-opus-5-5", "mid": "claude-sonnet-5-5" }` (line 53) and the placeholder table maps `<MODEL_STRONG>` and `<MODEL_MID>` to it (line 120). The field table (columns "Field | Meaning", lines 67 to 87) has no `models` row. A local project's config often has no `models` block at all, and `commands/loop.md` also runs with no config and no HANDOFF.
- Every agent that makes a judgement has `model: opus` in its frontmatter (`delivery-reviewer`, `delivery-fixer`, `design-reviewer`, `researcher`, `visual-checker`, `translation-reviewer`), so reviews, design reviews and agent fixes already run on Opus whatever the main session's model is. `usage-inspector` has `model: sonnet`.
- **The gap.** In local mode the main session is the builder. `commands/loop.md` round 0 says "Then build it in this session", runs the simplify pass there, and on FAIL fixes "in this session ... or by dispatching the `delivery-fixer` agent if the config sets `"fixer": "agent"`"; `--baseline` builds in the session too. The session's model is whatever the user started. On a top model, its tokens then go on the high-volume work (building, fixing), not on the plan, where a wrong decision costs most.
- `commands/loop.md` round 0 already tells the main session what binds a build: the skills in HANDOFF "Skills" and the four it never uses (`subagent-driven-development`, `executing-plans`, `finishing-a-development-branch`, `using-git-worktrees`), "test-first or check-first ... following the profile", and the simplify limits (only work built here; `/simplify <base>...HEAD`; one `refactor(simplify)` commit; only files the build changed; never again in later rounds). Its last two round-0 bullets are "If it names existing work ..., skip building" and "Record the scope precisely". Its section "At the cap, or when a stop guard fires" names three limits: round cap, no progress, budget.
- Three texts ban "cheaper models": `agents/usage-inspector.md` and `templates/routines/4-usage-inspector.prompt.md` ("NEVER propose ... cheaper models for review, fix, security or build work"; the list ends with the item about weakening the PASS rule and the hard limits; the routine copy then says "Cheaper models are fine only for pure bookkeeping."), and `commands/report.md` step 4 ("one concrete suggestion under the quality-first rule: never a cheaper model or fewer checks for judgement work"). Read literally they forbid suggesting this rule.
- The token log (`scripts/token_log.py`) writes one row per role and round with a `model` column. The main session's rows have role `main`; a `general-purpose` subagent's rows have role `general-purpose`.
- The Agent tool's `model` parameter takes a family name (`opus`, `sonnet`, `haiku`, `fable`), not a full model id. A subagent dispatched without it inherits the parent's model.

## 3. Design

### 3.1 Terms (the same in every copy)

- **Strong tier:** `models.strong`; Opus when it is not set (what the review and fix agents already run on).
- **Planning-tier session:** a session whose own model id contains one of the names in `models.plan`. `models.plan` is a new optional config field, a list of name fragments, default `["fable", "mythos"]`. A session that cannot tell its own model works as a strong-tier session.
- **Family name for a hand-over:** the family word inside `models.strong` (`claude-opus-5-5` gives `opus`). Use `opus` when the field is unset, when no family name fits, or when the name is itself in `models.plan`.
- **Where the tier is written:** the first line of this loop's entry in the ledger, or in `.autodeliver/loop-log.md` when there is no ledger: `Model tier: planning` or `Model tier: strong`, followed by the model id or `unknown`.

### 3.2 `templates/docs/HANDOFF.md`: new section, placed directly before `## Skills (use them when available)`

The charter carries the rule; the steps live once, in `commands/loop.md`, the only place that runs them. Exact text:

```markdown
## Models

- **The strong tier is the floor.** Building, reviewing, fixing and security work is never handed to a model below the strong tier: `models.strong` in the config, or Opus when it is not set (what the review and fix agents run on).
- **A planning-tier model plans; it does not build.** A local session is on a planning-tier model when its own model id contains one of the names in `models.plan` (default: `fable`, `mythos`). It keeps that model for understanding the task, research, the plan and its decisions, resolving the design review, rulings, dispatching agents and checking what they return. It may write the plan, the ledger and notes, and make a one-line fix that is needed to hand work over. It hands the build, the simplify pass and every fix to strong-tier subagents, and never finishes the build itself. `/autodeliver:loop` has the steps: the brief, the checks on return and the retry limit.
- **Cloud routines keep their tiers:** Worker, Reviewer, Fixer and security sweep on the strong model. Don't set a routine to a planning-tier model.
- A session on the strong tier, or on a lower model the user chose, works as before.
```

### 3.3 `references/playbook.md`

Section 11: the first bullet is replaced by these two bullets, exact text:

```markdown
- **Strong model** (`models.strong`) for building, design review, reviewing, fixing and security: this work is never handed to a lower model. A **mid-tier model** only for the usage inspector, which makes no quality judgements.
- **A planning-tier model plans; it does not build.** When a local session runs on a model named in `models.plan` (default: Fable and Mythos models), keep it for the work where a wrong decision costs most: understanding the task, research, the plan, resolving the design review, rulings and checking results. It hands the build, the simplify pass and every fix to strong-tier subagents with a fixed brief, checks what comes back, and never finishes the build itself. Handing work from a planning-tier model to the strong tier is not "a cheaper model" in the usage inspector's sense: the strong tier stays the floor. Cloud routines keep their tiers. HANDOFF "Models" has the rule; `/autodeliver:loop` has the steps.
```

Section 8: the table has the columns "Cloud piece | Local equivalent". Add this row directly after the "Design review" row: `| Worker routine (build) | the main session; on a planning-tier session, a strong-tier subagent with a fixed brief (`/autodeliver:loop`, round 0) |`. In the "Fixer routine + label" row, after "the `delivery-fixer` agent (cleaner separation)" add "; always the agent on a planning-tier session". Directly under the table add one sentence: "On a planning-tier session, the Builder and Fixer boxes in the diagram are strong-tier subagents." The diagram itself is unchanged.

Sections 2 (line 49) and 11 (the design-review bullet) are unchanged: the new section 11 bullet says in so many words that a hand-over to the strong tier is not a cheaper model. Sections 1 and 10: no change.

### 3.4 `commands/loop.md` (five edits)

1. Round 0: insert this bullet, with its four sub-bullets, directly before "Then build it in this session: ...". Exact text:

   ```markdown
   - **Model tier** (`HANDOFF.md` "Models"). This session is on a planning-tier model if its own model id contains a name in `models.plan` (default `fable`, `mythos`); if it can't tell its model, it is not. Write `Model tier: planning` or `Model tier: strong`, with the model id or `unknown`, as the first line of this loop's entry in the ledger or `.autodeliver/loop-log.md`. On a planning-tier session one thing changes in the bullets below: who builds and who simplifies. Everything else in them applies on every session: skip building for existing work, the simplify limits, record the scope.
     - **Hand the build** to one `general-purpose` subagent. Set its `model` to the family name in `models.strong` (`claude-opus-5-5` gives `opus`). Use `opus` when the field is unset, when no family name fits, or when the name is itself in `models.plan`. Never dispatch without an explicit `model`: the subagent would inherit this session's model.
     - **The build brief** has these items and none of your reasoning: the goal; the plan path; the file boundary; the hard limits and gates (from `HANDOFF.md`, or from `hard_limits` and `gates` in the config when there is no HANDOFF); build test-first or check-first, following the profile; use the skills in HANDOFF "Skills" when they are available, and never `subagent-driven-development`, `executing-plans`, `finishing-a-development-branch` or `using-git-worktrees`; run `proof_touched` and quote its output; commit, don't push.
     - **Hand the simplify pass** to a fresh subagent of the same kind and model. Its brief: the range `<base>...HEAD`; the simplify limits in the bullet below; the hard limits and gates; run `proof_touched` and quote its output; one `refactor(simplify)` commit; don't push.
     - **Check each return** before going on: the commit exists, the changed files are inside the boundary (for the simplify pass: inside the files the build changed), and the quoted proof is green. The gate reruns the proof itself; this check only catches an unfinished hand-over. If a check fails, or the dispatch itself fails, send a fresh subagent the exact gap, at most twice. Then stop and report as at the cap, naming the limit as a failed hand-over. Never finish the build here.
   ```

2. Rounds, step 2 FAIL: after "if the config sets `"fixer": "agent"`" add " or this session is on a planning-tier model (then always the agent)". After "Then run `proof_touched`." add " A planning-tier session runs it too: it is a check, not a fix."
3. "At the cap, or when a stop guard fires": the list of limits "(round cap, no progress or budget)" becomes "(round cap, no progress, budget or a failed hand-over)".
4. `--baseline`: append "On a planning-tier session, hand this build over the same way, with the same brief and checks."
5. Final report, the "tokens per role and round" bullet: append "(a handed-over build shows as role `general-purpose`)".

### 3.5 The three "cheaper model" texts

- `agents/usage-inspector.md`: a new paragraph directly after the last item of the NEVER list (the item about weakening the PASS rule and the hard limits). `templates/routines/4-usage-inspector.prompt.md`: a new paragraph directly after the line "Cheaper models are fine only for pure bookkeeping." The same text in both, exact: "The strong tier is the floor for that work. Handing building or fixing from a planning-tier model (one named in `models.plan`; by default Fable and Mythos models) to the strong tier is not a cheaper model in this sense. Where there is a token log: a loop that built new work, whose `main` rows are on a planning-tier model and which has no `general-purpose` row in round 0 on a model outside `models.plan`, may indicate that the planning session did the building. You may flag it and propose the hand-over in HANDOFF "Models". Never propose anything below the strong tier for that work." (The token-log half cannot apply in a cloud run, which has no token log; it stays so the two copies are identical.)
- `commands/report.md` step 4, last bullet: append as a new sentence: "Handing building or fixing from a planning-tier model to the strong tier (HANDOFF "Models") is not a cheaper model in this sense, and you may suggest it when the token log's `model` column shows the main session on a planning-tier model and no strong-tier build row."

### 3.6 Reference text

- `references/config.md`: in the example JSON, `models` becomes `{ "strong": "claude-opus-5-5", "mid": "claude-sonnet-5-5", "plan": ["fable", "mythos"] }`. Add this row to the field table, directly before the `token_log` row, exact text: `| `models` | `strong`: the model for building, reviewing, fixing and security, and the lowest tier that work is handed to (Opus when unset). `mid`: the usage inspector only. `plan` (optional, `models.plan`): name fragments of planning-tier models (default `["fable", "mythos"]`). A local session whose model id contains one of them plans and checks, and hands the build and the fixes to the strong tier (playbook section 11); if `strong` itself matches `plan`, hand-overs use Opus. Cloud routines use `strong` and `mid` only |`. The placeholder table is unchanged: `plan` has no placeholder.
- `references/cloud-setup.md`: one sentence as a new paragraph directly under the routine table that has the "Model" column: "Keep these tiers. Don't set a routine to a planning-tier model (`models.plan`): the Worker's ticks are frequent and mostly bookkeeping, and the planning-tier rule (HANDOFF "Models") is for local sessions."
- Root `CHANGELOG.md`, in the 0.10.0 entry, add this bullet group: lead line "**A planning-tier model plans; the strong tier builds** (local sessions; HANDOFF "Models", playbook section 11, `/autodeliver:loop`):" with five sub-bullets: (1) a session whose model id matches `models.plan` (new, optional; default `fable`, `mythos`) keeps planning, rulings and checks, and hands the build, the simplify pass and every fix to strong-tier subagents; (2) a fixed brief that carries the hard limits, test-first working and the excluded skills, an explicit `model` on every dispatch, checks on return, and at most two re-dispatches before the loop stops; (3) the strong tier is the floor, and the usage inspector and `/autodeliver:report` may suggest the hand-over; (4) cloud routines keep their tiers; (5) existing projects: copy the "Models" section from the HANDOFF template into your own HANDOFF.

Not changed, with the reason: all agents except `usage-inspector` (their `model` is already fixed); routines 1, 2, 3 and 5 (M7); `commands/doctor.md` (routine models are unchanged, so its "expected model" check stays true); `commands/init.md`, `review.md`, `design-review.md`, `status.md`; `SKILL.md` and README (the rule lives in the playbook and HANDOFF; more one-line copies would only drift); `examples/*.config.json` (the field is optional with a default).

## 4. Decisions

| # | Decision | Why | Cost if wrong |
|---|---|---|---|
| M1 | The rule applies only to a planning-tier session | That is what was asked ("in case Fable is used"); a strong-tier session keeps one context for plan and build | None for today's users |
| M2 | Optional `models.plan` name list, default `fable` and `mythos`, no placeholder | A session cannot rank models reliably, least of all ones newer than itself; a name match is decidable and the owner can extend the list. Mythos is in the default because it is the same model class as Fable | A new top model with another name is not matched until the owner adds it: the session builds as today |
| M3 | No new builder agent; a `general-purpose` subagent with an explicit model and a fixed brief | A new agent means init, doctor and cloud copies; the brief is short and written out word for word | Briefs still vary a little; the plan and the gate bound the work |
| M4 | The floor is worded as "never handed to a lower model" | It must not contradict a user who runs a whole local session on a lower model, which stays their choice | — |
| M5 | The planning session may make a one-line hand-over fix | Dispatching an agent for one line costs more than the line | A session stretches "one line"; the token-log signal in 3.5 can show a planning-tier loop with no strong-tier build row, but not a small stretch |
| M6 | The gate is unchanged | Review, proof and the PASS rule are not touched; the return check trusts a quoted proof only because the gate reruns the proof itself | If the strong tier builds worse than the planning tier would, the gate catches it at the cost of a round |
| M7 | Local sessions only; cloud routines keep their tiers | An unattended Worker handing its build to subagents needs the no-prompt rule and restart safety carried into every brief, covers more paths (take-over, staging), and changes what doctor expects; none of that can be tested here. The Worker also ticks hourly, mostly on bookkeeping | An owner who wants a planning-tier Worker waits for a later release |
| M8 | At most two re-dispatches, then stop | The same guard as the loop's no-progress stop: more of the same rarely converges | A build that needed a third try stops and is reported, not lost |
| M9 | The steps live once, in `loop.md`; HANDOFF carries the rule and a pointer | `loop.md` is the only place that runs them, and every cloud routine reads HANDOFF on every run although the rule is local | A reader of HANDOFF must open the loop command for detail; HANDOFF says so |
| M10 | The brief states the hard limits, test-first working and the four excluded skills itself | A local loop may have no HANDOFF; a subagent with the superpowers plugin could otherwise start a skill that moves work outside the gate | A longer brief |
| M11 | The inspector sentence is identical in both copies | The repo keeps the two inspector copies in step; the cloud copy's token-log half never applies and does no harm | A few unused words in a cloud prompt |

## 5. File boundary

`skills/autonomous-delivery/references/playbook.md` (sections 8 and 11), `skills/autonomous-delivery/references/config.md`, `skills/autonomous-delivery/references/cloud-setup.md`, `skills/autonomous-delivery/templates/docs/HANDOFF.md` (new "Models" section), `skills/autonomous-delivery/templates/routines/4-usage-inspector.prompt.md`, `agents/usage-inspector.md`, `commands/loop.md`, `commands/report.md`, root `CHANGELOG.md`.

## 6. Tasks

| # | Task | Done when |
|---|---|---|
| 1 | HANDOFF "Models" | The section sits directly before "Skills" and matches 3.2 word for word |
| 2 | Playbook sections 11 and 8 | The two bullets match 3.3; the row, the Fixer-row addition and the sentence under the table are in |
| 3 | `loop.md` | The five edits of 3.4 are in; the inserted bullet matches word for word |
| 4 | The three "cheaper model" texts | The paragraph of 3.5 is byte-identical in both inspector copies; `report.md` has its sentence |
| 5 | config.md, cloud-setup.md, CHANGELOG | Each matches 3.6; the example JSON block still parses as JSON |
| 6 | Reread the diff for conflicting wording (this stands in for `/simplify`, which is for code), run the proof, commit | Proof output quoted |

## 7. Test plan

1. The full proof in `.autodeliver/config.json`.
2. Greps: "planning-tier" appears in playbook, HANDOFF, `loop.md`, both usage-inspector copies, `report.md`, `config.md` and `cloud-setup.md`; `models.plan` appears in HANDOFF, `loop.md`, playbook, `config.md`, `cloud-setup.md` and both inspector copies; no new double-brace placeholder in the diff; the inspector paragraph is byte-identical in its two files; `git diff --name-only main` stays inside the two plans' boundaries; `git ls-files --eol` shows LF for each changed file.
3. Read-through cases (text → expected action), each checked by the reviewer:
   - a local loop whose model id contains `fable` → `Model tier: planning` is the first line of the loop's entry; plan and design review in the session; build by one `general-purpose` subagent with `model: "opus"` and the full brief; simplify by a fresh one with its own brief; fixes by `delivery-fixer`; review by `delivery-reviewer`;
   - the same loop pointed at existing work → no build is handed over; the scope is still recorded;
   - no `models` block in the config, or no config and no HANDOFF → the strong tier is Opus, the default name list applies, and the brief takes hard limits and gates from the config if there is one;
   - `models.strong` holds an id with no family name the Agent tool accepts, or a Fable id → `opus` is used; no dispatch without a model;
   - the build subagent returns with no commit, a file outside the boundary, or a red proof; or the dispatch fails → a fresh subagent gets the exact gap; after two such tries the loop stops and reports a failed hand-over; the session does not finish the build;
   - the simplify subagent changes a file the build did not → caught by the return check;
   - `--baseline` on a planning-tier session → the build is handed over;
   - a local loop on an Opus model → `Model tier: strong`; otherwise exactly today's behaviour;
   - a session that cannot tell its model → works as a strong-tier session and writes `unknown`;
   - a local session on a model below the strong tier → works as before; no text tells it otherwise;
   - the usage inspector sees a planning-tier loop that built new work with no strong-tier `general-purpose` row in round 0 → may flag it; a loop over existing work → no flag; a strong-tier build → may not propose a cheaper model;
   - cloud: no routine prompt changes except the inspector's paragraph; cloud-setup tells owners to keep the tiers.
