# Autonomous delivery playbook

A reusable way to run long pieces of work almost hands-off with Claude Code. One role **plans and builds**, fresh-eyes reviewers **check the plan** before any work starts, an independent role **reviews** the result, another **fixes**, and **monitors** watch quality, security, drift and cost. A human acts only at the gates they choose.

It works for any work that can be checked: software, documents and courses, data and analytics, infrastructure, migrations and research. Section 3 has a profile for each.

It runs in one of two modes:
- **Local:** one Claude Code session on your machine, with subagents and hooks. No GitHub or cloud is needed.
- **Cloud:** Claude Code routines on the web, fired by events from the code host (GitHub, or Azure DevOps service hooks). This mode runs around the clock and survives usage-limit resets.

The code host is a setting (`host: github | ado`). The routine prompts say *what* to do; one host-operations doc per host (`templates/docs/HOST-github.md`, `templates/docs/HOST-ado.md`) says *how*: cloning, PR comments, labels, merging pinned to a sha, firing the next routine, and where reports go.

---

## 1. Principles

1. **Quality first.** Never trade review depth, proof or verification for tokens. Save only by removing waste: idle runs, duplicate reviews, context bloat.
2. **No dependency on the human.** Nothing is parked "for the user":
   - visual checks are done by screenshots plus a visual-review agent;
   - session-written translations get a review agent;
   - product and policy questions get rulings;
   - owner-only facts are derived, or written in wording that is true without them;
   - stalls and caps go to the Worker.

   The human acts only at their own **hard-limit gates**, each prepared as a single action.
3. **Autonomy with a charter.** Sessions decide on their own and log every ruling with its *cost if wrong*. They don't stop to ask.
4. **Hard limits, never crossed.** For example:
   - only the gate merges into the main branch;
   - production needs explicit approval;
   - test data only outside production;
   - no secrets in git.
