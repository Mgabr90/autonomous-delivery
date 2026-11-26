# Changelog

## 0.11.0 (2026-11-15)

- **Dry run and live-vs-source check for live systems with no staging copy** (playbook section 9, HANDOFF "Phase workflow" step 5 and the review gate, `/autodeliver:loop` build brief, `delivery-reviewer`, routines 1 and 2): before go-live, a dry run on the platform's own runner with real inputs covering each changed path; after deploy, the deployed version read back and compared with the reviewed source, test switch off. Missing evidence is a Should-fix. Used when the deploy path is an admin console, a hosted editor or an API write to production; not when staging or an exact-commit pipeline covers it. Existing projects: copy step 5 and the new Should-fix line from the HANDOFF template into your HANDOFF, and update routines 1 and 2.
- **Playbook:** one lesson (an editor's "Execute" ran the saved version, not the edited buffer, and a field name from an export differed at run time).

- **Playbook:** four lessons (post-release checks read what the shipped code produced; confirm a measured difference's cause on raw records before designing for it; prove on the worktree's own install; rule on a platform-only proof failure before the gate and require the CI run before production).
- **Playbook:** three lessons (classify on typed state with a stated precedence; test precedence in each order; log one-time steps the day they run).
- **Playbook:** three lessons (reuse the widest existing pattern for a sensitive-value mask; a ruling that relaxes a rule marks every old statement superseded; each fail-soft branch on a send path gets an end-to-end test).
- **Playbook:** three lessons from a loop whose gate failed on missing tests, each written where its rule lives. Every argument a caller computes for a guarded pure function needs an integration-level test that fails on a plausible wrong value, and the gate mutates call-site arguments, not only the function body (HANDOFF step 1 "Test plan" and "Review gate", readiness lens, `delivery-reviewer`, Reviewer prompt; both reviewers may now run mutants in a throwaway copy outside the work under review). A refactor or simplify pass that moves a per-key guarantee from a query into an in-memory lookup adds a test with an item whose own key differs from the key it is looked up for (`/autodeliver:loop` simplify limits, HANDOFF step 4, Worker prompt, both reviewers). Every proof runs each command as its own step, never chained in one shell command or beside another heavy process, and records any heap or memory flag a step needed (`/autodeliver:loop` build and simplify briefs, HANDOFF step 4 and "Review gate", Worker, Reviewer and Fixer prompts, `delivery-reviewer`, `delivery-fixer`).
- **Playbook:** ten lessons from an alert-repeat loop and a dashboard-figure loop. Two are written into the test plan (HANDOFF step 1, `design-reviewer` readiness lens): a figure that must match numbers already sent gets the exact source query, window and sent counts as its spec and oracle; a figure compared with an outside number or shown for every tenant needs the store's coverage and each field's values and fill rate checked per tenant. One is written into `loop.md` and HANDOFF "Restart safety": after stopping an agent that edits files, check `git status` and `git diff` and restore what it left. Rows only: list every way an alert ends before changing its repeat; hold-backs key on the other output actually being sent; pin the exact resume time at a hand-over's end; no PowerShell double-quoted here-strings for files; chunk long verification reads; each defensive guard has a test that reaches it.
- **Playbook:** ten lessons from an alert-repeat loop and a dashboard-figure loop. Three are written into the test plan as two bullets (HANDOFF step 1, `design-reviewer` readiness lens): a figure that must match numbers already sent gets the exact source query, window and sent counts as its spec and oracle; a figure compared with an outside number or shown for every tenant needs the store's coverage and each field's values and fill rate checked per tenant. One is written into `loop.md` and HANDOFF "Restart safety": after stopping an agent that edits files, check `git status` and `git diff` and restore what it left. Rows only: list every way an alert ends before changing its repeat; hold-backs key on the other output actually being sent; pin the exact resume time at a hand-over's end; no PowerShell double-quoted here-strings for files; chunk long verification reads; each defensive guard has a test that reaches it.
- **Playbook:** four lessons from a settings-feature loop (own dependency install per building tree and no forced removal after a build, also written into the build brief in `loop.md`; an "equivalent" mutant needs a named no-difference scenario and each direction of a two-way choice its own test; logs carry positions and field names, never record values; a temporary manual production change gets its own dated undo task).
- **Playbook:** five lessons from an AI-judged mail-intake loop (probe real values before pinning verification rules; strict reads and claims for at-most-once sends; test-mode stand-ins; preview branches for pipeline-only sends; delta gates for mid-build user rulings).
- **Playbook:** five lessons from a document-conversion loop (probe the riskiest external assumption before building; rulings at the round cap; read-only live steps in parallel from a frozen copy; deadlines checked before each step; delete exported flow definitions that hold secrets).
- **Playbook:** four lessons from a diagram re-layout and export loop (prove the exported file itself, not an intermediate render; zoomed crops of every text box after each size change; check which element kinds a reused metrics tool covers; a source consistency check before re-layout, naming repairs that choose between readings).
- **Playbook:** two lessons from a classifier content split (guard an answer's narrower scope as data, sweep the same defect class after a Blocking fix, live near-miss probes in the proof; state per guard whether one vote or agreement triggers it).
- **Playbook:** seven lessons from a two-PR content delivery (replay past items as they arrived to prove a job that marks what it handled; transform before escaping; state a guard's criterion as a rule over the whole set; fact-check linked pages; what-if reports list every changed output; relabel stale evaluation labels by ruling; write provenance claims last).
- **Playbook:** six lessons from a backfill and photo-reading loop (restate all-or-nothing when a failure table is rewritten; one-shot reviewed backfills instead of "upload what is missing"; pinned A/B inputs; a live AI check for new input shapes; pairwise state-table tests; resumable write commands).
- **Playbook:** four lessons from a live-alert rule loop: wait for the day's away source before acting on people; test guard inputs at the call site; list unverifiable production facts as release checks with an owner-run probe; name where UI evidence comes from under network and auth limits.
- **Playbook:** three lessons, written into the test plan (HANDOFF step 1, `design-reviewer` readiness lens): trace the data path and dry-run a planted fact before changing a limit; click third-party deep links that rely on undocumented search or filter behaviour; test that personal data and credentials are stripped from data newly sent to an outside service.
- **Playbook:** nine lessons from a skill-building loop (UTF-8 mode for Python on Windows; run third-party scripts by path without writing caches; negative fixtures assert exact exit codes; LF line endings first; an eval assertion on the user's literal deliverable; reports name only real artefacts; fence eval runs; a fresh check for post-review design changes; checkers survive malformed input).
- **Playbook:** four lessons from a readability loop (rerun the fault tests on screens a round changed, and re-point, retire or repair them; reviewers type their own checks from the ruling text; run off-batch checks every round; same views across reader passes, page fixes apart from source questions, capped passes).
- **Playbook:** four lessons from a readability loop (rerun the fault tests on screens a round changed, and re-point, retire or repair them; reviewers type their own checks from the ruling text; run off-batch checks every round; same views across reader passes, page fixes apart from source questions, capped passes). Lessons-table rows only: the agents, commands, routine prompts and HANDOFF are not changed yet.
- **`visual-checker` checks its blur boxes:** a table of the areas each picture must hide, a code check that the boxes cover them with a planted fault, and a zoomed look at every delivered picture before it reports. Percentage boxes had missed small private details.
- **Playbook:** five lessons (find where a shown field is drawn before checking it, and verify a typed fix's place; a fault proves nothing on a check already red on the clean tree; a resource guard's refusal is "not run", never a result; blur-box coverage table, fault and zoomed look; full-size captures before the build starts).
- **Playbook:** nine lessons from a parallel multi-builder delivery on private data (folder isolation when git cannot hold the data; copy tools only from frozen siblings and broadcast check fixes; re-read cited rows and their neighbours, pin verbatim, bind quotes to their own row; reviewers probe the check; detached long jobs and orphan clean-up; notices to the coordinator only; targeted fix-round re-runs; answer from directory and records before asking people; declared changes for frozen inputs). Lessons-table rows only: the agents, commands, routine prompts and HANDOFF are not changed yet.
- **Playbook:** three lessons (request a new asset signed out; mount every surface that shows a state-dependent item; one approval covers one release and one exact text).
- **Playbook:** seven lessons from a parity port with a static-HTML scope change (tests that flip on an order or anchor; measure a reference reader cell by cell first; planner reruns a killed proof; commit before mutation restores; security decisions in tested pure functions; serving third-party generated HTML; measure print naming for framed content).
- **Reviewer briefs end with "Deliver your full report as the final text of your reply."** (`loop.md`, `design-review.md`): in a session that is not in auto mode the hand-back tool can be refused, and reviewers then ended with no report.
- **Playbook:** nine lessons from a data-pipeline loop (measure assumed signals before design review; end-to-end dry run on real data in the build proof; pin native bindings and prove in a fresh venv; fixtures from the code's defaults; separate work folders and per-item saves for parallel agents; record user overrides as decisions; date-check a cause before naming it).
- **Playbook:** two lessons (read a writing job's log before rerunning it; check the plan's decisions before calling a parity gap a defect).
- **Playbook:** nine lessons from a parallel multi-phase delivery, with these rule changes:
  - close the design review before any build starts, and never send plan amendments to a running builder (`loop.md`, HANDOFF step 2, Worker prompt, playbook 5a);
  - a test that pins a formula or ordering rule covers each term alone, the tie-break and each filter, and the gate reports every gap in that matrix in one round (HANDOFF test plan and "Review gate", `design-reviewer` readiness lens, `delivery-reviewer`, Reviewer prompt);
  - a test on a file that later phases also edit asserts only the lines it owns (HANDOFF test plan, readiness lens);
  - parallel builds in local mode: a worktree per builder, shared helpers first, a roster for direct messages between builders, merge rules written against the gated tests (`/autodeliver:loop`, with pointers from HANDOFF "Models" and playbook section 8).
- **Playbook:** six lessons on guards and proof hygiene, with these rule changes:
  - a plan that guards an irreversible or privacy-relevant act lists, per guard term, what can change between the check and the act and what re-checks it (`design-reviewer` critic lens, HANDOFF step 1 "Risks and fail-safe", playbook 5a);
  - the gate runs a mutation sweep over every guard term (one mutant per term, dropped or inverted) in the first round that sees the guard, in a throwaway copy, and reports every survivor together; plans name a test case per guard term (`delivery-reviewer`, Reviewer prompt, HANDOFF test plan and "Review gate", readiness lens);
  - builders and fixers run each proof command on its own, never through a pipe, and commit only when its own exit code is 0 (`/autodeliver:loop` build and simplify briefs, return check and fix step, `delivery-fixer`, Worker and Fixer prompts, HANDOFF step 3 and "Skills");
  - parallel builders stage explicit paths, and `.claude/worktrees/` is git-ignored (`/autodeliver:loop` "Parallel builds", `/autodeliver:init`, HANDOFF "Models", playbook section 8);
  - a cross-plan request is applied from the requesting plan's current text, copied verbatim (`/autodeliver:loop` "Parallel builds", HANDOFF step 1 "Context", readiness lens, playbook 5a and section 8);
  - the resume note is kept current at each milestone in local runs too, not only near a usage limit (`/autodeliver:loop`, HANDOFF "Autonomy charter").
- **Playbook:** seven lessons from review-gate loops, and one existing row strengthened, with these rule changes:
  - a privacy or safety guard over a state machine whose events can be lost, reordered or never seen gets a seeded, model-based test with its own oracle from the guard's first version, and the gate plants known leaks as mutants to show the test catches them (HANDOFF test plan and "Review gate", `design-reviewer` readiness lens, `delivery-reviewer`, Reviewer prompt);
  - a finding in a test or its oracle names its closing check, a planted case that must fail once the fix is in, and the fixer runs it and quotes the result (`delivery-reviewer` and Reviewer prompt reply format, `delivery-fixer`, Fixer prompt, HANDOFF "Review gate");
  - an accepted residual is worded by its real-world precondition, never by one example sequence (HANDOFF step 1 "Risks and fail-safe", `design-reviewer` critic lens);
  - one test per guard term is written in the same task as the guard, for every guard on an irreversible act (delete, send, overwrite, publish) or a privacy-relevant one, so the gate's mutation sweep confirms rather than discovers (HANDOFF test plan, readiness lens);
  - performance and budget measurements record machine-wide CPU per sample and are invalid over a threshold the plan sets; on a shared machine they run in a short quiet slot, claimed only after checking what is running, and the gate runs no mutants during one (HANDOFF test plan and "Review gate", `/autodeliver:loop` "Quiet slot for measurements", `delivery-reviewer`, Reviewer prompt, readiness lens);
  - a document section that other files point to gets a test pinning its heading and key line; the gate diffs each changed document against the base branch in every round, and the fixer reads the diff of each document it edited (HANDOFF test plan and "Review gate", readiness lens, `delivery-reviewer`, Reviewer prompt, `delivery-fixer`, Fixer prompt);
  - two row-only lessons: `$` in a pattern evaluated by Python's `re` also matches before a final newline; a test harness checks its environment's preconditions at set-up and stops early with an actionable message.
- **Playbook:** six lessons from documents that describe what a product does, with these rule changes:
  - product behaviour is stated once, in one numbered fact block that other documents point to by id; a claims table ties each fact to the code, with a test that the ids match; before the gate, an agent that did not write the documents checks each fact against the code (HANDOFF step 1 test plan and step 4, `design-reviewer` readiness lens, `/autodeliver:loop` "Claims check", Worker prompt, playbook 5a);
  - a regex ban on false claims is a smoke check: a gap in its pattern's breadth is a Nit, while a false sentence it missed stays a Should-fix (`delivery-reviewer`, Reviewer prompt, HANDOFF "Review gate");
  - a sentence a fix round added that fails review twice is removed, not rewritten a third time, or replaced by a pointer to its fact id (`delivery-fixer`, Fixer prompt, `/autodeliver:loop` step 4, HANDOFF "Review gate");
  - a product gap found while writing about the product is routed as a product item at once and listed in the document's gap list and the gate notice line, so no document promises the fix (HANDOFF step 3, Worker prompt);
  - the claims sweep: on one claims gap the gate greps every changed document for `never`, `only`, `all`, `no`, `not recorded` and `deleted` and checks each hit against the code; the builder runs the same sweep and commits its list before hand-back, and the fixer re-checks the lines it changed (HANDOFF step 4 and "Review gate", `/autodeliver:loop`, `delivery-reviewer`, `delivery-fixer`, Reviewer, Worker and Fixer prompts, readiness lens);
  - heavy work on a shared machine (mutation sweeps, full proofs) runs one process at a time at below-normal priority, as sequential, resumable sweeps with one spec file per item (HANDOFF "Review gate", `/autodeliver:loop`, `delivery-reviewer`). The Reviewer routine prompt is unchanged here: a cloud container is not a shared machine, and it already runs one command at a time.
- **Playbook:** four lessons from a security-heavy phase, with these rule changes:
  - rate limits, lockout counters and audit de-duplication are security state, kept in their own store with expiry bound to their window, never in a cache that evicts entries or applies a default timeout; a multi-step counter sequence that must stay consistent runs in one transaction (HANDOFF step 1 "Risks and fail-safe" and "Review gate", `design-reviewer` critic lens, `delivery-reviewer`, Reviewer prompt);
  - every "at most N per window" rule gets a test of the worst-case shape (many keys times enough retries to cross each threshold), and a multi-step counter sequence a test from real concurrent threads, since same-thread nesting runs as savepoints (HANDOFF test plan and "Review gate", readiness lens, `delivery-reviewer`, Reviewer prompt);
  - a cap or bound is tested on both sides: the bound holds, and the record it must still produce is produced (HANDOFF test plan and "Review gate", readiness lens, `delivery-reviewer`, Reviewer prompt, `delivery-fixer`, Fixer prompt);
  - a plan marks a phase security-heavy (authentication, authorization, rate limits, lockouts, audit records or secrets), and the gate then runs a mutation sweep over the phase's security code in every round from round 1, not only over the delta, each mutant against the whole test files; on a shared machine, one process at a time as before (HANDOFF step 1 and "Review gate", critic lens, `delivery-reviewer`, Reviewer prompt, `/autodeliver:loop`).
- **Playbook:** seven lessons from a stretch of design reviews (five new rows, two existing rows strengthened), with these rule changes:
  - cut before a third patch: a feature or rule that gets a Blocking in two design-review rounds in a row is cut by a ruling, or the cut is put to the owner; an unattended run moves it to its own roadmap row and never waits; a guard that something kept still needs is never cut (HANDOFF step 2, `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt, playbook 5a);
  - a rule about an action has one ways-in table, a row for every way into the action and what the rule does there, which the critic lens checks against the repo (HANDOFF step 1 "Decisions", `design-reviewer` critic lens, playbook 5a);
  - each review report is saved verbatim in the round it arrives, one file per report in `<phase>-reviews/` beside the ledger, or `.autodeliver/reviews/` without one (HANDOFF "Restart safety" and step 2, `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt, playbook 5a). The gate does not check for the files;
  - a ruling that adds a guard names its test and its mutant (HANDOFF "Autonomy charter", `/autodeliver:loop`, `/autodeliver:design-review`, Worker prompt, readiness lens, playbook 5a);
  - signals are measured, and a feature that depends on a measurable quality gets its spike, before the first design-review round; unmeasured platform facts are marked, and measuring them is the first build task (HANDOFF step 1, `/autodeliver:loop`, Worker prompt, critic and readiness lenses, playbook 5a);
  - people-facing texts (consent, notice and warning texts, and texts that make people a promise or ask them to agree) are in the plan in every locale, and pass the `translation-reviewer`, which checks them against the plan, before the design review closes (HANDOFF "No dependency on the user", steps 1 and 2, `/autodeliver:loop`, Worker prompt, `translation-reviewer`, readiness lens, playbook 5a);
  - after each fix, to a plan or to the work, every people-facing sentence that depends on what changed is re-read, and each such sentence has a behaviour test (HANDOFF test plan, step 2 and "Review gate", `/autodeliver:loop`, `/autodeliver:design-review`, `delivery-fixer`, `delivery-reviewer`, Worker, Reviewer and Fixer prompts, readiness lens, playbook 5a).


- **Playbook:** two lessons (identify records by structure and check the build's live count against an independent one before the gate; prove a hosted platform's write path early and give that part an off switch).


- **Playbook:** one lesson (scope local CSS overrides at least as specifically as the shared rule, and back layout claims with a geometry assertion).
- **Playbook:** five lessons (recount per item keyed by the raw source identifier and run a label-swap mutant; state a reused chart helper's denominator; leak checks on visible text, not raw HTML with inlined assets; contrast and animation-settled checks for rendered charts; proof output to an ignored folder, evidence committed as copies).

- **Playbook:** one lesson and a correction (check that every time in a "the vendor signal is late" comparison is recorded, not inferred, and keep inferred values distinguishable; the earlier vendor-fields row no longer claims a late push or prescribes "the earlier of push and poll").

- **Playbook:** four lessons (secret locations are as sensitive as secret values in widely read docs; search infrastructure repos before an owner TODO; inventory a fork by the team's own commits and deploy evidence; read infrastructure files through a redaction filter).
- **`/autodeliver:loop`:** a review that stops without a verdict (for example on a usage limit) is logged at once with the agent id, sha and reset time, and the same reviewer is resumed after the reset (a fresh review only if the head moved); it is not a round, and the resume never rests on a background timer alone.
- **Playbook:** three lessons (resume a reviewer stopped on a usage limit; a settings change that alters what a live system sends is a release, replayed on recent data first; capture raw vendor rows before fixing a live-data rule, and treat push signals as late or missing).

- **Playbook:** three lessons (read base files from the base ref and fetch a case-clashing base by refspec; list positional test assertions when a fixed-order output gains a field; role briefs never restate procedure).
- **Reviewer** (agent + routine prompt): mutants and base-branch runs go in a scratch copy or worktree, never in the work dir.
- **Playbook:** six lessons (guards follow a text into the output; backstops with negative lists; distinct inputs and scratch-copy mutants; probe before dropping an entry class; acceptance run on the final commit; no code through shell heredocs).
- **Playbook:** two lessons (check the owner's reference cases against the exact rule during design review; a diagnostic line of ids and rule inputs in the deciding stage).
- **Playbook:** two lessons (score an AI retry with the function that builds the output; list the alert classifier in the boundary when a plan adds a warning path).
- **Playbook:** two lessons (a mixed-direction fixture in the proof for right-to-left deliverables; size review rounds to the delta and check the usage budget before fanning out).

## 0.10.2 (2026-11-17)

- **Proof hygiene for the builder and the Fixer** (HANDOFF "Phase workflow" step 3; `/autodeliver:loop` build brief, routine 1 Worker, `delivery-fixer`, routine 3 Fixer): expected values come from the source data or a hand-written table, never from the artefact under test; a new view of rendered output is not built until its fit, contrast and text checks cover it at every width with every state open; no output is written into an input folder (the frozen data the proof reads as given), and inputs change only as declared changes.
- **Proof runs** (HANDOFF step 3, `/autodeliver:loop`, routine 1): a probe-gated chain (new and changed checks, then the full proof, then the mutation chain; a proof-file change restarts from the probe); each check in its own process with a time limit, where a timeout, crash or missing completeness line reads as FAIL; after a fix, only the mutations the change touches, with the full chain once before the gate; a result names the hash manifest of the file state it ran on. The builder's brief carries a fast probe.
- **Agents** (HANDOFF "Autonomy charter", `/autodeliver:loop`, routine 1): apart from the design-review lenses, one build or fix agent at a time, the unit closest to done first; only the main session starts runs on shared infrastructure.
- **The gate** (`delivery-reviewer`, routine 2 Reviewer, HANDOFF "Review gate"): every deliverable derived from the work is in scope and must match it; a crashed or timed-out check is a failure; counts must add up, or the proof is broken (Blocking). HANDOFF's fail-safe rule adds: verify an upload or send at the destination before reporting it done. `/autodeliver:loop` logs each round as it returns and reviews a fix made after the last round.
- **Design review:** the readiness lens checks the data contract and input-freeze point when the work reads data inputs (`design-reviewer`; HANDOFF step 1 "Decisions"; playbook section 5a).
- **Existing projects:** copy the new paragraphs of HANDOFF "Phase workflow" steps 1 and 3, "Autonomy charter" ("Agents") and "Review gate" into your own HANDOFF, update routines 1, 2 and 3 from the templates, and re-copy the `delivery-fixer`, `delivery-reviewer` and `design-reviewer` agents.
- **Playbook:** fourteen lessons (fallback rules that make equivalent mutants, sweeps without coverage; measures that move, scale or mis-calibrate what they measure; defects in new views; self-checking expected values; writes into proof inputs; results for the wrong file state; a fast probe and a probe-gated chain; a shorter proof per fix instead of skipping review; silent hangs, crashes and non-Latin output; too many parallel agents and sub-agent access to shared infrastructure; derived deliverables and the last review round; comments and word boundaries in text checks; pinned exceptions to a convention; empty-success uploads).

## 0.10.1 (2026-11-12)

- **A check covers the rule, not one instance of it** (HANDOFF "Phase workflow" step 3; `delivery-fixer`, routine 3 Fixer, routine 1 Worker and `/autodeliver:loop` carry the same rule): every value, view, layout, entry route and input method the rule or finding names is mapped to an assertion; class members are found from the output, never from a fixed list; behaviour is exercised, not presence; one mutation per distinct way the rule can break; one proof or mutation run at a time, with the work files' hashes compared after a mutation run. The Fixer reports the map and the mutations per finding.
- **The gate:** a fixed finding with a part that no check asserts is a Should-fix (`delivery-reviewer`, routine 2 Reviewer, HANDOFF "Review gate").
- **Values the plan pins are recomputed from the data before building**; the builder stops on a disagreement (HANDOFF step 3, routine 1 Worker, `/autodeliver:loop`).
- **Hard limits over files** name their file set and exceptions, and the proof scans exactly that set (HANDOFF "Hard limits", `config.md` `hard_limits`).
- **The cap report** marks each open finding as a defect in the work or a gap in the proof, with the count per round, and says a stop is never a PASS (`/autodeliver:loop`, routine 3 Fixer). HANDOFF restart step 4 also checks that no mutation is left in place.
- **Existing projects:** copy the new paragraphs of HANDOFF "Phase workflow" step 3, "Hard limits" and "Review gate" into your own HANDOFF, update routines 1, 2 and 3 from the templates, and re-copy the `delivery-fixer` and `delivery-reviewer` agents.
- **Playbook:** seven lessons (fix checks that covered only the reproduced instance; class rules checked against fixed lists; presence instead of behaviour; pinned values recomputed before building; hard limits without a file set; interrupted and batched mutation runs; a cap report that hid the trend).

## Unreleased

- **Playbook:** six lessons (run a plan's pattern against its own keep and remove examples before the design review; re-test every caller when a shared predicate gets an exemption; key A/B replays by request content and pin the clock; a value taken from a schedule fails the run when missing; leak checks never store the secret; no flag for behaviour the code already has).
- **Playbook:** seven more lessons (decide what an AI field's "unknown" means instead of falling back to the heuristic it replaces; anchor labels to field-counted data; agreement tests reach every branch; new fields get explicit fixture values; a rule change carries its doc sweep; check a gate script against a known value; no multi-line code edits through shell heredocs).


- **Playbook:** three lessons (verify UI automation by reading the system's data back, with idempotent steps; proof-check partial work left by a stopped agent; freeze the reviewed deployed artifact before a rebuild phase).
- **Playbook:** five lessons (spike the real target platform before fixing a design that depends on it; list insertion points and load order when patching existing code, with an undo-identity check; syntax-check generated code in the proof; reviewers run the proof with the configured interpreter and flags; keep design-review findings per lens per round).


- **Playbook:** four lessons (a dry run that rolled back per unit and so could not show cross-unit effects; a required field added to a shared type built outside the file boundary; a repository config that belonged to another workstream; parity gaps that were bugs in the old tool, settled against the primary source).


- **Playbook:** one lesson (reconcile a reported wrong figure against the source before changing code; look people up in every identifier format).


- **Playbook:** two lessons (ask the stakeholder before building a visible change they did not request; a dropped-column test checks every row, not only the header).


- **Playbook:** seven lessons (literal source codes quoted byte for byte and grepped in the proof; every figure from a saved evidence script, worded as what the data records; data notes a contradicted design instead of redrawing it; check a response shape and cap live API loops; publish only after `&&`; one file per deliverable; grep renames across companion files).
- **Playbook:** three lessons (closing owner named per path wherever closing is stated; a shared close sub-process never follows a step that already closes; proceed on defaults marked TO CONFIRM when a reviewer's call is waived).
- **Playbook:** two lessons (draw the outside party's events instead of messages to an empty pool; a label check exempts only the label's own edge).

## 0.10.0 (2026-11-12)

- **The security sweep uses Cloudflare's `security-audit` skill** ([cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), MIT) when the project has it in `.claude/skills/`. It covers the sweep's first two bullets (entry points and their guards; auth, crypto, secrets, injection, uploads, SSRF). Without it, or without Node.js, or when its output folder is not git-ignored, the sweep does those bullets by hand as before and says why.
  - Fixed settings in routine 5, so the skill has nothing to ask: full audit, profile `quick`, a budget of 40 agent calls, source review only (no target code run, nothing installed), run files only under the git-ignored `.autodeliver/security-audit/`.
  - Its records are leads. The sweep verifies them, checks them on staging and classifies them by its own scale. `needs_validation` records are never dropped for having no severity; at most 10 of them are checked on staging per sweep. A failed validator or an unfinished run falls back to work by hand for what the records do not cover.
  - Still one `<PFX>-SECURITY` report, now saying whether the skill ran and how it ended.
- **No other role uses it.** HANDOFF "Skills" says so for the Worker, Fixer and local loop, and the Reviewer prompt names it among the skills the gate never uses.
- **`init`** (cloud mode) offers to copy the skill from the pinned commit `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`, with its licence and a `SECURITY-AUDIT-VERSION` file, and always adds `.autodeliver/security-audit/` to `.gitignore`. **`doctor`** checks the copy: ❌ when the live routine 5 predates these rules; ⚠️ for missing files, another version, the folder not ignored, or no sweep report for 8 days.
- **Existing projects:** update routine 5 before adding the skill, and add `.autodeliver/security-audit/` to `.gitignore` (without that line the sweep does not run the skill).
- **Playbook:** four lessons (a check that passed only because of a machine-wide git ignore file; safety claims about a third-party skill that rested on its top file; a skill copied for one role that every role could use; exact rule text in the plan from the first draft).
- **A planning-tier model plans; the strong tier builds** (local sessions; HANDOFF "Models", playbook section 11, `/autodeliver:loop`):
  - a session whose model id matches `models.plan` (new, optional; default `fable`, `mythos`) keeps planning, rulings and checks, and hands the build, the simplify pass and every fix to strong-tier subagents;
  - a fixed brief that carries the hard limits, test-first working and the excluded skills, an explicit `model` on every dispatch, checks on return, and at most two re-dispatches before the loop stops;
  - the strong tier is the floor, and the usage inspector and `/autodeliver:report` may suggest the hand-over;
  - cloud routines keep their tiers;
  - existing projects: copy the "Models" section from the HANDOFF template into your own HANDOFF.

## 0.9.1 (2026-11-11)

- **Merge gate on a server you control:** `templates/merge-gate/server/` adds a systemd timer and service for `merge_gate.py`. They run every 10 minutes as an unprivileged user with a memory cap, and add no ports, no containers and no CI minutes.
  - `install-token.sh` takes the owner's token over SSH on stdin, stores it root-only, dry-runs once, and goes live only on a clean run.
  - The README has the install steps and a check against real PR history.
- **Worker template:** the MERGE PENDING stop now runs the branch cleanup first.
- **Playbook:** three lessons (a PASS left unmerged for 13 days on a missed notice; cleanup skipped by the early stop; an idle hourly Worker while the loop waits on the owner).
- **cloud-setup.md and config.md:** the server option, and `merge.pending_after_min` of about 30 for it.

## 0.9.0 (2026-11-07)

- **Superpowers and `/simplify` built into the steps** (HANDOFF "Skills", playbook section 5b). They are used when available, and each step falls back to the playbook's own text:
  - `writing-plans` writes the phase plan, kept in our format, and answers its execution question itself;
  - `test-driven-development` for each task, and `requesting-code-review` for the per-task review;
  - Claude Code's `/simplify` is the one simplify pass per phase (and runs once before review round 1 in `/autodeliver:loop`);
  - `verification-before-completion` before anything is called done;
  - the Fixer uses `receiving-code-review`;
  - `systematic-debugging` as before.
- **Guardrails:**
  - Never used: `subagent-driven-development` and `executing-plans`, which bypass the build, ledger and design review, and `finishing-a-development-branch` and `using-git-worktrees`, which merge or move work outside the gate.
  - `brainstorming` and `using-superpowers` are used only at `init`, where the owner is present.
  - `writing-plans` runs without its execution handoff.
  - "Ask your human partner" becomes a ledger ruling, and the design review replaces a skill's human plan review.
  - Skill severities map to Blocking, Should-fix and Nit.
  - The Reviewer uses none of these skills.
  - When a skill and HANDOFF disagree, HANDOFF wins.
- **`init`** offers to copy the unattended-safe superpowers skills into `.claude/skills/` for cloud sessions, with their MIT licence and a `SUPERPOWERS-VERSION` file. **`doctor`** checks the copies: licence present, no excluded skills, and version up to date when it can compare.
- **`/simplify` always gets an explicit range**, because its default diff can be empty on a pushed branch. In `/autodeliver:loop` it runs only on work built in that loop, after the build is committed.

## 0.8.0 (2026-11-07)

- **Unattended runs never wait on a permission prompt:** every routine prompt now forbids shell heredocs and multi-line inline scripts, keeps Bash commands short and single-purpose, and sends JSON to `curl` as `-d @file`. Shell heredocs had raised a prompt nobody could answer, which stalled runs. The Reviewer, usage inspector and security sweep now have Write, for request bodies and report files only. The Azure DevOps host doc states the `-d @file` convention once, for every call. CI checks that every prompt carries the rule.
- **Optional merge pipeline** (`templates/merge-gate/`, off by default, `"merge": {"by": "pipeline"}`): a workaround for when cloud permission checks keep refusing the Reviewer's own merge. A scheduled Azure Pipeline or GitHub Actions workflow, in a repo the routines never write to, completes only PRs whose current head has a trusted `<PFX>-REVIEW <sha> VERDICT: PASS` and no trusted FAIL, pinned to that sha. It skips forks, carries on past a refused merge, and fetches comments and mergeability only when needed. It has a dry-run default, stdlib-only code, and 44 tests. The default stays as it was: the Reviewer merges, or posts MERGE-PENDING for the owner.
- **`merge.pending_after_min`** (default 20): one setting for how long a PASS head may stay open before the Worker and `doctor` flag it.
- **Reviewer template:** the verdict line carries the full 40-character head sha.
- **cloud-setup.md:** a section on unattended runs (permission prompts, refused merges, the official org-managed fix, and the API dropping unknown `job_config` fields). Playbook: one new lesson (heredoc prompts), and the refused-merge lesson now names the official fix and the option. `init` mentions the option. CI runs the gate tests.
- **Playbook:** the plan-completeness lesson now says "15 of 21 done (2 partial, 4 not done)".

## 0.7.0 (2026-11-07)

- **Try it without setup:**
  - `/autodeliver:review [scope] [--fix] [--comment]` runs the independent gate once on the current changes, a branch, a PR or files. It detects the proof commands when there is no config.
  - `/autodeliver:design-review <doc> [--lens …] [--drift]` runs the four fresh-eyes lenses on any plan, spec or RFC, and writes a merged report beside it.
- **Loop metrics** (#3): `/autodeliver:report` and `scripts/loop_report.py`: tokens per loop, role, round and model from the token log, plus rounds to PASS, findings per round and design-review yield from the ledgers.
- **Stop guards** (#2): the local loop stops on no progress (the same finding open a third time, or no fall in open findings across two rounds) and at an optional `loop.token_budget`. In the cloud, the Worker re-plans or splits a phase whose ledger hasn't moved for three ticks or that passes `loop.phase_tick_cap` (default 12).
- **Optional second opinion** (#1): `second_opinion.command` runs another vendor's CLI on the diff; the gate verifies every item itself, and a failure never blocks a verdict. `doctor` checks it.
- **CI:** compiles and smoke-tests the report script.
- **Review fixes before release:** the report script never crashes (BOM, non-UTF-8, non-finite numbers, a folder path); the loop labels its tokens from round 0 so the budget and report include the plan, design review and build; the Worker's no-progress check moved to the resume step with a "Ticks" row in the ledger; ad-hoc reviews skip plan-based checks and include untracked files; the second-opinion tool is time-limited and checked for file changes (an edit is a Blocking safety finding). The loop marks its state file ended instead of deleting it, and the token-log hook labels the main session's last row before removing it, so `--baseline` and per-loop totals include the main session.
- **Repo:** `.github/assets/social-preview.png`, the source of the repository's social preview card.

## 0.6.0 (2026-11-07)

- **Design review before building**, adapted from Google's [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model) (Apache 2.0): the Worker, with full context, writes each phase plan as a design doc; fresh `design-reviewer` agents that never see its reasoning review it before anything is built.
  - **New agent `design-reviewer`** with five lenses: `zoom-out` (simplicity, YAGNI, reuse found by searching the repo), `comprehension` (a naive reader who must paraphrase the plan), `critic` (failure modes, fail-safe, security, cost), `readiness` (no design decision left to the builder, a file boundary, a test plan) and `drift` (the system doc against the code). Licence in `licenses/EGM-LICENSE.txt`.
  - **Phase plan = design doc** with fixed sections: goal, context, design, alternatives, risks and fail-safe, decisions, file boundary, tasks, test plan (HANDOFF "Phase workflow").
  - **No waiting on the user:** the Worker resolves findings by changing the plan or by a ruling; only lenses with findings re-run; after `design_review.rounds` (default 2) open items become rulings, except a Blocking that crosses a hard limit or fails unsafe. Each round is pushed to the ledger.
- **Gate checks (Reviewer routine and `delivery-reviewer`):** the file boundary (an unruled file outside it is a Should-fix; delivery files and lockfiles are exempt), design conformance, the system doc updated when the system's shape changed, and the design review recorded. Phases planned before this version are exempt. The Fixer keeps to the boundary.
- **Living system doc and drift:** `templates/docs/SYSTEM.md` (`paths.system`); the weekly security sweep adds a `## Drift` section, and the Worker routes it like security findings.
- **Commands:** `init` writes `SYSTEM.md`, copies `design-reviewer` and its licence, and adds `paths.system` and `design_review` to the config; `loop` runs the design review in round 0 for new work; `doctor` checks both.
- **Playbook:** principle 10, the design-reviewer role, the phase flowchart, and a new section 5a; `profiles.md` says what each lens looks for per profile.
- **README:** the design review, credits, and Azure DevOps in the requirements.

## 0.5.0 (2026-11-06)

- **Azure DevOps as a code host**, beside GitHub (`"host": "github" | "ado"` in the config, plus an `ado` block).
  - **Host-operations docs:** `templates/docs/HOST-github.md` and `templates/docs/HOST-ado.md`, copied to `docs/delivery/HOST.md` at init. The routine prompts now say *what* to do and point at the host doc for *how* (clone, PR list, marker comments, labels, sha-pinned merge, firing the next routine, reports, dependency alerts), so there is still one copy of each prompt.
  - **Azure DevOps plumbing:** routines with `sources: []` that clone with `$ADO_PAT`; service hooks (`git.pullrequest.created`, `.updated` PushNotification, `.merged`) call the routine fire endpoint; the Reviewer fires the Fixer itself (label changes emit no Azure DevOps event); the PR is completed with `lastMergeSourceCommit` pinned to the reviewed sha; reports go to a reports branch; dependency alerts come from the package manager's audit.
  - **Owner script** `templates/owner/ado-service-hooks.sh`: creates the service-hook subscriptions with the routine fire tokens read through hidden prompts.
  - **cloud-setup.md:** an "Azure DevOps host" section (what changes, fire endpoint facts, setup checklist, hook filters, the bootstrap block every routine needs).
  - **init, doctor, status:** detect the host from the remote, write HOST.md, check service hooks and probation, read reports from the host; init also removes connectors the server attached that the routines don't need.
- **Playbook:** six lessons (labels fire nothing on Azure DevOps; a plain clone works where the docs say GitHub only; the fire body carries no PR context; one PAT identity; no source-branch hook filter; silent hook probation).
- **Example:** `examples/ado-cloud.config.json`.

## 0.4.5 (2026-10-29)

- **Reviewer template:** merge through the REST endpoint pinned to the reviewed sha, after stating that the merge carries out the posted PASS. If the merge is blocked, post `<PFX>-MERGE-PENDING` and send a push notification, never retry another way.
- **Worker template:** a MERGE PENDING watchdog check flags a PASS left unmerged and notifies the owner. It never merges.
- **Playbook:** one lesson (a permission check blocked the gate's merge after its own PASS).

## 0.4.4 (2026-10-28)

- **Worker and HANDOFF templates:** restart safety. Push before every long step, put review findings in the committed ledger as soon as a review returns, and follow a fixed recovery order after a container restart.
- **Playbook:** two lessons (container restarts that lost work; a routine API call made from the wrong account looks like the routine is gone).

## 0.4.3 (2026-10-28)

- **Fixer template:** answers the union of every FAIL review on the current head, not only the latest, and lists the review ids it answered.
- **Reviewer template:** a claim step (`<PFX>-REVIEW-CLAIM <sha>`, expires after 30 minutes) that stops a duplicate run before it reviews. The step-7 guard still stops a duplicate post.
- **Worker and HANDOFF templates:** one ledger commit per task close-out.
- **cloud-setup.md:** always `get` and edit the live routine prompt; never rebuild it from an older copy.
- **Playbook:** two lessons (duplicate reviews reaching the Fixer; a stale-copy update reverting another session's changes).

## 0.4.2 (2026-10-27)

- **Reviewer template:** a duplicate guard. Before posting, it re-checks for a review of the same sha and for a moved head, so two webhook events on one PR produce one review.
- **Fresh sessions everywhere:**
  - `cloud-setup.md` now sets `persist_session: false` for the Worker too, with the reason;
  - the Worker and HANDOFF templates push the ledger at least every 30 minutes, with the exact next step.
- **Usage-inspector template:** a Worker fresh-run health check (tick time, resume gaps, lost work, ledger cadence, merged branches left behind) and duplicate-review detection, replacing the session-size check.
- **Playbook:** two lessons (a persistent Worker blocking cleanup; duplicate reviews from two webhook events).

## 0.4.1 (2026-10-27)

- **Roadmap template:** a production-readiness phase (capacity plan, encrypted backups with a restore test, a production-watch routine, a dependency batch) and a rehearsal row, both before the go-live gate.
- **Playbook:** the guidance and a lesson for this; the rehearsal text now keeps the data copy until the final restore.

## 0.4.0 (2026-10-27)

- **Owner steps made one-time and early:** `templates/owner/place-real-data.sh` (hidden decryption prompt, a single dump uploaded root-only) and `templates/owner/stage-production-secrets.sh` (hidden prompts into a root-only file).
- **Staging gate:** `rehearsal-down` keeps the real-data copy for the final restore (`shred` destroys it).
- **Worker template:**
  - a fresh session per tick;
  - nits from the last PASS are carried into the next phase;
  - a rehearsal runs only when its own roadmap row is next.
- **Reviewer template:**
  - e2e on every PASS when the whole PR touches the UI;
  - operator CLIs must load from the built image;
  - nits listed precisely.
- **Playbook:** five new lessons, and the gates guidance updated.

## 0.3.0 (2026-10-27)

- **Staging kit: configuration without an operator.**
  - New gate verbs `config-show`, `gen-secret` (generate-once, never printed), `set-config` / `unset-config` (allow-listed, typed and range-checked), `apply-config`, `run-cli` (allow-listed app CLIs in a throwaway container) and `prune-images`.
  - Two env files: `config.env` for the app and a CLI-only `cli.env`.
  - `prune-images.sh` removes only this project's images.
  - The ops service and client support the new verbs.
- **The "Pending installs" convention** for server-file changes that only an operator may install.
- **Playbook:** five new lessons (operator dependency, CLI-only secrets, disk growth on shared hosts, CLIs missing from images, pending installs).

## 0.2.0 (2026-10-26)

- **New agent `researcher`:**
  - `brief` mode: sourced facts before a phase or task;
  - `fact-check` mode: verifies the claims in docs, plans and PRs;
  - every claim carries a URL, date and quote, or is marked UNVERIFIED; read-only, and never decides.
- **Wired in:**
  - the Worker runs a research brief at each new phase;
  - the Reviewer and `delivery-reviewer` fact-check docs, research and fact-asserting PRs;
  - `/autodeliver:loop` researches first when a task depends on external facts;
  - the docs and research profiles use the fact-check as proof;
  - `init` and `doctor` include the new agent.

## 0.1.0 (2026-10-26)

First public release.
- **Commands:** `/autodeliver:init`, `/autodeliver:loop`, `/autodeliver:status` and `/autodeliver:doctor`.
- **Agents:** `delivery-reviewer`, `delivery-fixer`, `visual-checker`, `translation-reviewer` and `usage-inspector`.
- **Skill:** `autonomous-delivery`, with the playbook, the profiles (software, docs, data, infra, migration, research), and config and cloud-setup references.
- **Templates:** the five cloud routine prompts (Worker, Reviewer, Fixer, Usage inspector, Security sweep), the charter docs, and the staging ops gate.
- **Token log:** records token usage per role and round. It is on by default in new configs; set `"token_log": false` to turn it off.
- **Community:** issue and PR templates, a Code of Conduct, the CI validate workflow, and the plugin icon.
- **Docs:** GitHub trigger filters, the supported events, and dropped-event limits (cloud setup and lessons).