5. **Independent review.** The reviewer did not do the work, runs separately, runs the deterministic checks itself, and passes only with the full proof green.
6. **State lives in files, not in sessions.** The handoff doc, roadmap, plans, ledgers and decisions log make any session restartable from zero.
7. **Least privilege everywhere.** Sessions reach outside systems only through narrow, allow-listed gates.
8. **Event-driven, with a watchdog.** Events drive the loop; a periodic tick catches anything that stalls.
9. **No paid CI needed.** Everything runs in Claude Code sessions, whichever host holds the code.
10. **Design with an elephant, review with a goldfish.** The Worker holds the full context and writes each phase plan as a design doc. Reviewers who have never seen its reasoning check that plan *before* building starts, when a wrong design is cheapest to fix. The gate then checks the result against the plan. (From Google's [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model); see section 5a.)

---

## 2. Roles

| Role | Does | Never does |
|---|---|---|
| **Builder / Worker** | Plans and builds one work unit (a "phase"), verifies it, opens it for review. In cloud mode it is also the watchdog and the janitor, and it takes over stuck loops. | Merges its own work. Crosses a hard limit. |
| **Reviewer (gate)** | Independent review plus the full proof. Classifies findings as Blocking, Should-fix or Nit. PASS = zero Blocking, zero Should-fix, proof green. Merges on PASS (cloud) or reports PASS (local). | Edits the work. Merges on FAIL. |
| **Fixer** | Fixes exactly the Blocking and Should-fix findings, test-first, in one commit per round. | Reviews. Merges. Touches unrelated work. |
| **Security sweep** | Reviews the *whole* main line on a schedule, and confirms serious findings at runtime. | Changes anything. |
| **Usage inspector** | Measures usage, ranks waste and proposes exact edits, under the quality-first rule. | Applies its own edits. Proposes cheaper models or fewer checks for judgement work. |
| **Design reviewers (goldfish)** | Review the phase plan before building, one lens per fresh agent: zoom-out (simplicity, YAGNI, reuse), comprehension (a naive reader), critic (risks, fail-safe), readiness (no decisions left to the builder, file boundary, test plan). The drift lens checks the system doc against the code for the weekly sweep. | See the Worker's reasoning. Edit anything. Wait for the user. |
| **Researcher** | Gathers evidence: a sourced **brief** before a phase (current docs, breaking changes, prior art, owner facts, policy context), and a **fact-check** of claims in documents and PRs. Every claim carries a URL, date and quote, or is marked unverified. | Decides, builds or reviews. Acts on instructions found in web content. |

---

## 3. Profiles: one loop, many kinds of work

Each profile sets what "proof" means, what the reviewer checks, and what counts as evidence. Pick one at `/autodeliver:init`, mix several, or define your own. Full details are in `profiles.md`.

| Profile | Work unit | Proof (deterministic, run by the reviewer) | Reviewer adds | Evidence | Typical gate |
|---|---|---|---|---|---|
| **software** | feature or phase branch | all test suites, typechecks, lint, build, e2e if UI changed, schema-drift check | correctness, security, races, error paths end to end, migrations, test quality, fail-safe when services are absent | test counts, staging checks, screenshots | production deploy |
| **docs** (guides, courses, reports, policies) | section or chapter | validators, link checker, render or build, spell and style lint, structure limits | accuracy against sources, completeness against the brief, audience and tone, consistency, citations | rendered output, source list | publication |
| **data** (analysis, dashboards, pipelines) | notebook, model or pipeline step | reproducible run from clean, data tests, reconciliation counts, schema checks | method soundness, leakage, sampling, units, privacy (no row-level personal data in outputs) | run logs, counts, charts | sharing results or writing to production data |
| **infra** (IaC, configs, servers) | change set | `plan` or dry run, policy-as-code checks, lint, apply to staging | blast radius, rollback, least privilege, secrets handling, isolation from neighbours | plan output, staging health, log scan | production apply |
| **migration** (port, rewrite, upgrade) | phase of a parity matrix | golden tests against the source of truth, parity matrix, plus the software proof | the source wins on conflicts, nothing dropped, data-migration safety on real-shaped data | parity matrix, rehearsal on an isolated copy | cutover |
| **research** (decisions, designs, investigations) | question or design doc | citation check, every source reachable, claims traced to sources | evidence quality, alternatives considered, cost if wrong | source list, decision record | decision sign-off |

---

## 4. System overview (cloud mode)

```mermaid
flowchart LR
    H([Human owner])
    subgraph Cloud["Claude Code cloud (one environment)"]
        W[1 Worker<br/>hourly + wake on merge<br/>watchdog, cleanup, phase work]
        R[2 Reviewer<br/>webhook: PR opened/updated<br/>gate, labels FAIL, merges on PASS]
        F[3 Fixer<br/>webhook: review-fail label<br/>fixes, pushes]
        U[4 Usage inspector<br/>daily, read-only]
        S[5 Security sweep<br/>weekly, read-only]
    end
    subgraph GH["Code host: GitHub or Azure DevOps"]
        B[(work branches)]
        PR[(Pull requests<br/>labels + marker comments)]
        MAIN[(main branch)]
        I[(Issues: usage report,<br/>security sweep)]
    end
    subgraph ENV["Optional: staging"]
        G[HTTPS ops gate<br/>token per client]
        STG[(Staging)]
        PROD[(Production)]
    end
    W -- commits, opens PR --> B
    B --> PR
    PR -- opened/synchronize --> R
    R -- FAIL + label --> PR
    PR -- labeled --> F
    F -- push fix --> B
    R -- PASS: merge commit --> MAIN
    PR -- closed --> W
    W -- ship / verify / log scan --> G --> STG
    U -- report --> I
    S -- findings --> I
    I -- routed into phases --> W
    H -. only at hard-limit gates .-> PROD
```

## 5. Phase lifecycle

```mermaid
flowchart TD
    A[Start phase from latest main] --> B[Read HANDOFF, roadmap,<br/>ledger, latest security findings]
    B --> RB[Research brief:<br/>researcher agent, every claim sourced]
    RB --> C[Write the phase plan as a design doc:<br/>design, decisions, file boundary,<br/>tasks with done-when, test plan]
    C --> DR[Design review: 4 fresh lenses in parallel<br/>zoom-out, comprehension, critic, readiness]
    DR --> DQ{Blocking or<br/>Should-fix?}
    DQ -- yes, rounds left --> DF[Change the plan or rule,<br/>re-run only those lenses] --> DR
    DQ -- no, or cap: open items become rulings --> DL[Ledger: design review recorded]
    DL --> D{Each task}
    D --> E[Test-first or check-first work<br/>+ guard skills]
    E --> F[Per-task review subagent]
    F --> G[Commit + ledger line + push]
    G --> D
    D -- all done --> H[ONE simplify pass over the whole phase<br/>/simplify, own commit]
    H --> SY[Update the system doc<br/>if the system's shape changed]
    SY --> I[Full proof]
    I --> J[Final whole-phase review]
    J --> K[Staging ship + checks<br/>if the profile has staging]
    K --> L[Log scan: fix every error<br/>the phase caused]
    L --> M[Evidence: screenshots, rendered output,<br/>counts, committed]
    M --> N[Write-up + roadmap update]
    N --> O[Open for review]
    O --> P([End this run. The next phase<br/>starts fresh after the merge.])
```

**Simplify once, at the end of the phase.** A per-task simplify churns work that the next task changes again. One pass over the whole phase sees duplication across tasks, and its own commit is easy to review and revert.

## 5a. Design review: the elephant and the goldfish

The gate reviews finished work, so a design problem found there costs a fix round and a full re-review. Several lessons in section 10 are of that kind: plan items left undelivered, fail-safe gaps, a rule that rested on an outdated fact. This step, taken from Google's [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model) (EGM), looks for them while the plan is still text.

- **The elephant** is the Worker. It holds the research brief, the system doc, the roadmap and the rulings, and writes the phase plan as a design doc (sections in `HANDOFF.md`, phase workflow step 1).
- **The goldfish** are the `design-reviewer` agent, dispatched once per lens, in parallel. Each sees only the plan, the documents it links and the repo. **The brief carries no summary of the Worker's reasoning:** a reviewer told why the plan is right tends to agree with it, so isolation is what makes the review worth its tokens.

| Lens | Asks | Catches |
|---|---|---|
| zoom-out | Is this the simplest design that solves the root problem in this codebase? | YAGNI, premature optimisation, rebuilt helpers (it searches the repo), wrong placement |
| comprehension | Can a newcomer paraphrase what this proposes and how the system works today? | undefined terms, silent prerequisites, sections that don't connect |
| critic | Will it hold up? | unbacked claims, a feature that rests on a quality nobody measured, a way into an action that its rule does not cover, failure modes, fail-safe and security gaps, cost, a guard term on an irreversible or privacy-relevant act that nothing re-checks between the check and the act, security state (rate limits, lockouts, audit de-duplication) in a cache that evicts or times out, a counter sequence split across transactions, a security-heavy phase not marked as one |
| readiness | Can a fresh session build it without making a design decision? | open decisions, a missing or wrong file boundary, a thin test plan (no test per guard term, no model-based test for a guard over events that can be lost or reordered, no worst-case-shape test for an "at most N per window" rule, no test of the record a cap must still produce, a concurrency test that nests on one thread), a ruling that adds a guard with no test and mutant, a people-facing sentence with no behaviour test or a missing locale, unmeasured platform facts not measured first, another plan's request applied from a paraphrase, product behaviour restated across documents instead of one fact block tied to the code |

**What changes from EGM.** EGM is built around a human who approves the design and resolves each finding. Here no one waits on the user (principle 2):
- the Worker resolves each finding by changing the plan or by a ruling with its cost if wrong; a ruling that adds a guard also names its test and its mutant; after each change to the plan, it re-reads every people-facing sentence that depends on what changed;
- **cut before a third patch:** a feature or rule that gets a Blocking in two rounds in a row is not patched a third time. It is cut by a ruling, or, if the owner asked for it, the cut is put to the owner; an unattended run moves it to its own roadmap row, reports that, and goes on without it. A guard that something kept still needs is never cut;
- only the lenses that had findings run again;
- after `design_review.rounds` rounds (default 2), whatever is still open becomes a ruling, and building starts;
- people-facing texts (consent, notice and warning texts, and texts that make people a promise or ask them to agree) pass the `translation-reviewer` in every locale before the review closes, not in the build;
- the review is closed before any build starts: every round has run, its plan changes and rulings are in the plan, and the people-facing texts have passed. Plan amendments sent to builders already running caused rework worth about one gate round per phase;
- the one exception is an open Blocking that crosses a hard limit or fails unsafe: the Worker changes the plan or splits the phase, however many rounds that takes;
- each round's findings go into the pushed ledger as soon as the lenses return (restart safety), with each lens's report saved verbatim beside it.

**Measure first.** Every signal the design assumes is measured on the real inputs before round 1, and a feature whose existence depends on a measurable quality gets a short throwaway spike then, so no round is spent on a feature its numbers would remove. A platform fact nobody has measured is marked in the plan, and measuring it is the first build task (`HANDOFF.md` step 1).

EGM's other ideas are folded in like this:
- **File boundary.** EGM's "target scope & file boundary" becomes the plan's list of files. The gate treats an unruled file outside it as a Should-fix; delivery files, lockfiles and evidence are exempt. Phases planned before the `design-reviewer` agent was in the repo are exempt from the new gate checks.
- **Living spec.** EGM keeps specs in `docs/designs/` and checks them for drift. Here phase plans are *change* documents, so drift-checking them would flag every later phase. Instead there is one **living system doc** (`paths.system`, template `templates/docs/SYSTEM.md`). Each phase updates it when the system's shape changes, the gate checks that, and the weekly sweep runs the `drift` lens on it.

**Not adopted:** EGM's human approval step (replaced by rulings), its chat checkpoints (nobody is watching), and its brainstorm swarm (roadmap-level ideation stays with the owner at init). EGM's `/egm-bootstrap` is a good way to write the first `SYSTEM.md` for an existing codebase, if that plugin is installed locally.

**Measure it.** As with the loop itself (section 8), compare a few phases with and without the design review: Should-fix findings at round 1 of the gate, rounds to PASS, and total tokens. Keep it if it pays for itself.

## 5b. Skills: superpowers, /simplify and security-audit

The loop's steps match well-tested skills, and the Worker, Fixer and local loop use them when they are available. `templates/docs/HANDOFF.md`, section "Skills", has the full map:
- `writing-plans` for the phase plan, saved in our format;
- `test-driven-development` for each task, with `requesting-code-review` for the per-task review;
- Claude Code's `/simplify` for the one simplify pass per phase;
- `verification-before-completion` before anything is called done;
- `receiving-code-review` for the Fixer, and `systematic-debugging` when something is stuck.

Three rules keep this safe:
- **The playbook wins.** A skill makes a step more reliable but never overrides a rule in HANDOFF.md. Every step has a fallback, so a project without the skills still works.
- **Some skills are never used.** `subagent-driven-development` and `executing-plans` would replace the playbook's build, ledger and design review with their own. `finishing-a-development-branch` and `using-git-worktrees` would merge or move the work outside the gate. `brainstorming`, and `using-superpowers`, which routes to it, need a person to approve, so they belong only to `/autodeliver:init`.
- **Skills that say "ask your human partner" get a ruling instead.** The run writes a ledger ruling with its cost if wrong and continues. The design review replaces a skill's human plan review.
- **The Reviewer stays plain.** The gate uses none of these skills, so its rules can't drift with a skill update.

Cloud sessions don't load plugins, so `/autodeliver:init` offers to copy the unattended-safe superpowers skills into `.claude/skills/`, with their MIT licence. `/simplify` ships with Claude Code. The superpowers skills are by Jesse Vincent ([obra/superpowers](https://github.com/obra/superpowers), MIT).

**`security-audit` in the security sweep.** Cloudflare's `security-audit` skill ([cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), MIT) is a full audit method: a coverage ledger, isolated hunters, a fresh verifier per candidate, and records checked by two validators. Only the weekly security sweep runs it, in a bounded `quick` pass on source only; no other role uses it. Its records are leads: the sweep verifies them, confirms them on staging and classifies them itself. `/autodeliver:init` copies one pinned commit. The pin moves only in a plugin release, after the skill is re-read against the sweep's rules. Without a sandbox, few leads end as `confirmed`; what the skill still adds is a coverage ledger that names what was and was not looked at, and a fresh verifier per candidate. **Measure it.** Compare a few sweeps with and without the skill: findings kept after verification, and tokens. On the first run, count the sweep session's own tokens too, since it writes every brief.

## 6. The closed review/fix loop

```mermaid
sequenceDiagram
    autonumber
    participant P as Worker
    participant GH as PR
    participant R as Reviewer
    participant F as Fixer
    P->>GH: open PR (work branch → main)
    GH-->>R: pull_request.opened
    R->>R: round 1 full review + specialist agents<br/>+ plan completeness + FULL proof
    alt FAIL
        R->>GH: "PFX-REVIEW sha VERDICT: FAIL" + label
        GH-->>F: pull_request.labeled
        F->>F: fix Blocking + Should-fix test-first<br/>ONE commit, touched checks
        F->>GH: push + "PFX-FIXER sha" + remove label
        GH-->>R: pull_request.synchronize
        R->>R: round N: delta analysis + previous findings<br/>FULL proof before PASS
    else PASS
        R->>GH: "PFX-REVIEW sha VERDICT: PASS" + merge commit
        GH-->>P: pull_request.closed (wake)
    end
    Note over P,GH: Watchdog (hourly): review stalled → empty commit · fixer stalled → re-add label<br/>staging step needed → Worker does it · still stuck or cap reached → Worker takes the PR over
```

| Marker | Writer | Meaning |
|---|---|---|
| `<PFX>-REVIEW <sha> VERDICT: PASS\|FAIL` plus `(round N, full\|delta\|docs-only)` | Reviewer | The verdict for exactly that sha; the idempotency key. |
| label `<pfx>-review-fail` | Reviewer adds, Fixer removes | **Fires the Fixer.** Label events are supported triggers; comment events are not. |
| `<PFX>-FIXER <sha> round <k>` / `blocked: …; Worker takes over` | Fixer | What was fixed, or a hand-off. |
| `<PFX>-RETRY review\|fixer <sha>` | Worker | The watchdog's one retry per kind per sha. |
| `<PFX>-SECURITY <date>`, `<PFX>-SECURITY-NOTE`, `<PFX>-USAGE <date>` | Sweep, operator, inspector | Reports and corrections on their issues. |

## 7. Worker tick

```mermaid
flowchart TD
    T([Tick: hourly or PR closed]) --> WD[Watchdog over open PRs<br/>retry once, then take over]
    WD --> CL[Cleanup: delete merged branches<br/>with no open PR, idle over 30 min]
    CL --> Q1{Another session active?<br/>newest commit under 90 min, not mine}
    Q1 -- yes --> X1([Stop])
    Q1 -- no --> Q2{Open phase PR?}
    Q2 -- yes --> X2([In review loop: stop])
    Q2 -- no --> Q3{Only hard-limit gates left?}
    Q3 -- yes --> X3[Write the gate notice once,<br/>with evidence] --> X4([Stop])
    Q3 -- no --> PH[Run ONE phase] --> X5([Stop after the PR opens])
```

## 8. Local mode

```mermaid
flowchart LR
    B[Builder<br/>main session] --> R[delivery-reviewer agent<br/>read-only, runs the proof itself]
    R -- PASS --> D([Stop + report])
    R -- FAIL: findings --> F[Fixer<br/>main session or delivery-fixer agent]
    F -- only the listed findings --> R
    R -. cap reached .-> E([Stop: report what keeps failing<br/>and the next approach])
    H[[Hook: token log CSV, on by default<br/>per role, per round]] -.-> B
    H -.-> R
    H -.-> F
```

| Cloud piece | Local equivalent |
|---|---|
| Design review | the same `design-reviewer` lenses, dispatched by the main session before building (round 0 of `/autodeliver:loop` for new work) |
| Worker routine (build) | the main session; on a planning-tier session, a strong-tier subagent with a fixed brief (`/autodeliver:loop`, round 0) |
| Reviewer routine + webhook | the `delivery-reviewer` agent, dispatched each round by `/autodeliver:loop` |
| Marker comment | the reviewer's reply starts with `VERDICT: PASS` or `VERDICT: FAIL`, then the finding sections |
| Fixer routine + label | the main session (no cold start) or the `delivery-fixer` agent (cleaner separation); always the agent on a planning-tier session. The reviewer must always be separate. |
| Full proof | the profile's deterministic checks, run by the reviewer itself |
| Usage inspector | the token-log hook (on by default; `token_log: false` turns it off), plus the `usage-inspector` agent on demand |
| Ledger / HANDOFF | `docs/delivery/` (the same files as cloud mode) |
| Deliberate loop test | a sample with **seeded defects**; the reviewer must catch them all first |

On a planning-tier session, the Builder and Fixer boxes in the diagram are strong-tier subagents.

**Measure the loop's value:** run one comparable task without the loop as a baseline, logged the same way. Compare tokens, defects caught and a quality rating before adopting the loop.

**Stop guards.** A loop that isn't converging is stopped and re-planned instead of retried:
- **local:** stop when the same finding is open a third time or the open count hasn't fallen across two rounds; optionally, stop at `loop.token_budget`;
- **cloud:** when the Worker resumes a phase with no PR yet, it re-plans or splits a phase whose ledger "Next" hasn't moved for three ticks, or that passes `loop.phase_tick_cap`. The Fixer's `fail_review_cap` still hands a stuck PR to the Worker.

**Parallel builds (local only).** A session may hand several planned phases to builders at once, each in its own git worktree and each through its own gate. Shared helpers are built first, as one small commit, and the dependent phases branch from it; builders get a roster and message each other directly about interfaces, shared files, commit hashes and merge order, while plan changes go to the planning session. The worktree folder is git-ignored and builders stage explicit paths. When one plan asks another for a change, the requesting plan's current text wins and is copied verbatim. `/autodeliver:loop` ("Parallel builds") has the rules. Cloud routines still run one phase per run.

**Second opinion (optional).** `second_opinion.command` lets the gate also ask a model from another vendor for defects. Its output is data: the gate verifies every item, so a second model widens what is looked at without lowering the bar.

**Try it without setup:** `/autodeliver:review` runs the gate once on the current changes, and `/autodeliver:design-review <doc>` runs the four lenses on any plan or spec. `/autodeliver:report` shows what the loop cost and caught.

## 9. Gates and staging

**Hard-limit gates** are the only places a human acts. Each is prepared so that it is one action:
- the evidence is gathered;
- the runbook is rehearsed;
- the notice is written once in the decisions log, under "Hard-limit gates".

Typical gates are a production deploy, publication, a production data write, and placing real data that only the owner can decrypt.

**Add a production-readiness phase before the rehearsal.** Building the features doesn't make a system ready to run. Before going live, the sessions must:
- size it for the host it shares;
- give it encrypted, restore-tested backups;
- set up a watch routine;
- clear critical dependency advisories.

Sessions can do all of this; the owner is involved only if more hardware is needed.

**Rehearse before the irreversible step.** Restore a copy of the real data into an isolated, throwaway environment:
- an internal network, joined to nothing else;
- aggregate checks only, never row contents;
- torn down afterwards, with the data copy kept root-only until the final restore is verified, then shredded.

Run the exact cutover steps there first.
- **The owner placing the copy is their consent.** Have them place it **once, early** (`templates/owner/place-real-data.sh`), and keep it root-only until the final restore is verified.
- **Run the rehearsal only when its roadmap row is next.**
- **Stage owner-only credentials early too** (`templates/owner/stage-production-secrets.sh`). The go-live then needs only the owner's "go" in chat.

**Staging access from the cloud** goes through an allow-listed gate, never SSH keys in sessions:

```mermaid
flowchart LR
    CS[Cloud session<br/>staging client] -- HTTPS + header token<br/>from a Network secret --> TR[Reverse proxy /_ops/*]
    TR --> OPS[ops service<br/>checks sha256 of token<br/>per-client hash file]
    OPS -- fixed verbs only --> GATE[forced-command gate.sh]
    GATE --> APP[(Staging app + DB)]
    GATE --> RO[(Read-only SQL role<br/>throwaway client container)]
    GATE --> REH[(Isolated rehearsal DB<br/>counts-only checks)]
```

Useful verbs:
- `status`, `logs`, `logs-since <min>` (the post-deploy log scan);
- `upload` and `deploy <sha>`;
- `sql-ro`;
- test-account helpers restricted to `@example.com`;
- `rehearsal-up|restore|migrate|check|down`;
- an app API proxy that still requires the app's own login;
- **configuration without an operator:** `config-show`, `gen-secret`, `set-config`, `apply-config`, `run-cli` (allow-listed app CLIs) and `prune-images`. CLI-only secrets live in a file the app never reads.

See `templates/staging/`.

## 10. Lessons learned

| What happened | Rule |
|---|---|
| Azure DevOps has no event for a PR label change, so a label can't fire the Fixer there. | On Azure DevOps the **Reviewer fires the Fixer** through the routine fire endpoint after posting FAIL (the label stays as a visible marker), and the Worker's watchdog re-fires a stalled Fixer the same way. |
| The routine docs say cloning needs GitHub, yet routines with no repo attached cloned Azure DevOps repos fine with `git clone https://pat:$ADO_PAT@dev.azure.com/…` (`dev.azure.com` is on the default Trusted list). | On Azure DevOps, routines have `sources: []` and clone in the prompt's first step. |
| A service hook POSTs its own event JSON; the fire endpoint reads only a top-level `text`, so the run started with no PR context. | Prompts never depend on the trigger: they find their work from the host state (open loop PRs without a review of the head). |
| Every routine acts as the one PAT owner on Azure DevOps. | Authorship proves nothing there: the exact marker format, the per-sha claim and the sha-pinned merge carry the trust. |
| Azure DevOps service hooks have no source-branch filter, so they fire for people's own PRs into the gate branch too. | Filter on target branch in the hook; every prompt keeps only `<branch_prefix>*` PRs and exits on the rest. |
| A failing service-hook subscription goes on probation, then gets disabled, silently. | The Worker's watchdog lists the subscriptions each tick and re-fires stalled routines by hand. |
| `issue_comment` webhooks never fired the routine. Comment events aren't a supported trigger; only pull request, release and issue events are. | Drive the Fixer with a **label** (`pull_request.labeled`). |
| GitHub triggers support filters (base and head branch, labels, draft, merged, author, title, body). | Filter each trigger to cut wasted runs. For example: Reviewer with base = main and head starting with the branch prefix; Fixer with labels including the fail label. **Also** keep the event, branch and marker checks in every prompt, as defence in depth. |
| GitHub events over the per-task or per-account hourly caps are dropped, not queued. | The Worker's watchdog is required, not optional: it re-fires stalled reviews and fixers. Schedules can't run more often than hourly. |
| `pull_request.*` events also fire for the bot's own pushes. | That closes the loop. Guard it with per-sha markers and a cap. |
| GraphQL was unavailable in cloud sessions. | Use REST `gh api` or the GitHub MCP tools. |
| Cloud sessions can't be messaged from other sessions. | Talk to them through files (ledger, HANDOFF) and issues. |
| Plugins don't load in cloud sessions. | `/autodeliver:init` copies the agents into the repo's `.claude/` folder, which cloud sessions do load. |
| Reviewers that scoped the *proof* to the delta passed broken heads. | Scope the **analysis** per round; always run the **full proof** before PASS. |
| A reviewer passed a phase with only 15 of 21 plan items done (2 partial, 4 not done; the PR merged before the final task ran). | A plan-completeness section is mandatory; a missing item is a Should-fix. |
| The Fixer pushed a fix and a formatting commit a minute apart, which triggered two full reviews. | One commit per round; never push formatting-only commits. |
| Long sessions re-read 700K+ contexts every turn. | One phase per session run; state in files; narrow subagent briefs. |
| A persistent Worker session carried four phases in one growing context, and while it was busy its hourly cleanup never ran (merged branches stayed for hours). | Run every routine with `persist_session: false`. State lives in the pushed ledger (push at least every 30 minutes), and the 'another session is active' check prevents overlap. |
| Two webhook events on one PR started two reviewers on the same sha, and both posted a full review. | The reviewer re-checks for an existing review of the sha right before posting, and stops silently if one appeared or the head moved. |
| Two reviews of one sha reached the Fixer, which answered only the latest; five Should-fix items (one a privacy leak) needed an extra fix round and review. | The Fixer answers the **union** of every FAIL review on the current head and lists the review ids it answered. The Reviewer also **claims** a sha before reviewing, so a second run stops before doing a full review. |
| An operator rebuilt two routine prompts from an old local copy, silently reverting another session's additions (research agent, web tools, gate ordering) for about 10 hours. | Always `get` the live prompt and edit that, never an older copy. Compare tool lists and key sections before and after each update. |
| Two container restarts in one phase: one killed an implementer with 8 files uncommitted, the other cut a full e2e run while five finished fix commits sat unpushed. A fresh session also lost review findings kept only in the git-ignored workspace. Elsewhere, the ledger held only the rulings, and a review's nits and details were lost. | Push before every long step; save each review report verbatim beside the ledger, committed in the round it arrives; follow a fixed recovery order after a restart (HANDOFF "Restart safety" and step 2, `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt). |
| Routine API calls from an operator session returned 404 and an empty list, because that session was logged into a different claude.ai account. The routines were fine. | Routines belong to one account. Check `list` before deciding a routine is gone, and use the owning account's login to inspect or edit them. |
| The cloud permission check blocked the Reviewer's merge after its own PASS ("Merge Without Review"), although the same step had merged earlier phases. The PR sat unmerged for 6 hours, and the Worker kept waiting on the open PR. | The Reviewer merges through the REST endpoint pinned to the reviewed sha, and first states that it is carrying out its own posted PASS. If the merge is still blocked, it posts `<PFX>-MERGE-PENDING` and sends a push notification. The Worker's watchdog flags a PASS left unmerged, but never merges it. The official fix is an organisation-managed `autoMode` setting; without one, an optional external merge pipeline (`templates/merge-gate/`, `merge.by: pipeline`) can complete trusted PASS heads (cloud-setup.md, "Unattended runs"). |
| Unattended runs hung for good on a permission prompt raised by a shell heredoc; the run lock went stale and later runs redid the work. | Routines create and change files only with Write and Edit, keep each Bash command short and single-purpose, and pass JSON to `curl` as `-d @file`. |
| A PASS sat unmerged for 13 days: the Reviewer's merge was refused, and the owner missed the single push notice. The Worker correctly refused to merge or start the next phase. | Don't rely on the owner reading one notice. Run the merge gate unattended: a pipeline, or a systemd timer on a server you already run (`templates/merge-gate/server/`). A scheduled task on the owner's PC only works while the PC is on. |
| The Worker's MERGE PENDING stop came before the branch cleanup, so merged branches stayed for 13 days. | Run the cleanup before any early stop. |
| An hourly Opus Worker ran about 24 times a day for 13 days with nothing it was allowed to do, because the port was waiting on the owner. | While the loop waits on an owner gate, lower the Worker's cron (for example every 4 hours; a merge still wakes it at once), and restore it when work resumes. |
| Pushing setup changes onto an active branch forced catch-up merges. | Change the setup between phases; mid-phase, touch only docs and tools. |
| A prompt updated mid-run took effect only at the next tick. | Expect a one-tick delay; for urgent changes, also leave a ledger note. |
| A routine nobody had triggered was untested. | Trigger every new routine once by hand and read its output. |
| Turning on dependency alerts showed hundreds at once. | The security sweep triages them (runtime vs dev-only, minimal upgrades); phases pick them up. |
| A retention job counted unsent warning emails as sent, so it would have erased accounts without notice. | **Fail safe** when mail, payments, storage or an API is absent. The gate checks this, and caught a second case later. |
| A flaky suite failed once in six runs. | Re-run once to tell flaky from broken; a flaky test is a Should-fix. |
| The first security sweep rated a finding HIGH from code reading; a live check refuted it. | Confirm every HIGH or CRITICAL at runtime on staging. Post corrections as `<PFX>-SECURITY-NOTE`. |
| The cloud token got 403 on the dependency-alerts API. | Fall back to the package manager's audit. |
| A phase was told to "check findings at the next phase". | When a report lands mid-phase, add an intake note to the active ledger. |
| Every new staging setting or secret needed a human with server access. | Allow-listed config verbs: generate-once secrets that are never printed, typed and range-checked settings, `apply-config`, and allow-listed app CLIs via `run-cli`. Sessions never get code execution as root. |
| A secret meant only for the operator CLI was loaded into the app's environment. | Keep two env files: one the app reads, one only the CLI runner reads. |
| Old build images grew toward a full disk on a shared host. | Prune this project's own tags after every deploy (keep the running one + 2). Never run a global prune on a shared host. |
| An operator CLI was excluded from the image by `.dockerignore`, so the production step would have failed. | Smoke-test every operator CLI from the built image (`run-cli … --dry-run`) during the phase. |
| Cloud sessions can't install server files, by design. | Sessions list repo-side server changes under "Pending installs"; the operator installs them during the next progress check. |
| A rehearsal step shredded the owner's data copy, so the final restore would have needed the owner a second time. | Keep the copy (root-only) until the final restore is verified; shred only then. |
| A Worker that treated "backup present" as "go" would have rehearsed on real data before the build phases were done. | Gate a rehearsal on its roadmap row being next, not on the data being present. |
| Nits left at a PASS were lost between phases. | The next phase copies them into its ledger, and does each one or routes it with a ruling. |
| A delta-round PASS skipped e2e although the PR as a whole changed the UI. | Run e2e on every PASS whenever the whole PR touches the UI. |
| An attempt to relax the production hard limit through a file-recorded approval was blocked by the safety system. | Production approval stays a chat message from the owner, by design. Prepare everything else so that it is the only step. |
| The roadmap ended at "features done → go live", with no backups, monitoring or capacity check for a server shared with another production site. | Add a production-readiness phase (capacity, encrypted backups + restore test, watch routine, dependency batch) before the rehearsal. |
| A playbook rule ("webhooks have no filter") was out of date; the platform's docs had changed. | Facts drift. Each phase starts with a **research brief** from the `researcher` agent, and rulings on external facts cite its sources. |
| A long "waiting on you" list built up. | Sessions resolve visual checks, translations, policy and owner facts themselves; only hard-limit gates remain. |
| The CLI account switched to another organisation, so routine calls returned 404. | Check which account is signed in before managing routines (`/login`). |
| Pasting a secret through the clipboard stored the wrong value. | Verify secrets by length and sha256; never print them. |
| Shell quoting broke remote heredocs. | Copy files to servers with `scp`, not inline heredocs. |
| `pipefail` with `head` aborted scripts. | Avoid `head` on pipes under `pipefail`. |
| Free GitHub plans have no branch protection on private repos. | Only the gate merges; it is a hard limit in every prompt. |
| A plan's check ("is this folder git-ignored?") passed on the author's machine in a repo with no ignore entry, because a machine-wide git ignore file matched it. The unattended session has no such file, so the health check would have passed while the run skipped the feature. | A check that decides what an unattended run does reads only the repo's own state (`git -c core.excludesFile= check-ignore …`). Run every new check both ways, pass and fail, before it goes into a plan. |
| A plan to use a third-party skill unattended rested its safety claims on the skill's top file. The files that brief its subagents, and the programs it runs, had not been read. | Before a third-party skill runs unattended: read the files that drive its subagents, scan the programs it runs for network, process and write calls, and pin the commit that was read. The plan says what was read, scanned and not read. |
| A skill copied into `.claude/skills/` for one routine was open to every role, and the Reviewer's prompt already allowed "vendored security skills". | When a skill is added for one role, say in the charter which roles never use it, and search every prompt for wording that already lets it in. |
| Text added to a plan to settle the first design-review round caused most of the second round's findings, and rules given as a summary ("four short bullets") came back as "the builder would be writing the rule". | In a repo where wording is behaviour, the plan carries the exact text of each new rule from the first draft, and the steps live in one file with pointers from the others. |
| Design and reviewer subagents in a session that was not in auto mode ended without a report: their hand-back tool was refused and nothing told them to answer in text. | Every reviewer brief ends with "Deliver your full report as the final text of your reply." (`loop.md`, `design-review.md`). If a subagent still ends without a report, message it to deliver it; never re-run the review. |
| A design built its main mechanism on a signal (template words in a PDF text layer) that a measurement after two review rounds found on 2% of the real inputs. In another project, a short spike removed a whole feature from a plan, but only after a design round had reviewed it. | Before the design review, measure every signal the design assumes on the real corpus (counts by input kind) and put the numbers in the plan. A design reviewer cannot catch an assumption nobody measured. When a feature's existence depends on a measurable quality (recognition accuracy, speed, platform behaviour), run the spike before the first design round. Platform facts nobody measured are marked in the plan, and measuring them is the first build task, before anything depends on them (HANDOFF step 1, `/autodeliver:loop`, Worker prompt, `design-reviewer` critic and readiness lenses). |
| Unit tests and offline timings passed; the first end-to-end dry run on real data processed none of its 284 inputs, because downloads ran one by one before any processing and used the whole time budget. | For a data pipeline, an end-to-end dry run on real data (read-only, nothing sent) is part of the build proof, before the gate. Timings that skip I/O are not evidence for a time budget. |
| The local environment held a yanked release of a native-binding library; a fresh install took the next major version and broke a third of the feature's tests. The build's proof was green. | Pin native bindings with an upper bound, and run the suite once in a fresh virtual environment built only from the requirements file before the gate. |
| A deadline test passed before its fix because its fixture assumed a different default budget than the code. | A test proves a fix only if it fails on the old code; build fixtures from the code's own defaults, not from a number in the brief. |
| Parallel subagents writing helper files into one shared folder overwrote each other's scripts mid-run. | Give each parallel subagent its own work folder; shared inputs are read-only. Results go to one file per agent, keyed so the merge can reject entries outside that agent's assignment. |
| A session restart stopped nine background agents at once; none had saved anything yet. | Long-running agents write their results after every item (or commit after every item) so an interruption costs one item. Say so in the brief. |
| The user changed a decision mid-loop (go live at merge). It lived only in a commit message, while the plan's rollout and a ledger ruling still described the old path; the gate failed on it. | Record a user override as a numbered decision in the plan and a ledger line in the same commit that implements it, and update every plan section it contradicts. |
| An outward message named a provider outage as the cause of a failure; the outage banner was undated and months old. | Before naming a cause in a message to people, check its date and that its timing matches the failure; say "likely" until it does. |
| A long data-repair run was believed killed when a background notice arrived, so its range was run again in chunks. Its log showed it had finished, and its report (relative to its own first read) held the only list of what it changed; every rerun read the changed values as its baseline and reported nothing. | Before rerunning a job that writes data, read the end of its log to learn whether it finished and what it reported. Keep the first run's report; a rerun of a run-relative check proves nothing about the earlier change. |
| A comparison against a reference tool showed a two-day swap that looked like a defect; it was a documented decision (a reopened item counts on its first day, the reference counts it on a later day). | Before reporting a parity gap as a defect, check the plan's decisions for a rule that explains it, and report it as "by decision" with the alternative. |
| An input cap was raised, built, reviewed and dry-run to get facts people added to a source into a generated section; the section did not change, because the drafting call never received the source, only short per-item summaries. | Before changing a limit or a prompt so that an output reflects source facts, trace the data path from the source to that output section, and prove it with a dry run that plants a known fact in the source and finds it in the output (HANDOFF step 1 "Test plan", readiness lens). |
| Report links into another product's UI used its search for several item numbers; they were checked once and trusted. The product's search later began requiring every word to match, and every multi-item link went dead until a reader clicked one. | A deep link that relies on undocumented search or filter behaviour is clicked in the dry run of any change to that output; prefer stable one-item URLs, and when no URL can open a chosen set, show the items on hover or in an attachment instead (HANDOFF step 1 "Test plan", readiness lens). |
| A change widened what is sent to an AI service (whole notes instead of summaries). It reused a correct personal-data strip that no test covered on that path; the gate caught it with a mutant. | When a change widens data sent to an outside service, the build adds a test that plants personal data and credentials in each new field and asserts they are stripped (HANDOFF step 1 "Test plan", readiness lens). |
| A design revision rewrote a failure-state table, and one row quietly changed from "one failed item fails the batch" to "every item failed". A partial result would then have counted as success, and its cached reading would have been kept for good. | When a revision rewrites a failure table, re-check every row against the all-or-nothing rule and restate that rule beside the table. |
| A planned standing rule "upload whatever the target folder lacks" would have restored files that staff had deleted, merged or moved on purpose. An empty or cut-off listing would also have made every file look missing. | Missing from the target does not mean never written. Make a backfill a one-shot command: it lists the candidates, a person reads the list, and `--apply` writes only the reviewed names, re-checked just before each write. |
| A before/after regression gate compared two live dry runs taken minutes apart, with an AI reader on both sides. New replies and non-deterministic readings made it flap, and intended changes counted as regressions. | Pin the A/B inputs: the same past date (a fixed cut-off), no AI on either side, rows keyed by a stable id. List the intended differences in the plan; any other difference is Blocking. |
| A new input shape for an AI reader (several photos instead of one PDF) made the model reason longer, and 2 of 27 answers were cut off at the output-token cap. Unit tests with fake readers could not show it. | Before merging a new input shape for an AI step, run it live with the real model on real data, and count the failed or cut-off answers. |
| Tests for a state table set one condition at a time, so swapping the order of two checks (open before off-host, off-host before dry run) survived the suite. The gate's mutants found it. | State-table tests include a case for each pair of rows whose conditions can hold at once, and assert which row wins. |
| A long upload command running in the background was stopped halfway because the machine ran low on memory. | Every write command is resumable: it skips work that is already done and re-checks before each write. It prints progress as it goes, not only at the end. |
| A builder ran the proof in a throwaway checkout whose dependency folder was a link to another worktree's. The build output linked into it, and the forced removal of the checkout followed those links and emptied packages in the other tree. | Every tree that runs a build has its own dependency install; never link the dependency folder from another tree. Never force-remove or recursively delete a tree after a build: unlink any links first, without recursion. |
| A builder called a surviving mutant "equivalent" because another code path seemed to cover it. The gate found a case where the output differed: one direction of a two-way choice had no test. | A survivor counts as equivalent only with a named scenario that shows no observable difference. Each direction of a two-way choice (this set or that set, this rule or that rule) gets its own test. |
| A "warn once" dedupe key was also printed as the log line, and it held an e-mail and a free-text note. | Log lines carry positions and field names, never record values; a test asserts that the planted personal data is absent from the log. |
| A one-day request was first done by hand on production, and its undo deadline came before the release that automates it. | A temporary manual change gets its own dated undo task, recorded where the next session will see it, separate from any release. |
| Builds started while the design review was still open, and plan amendments were sent to the running builders; the rework cost about one gate round per phase. | Close the design review (every round, every ruling written into the plan) before any build starts. Never send plan amendments to a running builder. |
| Tests pinned a formula and an ordering rule, but each gate round found one more change they did not catch (a term, the tie-break, a filter); fixing one surviving mutant per round cost two gate rounds. | When a test pins a formula or ordering rule, check it against the full mutation matrix at once: each term alone, the tie-break and each filter must each fail a test when changed. A sort that is not stable needs a case whose expected order flips, not only reversed input. The gate reports every gap in one round. |
| An owner's manual setting was stored in the same table as learned values, so every consumer had to guess what a row meant; it took three gate rounds and a re-plan. | Store overrides apart from learned or derived data, and combine the two in one function at read time that every consumer calls. |
| The no-progress stop guard fired as designed: one finding with the same root cause stayed open for three rounds, the loop stopped, the root cause was re-planned, and the last round passed. | Keep the guard (`/autodeliver:loop` step 5, section 8). When it fires, re-plan the root cause; don't patch the symptom again. This confirms the existing rule. |
| Tests asserted one exact line in files that later phases also edit (service units, install scripts, web-server config), while the merge rules combined lines, so merged files broke gated tests. A test that read from a header to the end of the file silently constrained every step appended after it. | Keep one directive per concern in shared files, and write merge rules against what the gated tests assert. A test on a shared file asserts the lines it owns, never a span that runs to the end of the file. |
| Some parsers echo their input in the error message (for example `ConvertFrom-Json` in Windows PowerShell 5.1), so logging the exception from parsing a file that holds secrets writes the secrets to the log. | Never log the exception text from parsing a file that holds secrets; log the file name and that parsing failed. |
| Builders working in parallel worktrees relayed every interface question through the planning session until they were allowed to message each other directly. | In local mode, give parallel builders a roster and rules: talk about interfaces, shared files, commit hashes and merge order; never edit another builder's files; plan changes go to the planner; no secrets; no push or merge (`/autodeliver:loop`, "Parallel builds"). |
| On Windows, editors and Python wrote deploy files with CRLF line endings, while the deploy files and their tests need LF. | Normalise line endings to LF after writing deploy files on Windows, and check them before committing. |
| Several parallel phases needed the same shared helpers (a database helper, a named lock). | Build shared helpers first, as one small commit to an exact written spec, and branch the dependent phases from that commit. |
| Four gate rounds each found one more gap in the same guard on a privacy-relevant act: the target changed (it moved, appeared, vanished or changed order) between the check and the act, or a case the guard was meant to cover was skipped. The design review had not asked, for each guard term, what can change between the check and the act. | A plan that guards an irreversible or privacy-relevant act lists every term of the guard's condition with what can change between the check and the act and what re-checks it right before the act. The critic lens treats each term without that answer as a finding (HANDOFF step 1 "Risks and fail-safe", `design-reviewer` critic lens). |
| The gate found untested guard terms one per round, each through a mutation probe; a sweep over every term in round 1 would have found them all at once and saved two rounds. In another project, a sweep over the guards on irreversible acts (delete, send, overwrite) found 14 untested terms in code that was correct. | In the first round that sees a guard condition, the gate runs one mutant per term (dropped or inverted), each of which must fail a test, and reports every survivor together. Mutants run in a throwaway copy, never in the work under review (`delivery-reviewer`, Reviewer prompt, HANDOFF "Review gate", readiness lens). The builder writes one test per guard term in the same task as the guard, so the sweep confirms the matrix rather than discovering it (HANDOFF test plan, readiness lens). |
| A builder piped the test run into `tail` and committed on the pipe's exit code, which is `tail`'s; a red commit went in. | Run each proof command on its own, never through a pipe, quote its output and exit code, and commit only when that exit code is 0 (`/autodeliver:loop` build and simplify briefs and fix step, `delivery-fixer`, Worker and Fixer prompts, HANDOFF step 3 and "Skills"). |
| A parallel builder's `git add -A` committed the other builders' worktrees as gitlinks, and a follow-up commit had to remove them. | Builders stage explicit paths, never `git add -A` or `git add .`, and the repo ignores the worktree folder (`/autodeliver:loop` "Parallel builds", `/autodeliver:init` `.gitignore`). |
| A plan that applied another plan's request restated it from an older shape and numbering, so the two plans disagreed. | The requesting plan's current text wins. The applier copies it verbatim, with its path and section, never a paraphrase or summary (`/autodeliver:loop` "Parallel builds", HANDOFF step 1 "Context", readiness lens). |
| Long design reviews across several phases hit the usage limit twice; a committed handover note and per-phase ledgers kept every agent's work resumable. | Keep the resume note current at each milestone (design-review round, builder hand-over and return, gate round), not only when the limit is near. This extends the existing push-the-ledger rule to local sessions (`/autodeliver:loop`, HANDOFF "Autonomy charter"). |
| Hand-written tests of a privacy guard over a state machine (events that can be lost, reordered or never seen) each missed a different member of the same leak class, in three gate rounds in a row. A seeded, model-based test closed the class: it simulates the real-world state with its own independent oracle and asserts the invariant ("no output reveals X") on every generated sequence, except named accepted residuals. | A privacy or safety guard over such a state machine gets a seeded, model-based test with the guard's first version, not after the gate finds leaks. The gate plants known leaks as mutants and shows the model test fails on each (HANDOFF test plan and "Review gate", readiness lens, `delivery-reviewer`, Reviewer prompt). |
| Twice, a model test's oracle allowed more than the ruling said, so a reintroduced bug was filed as an "accepted residual" and the test stayed green. | Check an oracle's allowances with planted failures. A finding in a test or its oracle names its closing check, a planted case that must fail once the fix is in, not only the edit; the fixer runs that case and quotes the result (`delivery-reviewer` and Reviewer prompt reply format, `delivery-fixer`, Fixer prompt, HANDOFF "Review gate"). |
| An accepted residual was worded by one example sequence of events; the next variant of the same real-world situation was argued over, and the wording had to be widened a round later. | Word an accepted residual by its precondition in the real world (for example "a record already open before the watcher started"), never by one example sequence, and let tests and oracles allow exactly that precondition (HANDOFF step 1 "Risks and fail-safe", `design-reviewer` critic lens). |
| Performance and time-budget measurements on a shared PC were spoiled by CPU-heavy work running at the same time: the reviewer's parallel mutation runs, and agent sessions of other projects on the same machine. | Each measurement records machine-wide CPU per sample; a scenario whose other-process load passes a threshold set in the plan is invalid. Before claiming a quiet slot, check what is running on the machine, and hold heavy agent work while the slot runs. Keep the slot short: only a scenario that failed a limit needs it, and one far below its limits is judged on its quiet samples (HANDOFF test plan and "Review gate", `/autodeliver:loop` "Quiet slot for measurements", `delivery-reviewer`, Reviewer prompt, readiness lens). |
| A fix round deleted an unrelated documentation section while editing a neighbouring one; only the next gate round caught it. | A document section that other files or outputs point to gets a test that pins its heading and key line. In every round the gate diffs each changed document against its version on the base branch, and the fixer reads the diff of each document it edited and restores any section the findings did not name (HANDOFF test plan and "Review gate", readiness lens, `delivery-reviewer`, Reviewer prompt, `delivery-fixer`, Fixer prompt). |
| A JSON Schema `pattern` for ids ended in `$`, and the validator evaluated it with Python's `re.search`, where `$` also matches before a final newline; an id with a trailing newline passed, held back only by `maxLength`. (In ECMA-262, the dialect JSON Schema names, `$` matches only at the end of input.) | Don't rely on `$` to end a match in a validator built on Python's `re`. Checks in code use `re.fullmatch` (or `\Z`), and tests pin the trailing-newline case. |
| On Windows, desktop UI tests could not bring their test window to the foreground while no window was in front (the foreground lock), so a run could take an hour to fail. | A test harness checks its environment's preconditions at set-up (here, that a window has the foreground) and stops early with a clear, actionable message (here, that one real click is needed), rather than running until it times out. |
| Documents that describe what a product does (what it records, keeps, sends, deletes or protects) drifted from the code one paraphrase at a time: five gate rounds each found the next false sentence, and the fix rounds introduced new ones. | The plan states product behaviour once, in one numbered fact block; every other document points to fact ids. A claims table ties each fact to the code, with a test that the ids match, and before the gate an agent that did not write the documents checks each fact against the code (HANDOFF step 1 test plan and step 4, readiness lens, `/autodeliver:loop` "Claims check", Worker prompt). |
| Regex bans written to stop false claims about the product were never complete, and a pattern wide enough to be complete also matched true sentences: a regex ban cannot be both complete and harmless. | Treat a regex ban on false claims as a smoke check: a gap in its pattern's breadth is a Nit. A false sentence it missed is still a Should-fix, and the claims sweep and fact check carry the real proof (`delivery-reviewer`, Reviewer prompt, HANDOFF "Review gate"). |
| A sentence that a fix round added to settle a finding failed review twice, and each rewrite drew a new finding. | When a sentence a fix round added fails review twice, remove it rather than rewrite it a third time; if a finding or a plan task needs its content, point to the fact id instead (`delivery-fixer`, Fixer prompt, `/autodeliver:loop` step 4, HANDOFF "Review gate"). |
| Writing documents about a product surfaced gaps in the product itself; a document that described the intended behaviour would have promised a fix nobody had planned. | Route each product gap as a product item (a roadmap row with a ruling) the moment it is found, and list routed items in the document's gap list and in the gate notice line, so no document promises the fix (HANDOFF step 3, Worker prompt). |
| A reviewer who found one false claim found the next ones only in later rounds, until a systematic sweep found the rest at once. | On one claims gap, the gate sweeps every changed document: grep for the whole words `never`, `only`, `all`, `no`, `not recorded` and `deleted`, check each hit against the code, and report every false sentence together. The builder runs the same sweep and commits its list before hand-back, and the fixer re-checks the lines it changed (HANDOFF step 4 and "Review gate", `/autodeliver:loop`, `delivery-reviewer`, `delivery-fixer`, Reviewer, Worker and Fixer prompts, readiness lens). |
| On a shared PC, heavy review work (mutation sweeps, full proofs) run as several background processes starved the machine of memory, and the background runs were killed part-way. | In a local run on a shared machine, run heavy work strictly one process at a time at below-normal priority. Prefer sequential, resumable sweeps: one spec file per item, each result saved as it finishes, so a killed run resumes from the next spec (HANDOFF "Review gate", `/autodeliver:loop`, `delivery-reviewer`). |
| Rate limits, lockout counters and audit de-duplication keys were kept in a general cache that evicts entries and applies a default timeout; a flood of other keys or an idle gap reset them silently, and the limit they enforced opened again. | Rate limits, lockout counters and audit de-duplication are security state: keep them in their own store with expiry bound to their window, never in a cache that evicts entries or applies a default timeout (HANDOFF step 1 "Risks and fail-safe" and "Review gate", `design-reviewer` critic lens, `delivery-reviewer`, Reviewer prompt). |
| Tests of "at most N per window" rules drove only the literal flood (one key, many calls); the gate found the shape they missed: many keys, each retried just enough to cross each threshold. A multi-step counter update ran as several transactions, and its concurrency test nested the steps on one thread, where the inner transactions run as savepoints of the outer one, so it proved nothing about two writers. | Every "at most N per window" rule gets a test that drives the worst-case shape (many keys times enough retries to cross each threshold), not only the literal flood. Every multi-step counter sequence that must stay consistent runs in one transaction, with a test that drives it from real concurrent threads, each with its own connection; same-thread nesting is not a concurrency test (HANDOFF step 1 "Risks and fail-safe", test plan and "Review gate", `design-reviewer` critic and readiness lenses, `delivery-reviewer`, Reviewer prompt). |
| A fix that capped a flood of records also suppressed the very record the cap was meant to limit, so the event went unrecorded. | A fix that adds a cap or bound can open the opposite hole. Test both sides: the bound holds, and the record it must still produce is produced (HANDOFF test plan and "Review gate", readiness lens, `delivery-reviewer`, Reviewer prompt, `delivery-fixer`, Fixer prompt). |
| In a security-heavy phase, each gate round's new tests left guards untested, and in every round a mutation sweep run against whole test files found the ones they missed. | A plan says when its phase is security-heavy (it adds or changes authentication, authorization, rate limits, lockouts, audit records or secrets). For such a phase, budget a mutation sweep into every gate round from round 1, not only the first round that sees a guard: it covers the phase's security code (each guard, bound and counter check), not only the delta, with each mutant run against the whole test files that cover that code. On a shared machine it follows the one-process-at-a-time rule above (HANDOFF step 1 "Risks and fail-safe" and "Review gate", `design-reviewer` critic lens, `delivery-reviewer`, Reviewer prompt, `/autodeliver:loop`). |
| Two features failed the same plan review three times in a row, each time after a "complete" fix; cutting them closed the plan in one revision. | When the same feature or rule gets a Blocking in a second consecutive review round, put cutting it to the owner (or cut it, where the plan may decide) before patching it a third time; an unattended run moves it to its own roadmap row and goes on. This is the plan-level companion of removing a sentence that fails review twice (HANDOFF step 2, `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt, section 5a). |
| A plan's last Blocking was a second entry point (a command-line path) of a rule written for a page; elsewhere, three findings were one missing row of "ways in". | A plan that states a rule about an action lists every way into it once (page, API, command, timer, hardware key, file, intent) and what the rule does at each; the critic lens checks that table against the repo (HANDOFF step 1 "Decisions", `design-reviewer` critic lens). |
| A ruling that settled a review finding added a check without a test; the next review found it untested. | A ruling that adds a guard names its test and its mutant (HANDOFF "Autonomy charter", `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt, readiness lens). |
| A consent or notice text in a second language held many wrong or ambiguous statements, and the test plan pinned them as correct. | People-facing texts are in the plan word for word, and the translation reviewer passes them in every language, against the plan, before the design closes, not in the build (HANDOFF steps 1 and 2, `/autodeliver:loop`, Worker prompt, `translation-reviewer`, readiness lens). |
| A safety fix changed behaviour and made a promise to people false in a text the fix did not touch. | After each fix, to a plan or to the work, re-read every people-facing sentence that depends on what changed, not only the edited lines. Plans give each such sentence a behaviour test (HANDOFF step 1 test plan, step 2 and "Review gate", `/autodeliver:loop`, `/autodeliver:design-review`, `delivery-fixer`, `delivery-reviewer`, Worker, Reviewer and Fixer prompts, readiness lens). |
| A mask for a sensitive identifier was written as a fresh, narrow pattern; the gate found the same identifier passing unmasked with other separators and another digit script, while the repo already had a wider pattern for it. | A mask or detector for a sensitive value reuses the project's widest existing pattern for that value (any separators, other digit scripts) and is tested with each written form. |
| A later ruling relaxed an earlier "never" rule, and two statements of the old rule stayed in the design doc. | A ruling that relaxes or reverses a rule searches the plan for the old rule's wording and marks each statement superseded in the same change. |
| Fail-soft branches added to a send path (a lookup fails, the time limit passes, a lookup must run before the claim) were tested only through the helper; every branch survived the mutation sweep. | Each fail-soft branch on a path that sends or publishes has a test that runs the whole send through it and asserts what was sent, and the call order when the rule is about order. |

## 11. Cost and quality controls

- **Strong model** (`models.strong`) for building, design review, reviewing, fixing and security: this work is never handed to a lower model. A **mid-tier model** only for the usage inspector, which makes no quality judgements.
- **A planning-tier model plans; it does not build.** When a local session runs on a model named in `models.plan` (default: Fable and Mythos models), keep it for the work where a wrong decision costs most: understanding the task, research, the plan, resolving the design review, rulings and checking results. It hands the build, the simplify pass and every fix to strong-tier subagents with a fixed brief, checks what comes back, and never finishes the build itself. Handing work from a planning-tier model to the strong tier is not "a cheaper model" in the usage inspector's sense: the strong tier stays the floor. Cloud routines keep their tiers. HANDOFF "Models" has the rule; `/autodeliver:loop` has the steps.
- **Event-driven:** the Reviewer and Fixer run only on events. A Worker tick with nothing due exits in seconds.
- **Review rounds:** round 1 is full; later rounds analyse the delta plus the previous findings; docs-only deltas check only docs. **The proof is always full.**
- **Daily usage report:** waste ranked with evidence and exact edits, applied only after a human approves them.
- **Design review scales by round, not by depth:** all lenses in round 1; later rounds re-run only the lenses with open findings; the round cap turns the rest into rulings. The usage inspector may propose a different lens set for a project, never a cheaper model for a lens.
- **Weekly security sweep:** findings go to an issue, and phases must route each confirmed one. The same report carries the `## Drift` section from the system-doc check. It uses the `security-audit` skill when the project has it (section 5b).

## 12. Changing the setup while work runs

```mermaid
flowchart TD
    A[Setup change] --> B{What changes?}
    B -- routine prompt or trigger --> C[RemoteTrigger update<br/>takes effect at the next run]
    B -- charter, docs, agents --> D{Phase mid-task?}
    D -- no --> E[Commit with the next phase]
    D -- yes --> F[Commit docs/tools only to the active branch<br/>the session merges it at its next push]
    B -- server gate --> H[Check no job is running, back up,<br/>install, rebuild, test verbs end to end]
    C --> J[Check the next run log or ledger<br/>shows the new behaviour]
    E --> J
    F --> J
    H --> J
    J --> K{New routine?}
    K -- yes --> L[Trigger it once by hand]
    K -- no --> M([Done])
    L --> M
```

Record each setup change in the decisions log under "Decided by the user".
