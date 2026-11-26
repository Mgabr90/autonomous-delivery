# {{PROJECT}}: handoff (read first)

Every session reads this file before doing anything else. It is the charter: what we're doing, how we work, and what must never happen.

## Goal

{{GOAL}}

## Where things live

- Config: `.autodeliver/config.json` (mode, profiles, proof commands, gates).
- Roadmap: `{{ROADMAP}}` (phases, dependencies, done-when). Gate rows are marked **GATE**.
- Phase plans: `{{PLANS}}`. Ledgers: `{{LEDGERS}}<phase>.md` (tasks done, rulings, evidence).
- Decisions: `{{DECISIONS}}`. Evidence: `{{EVIDENCE}}<phase>/`.
- System (living doc, what is built now): `{{SYSTEM}}`.

## Autonomy charter

- **Decide on your own.** Don't stop to ask. Log every ruling in the ledger as `R<n> — decision — why — cost if wrong`, and index product, data or scope rulings in `{{DECISIONS}}`. A ruling that adds a guard (a check, a limit, a refusal) also names its test and its mutant (the guard dropped or inverted, which that test must fail on), and adds both to the plan's test plan.
- **Quality first.** Never trade proof, review depth or verification for tokens.
- Commit and push the ledger after every task, and at least every 30 minutes, with the exact next step written down. Each Worker tick is a fresh session that resumes only from what is pushed. A local session can end at a usage limit at any moment, so it keeps the ledger's "Resume here" current at each milestone (design-review round, builder hand-over and return, gate round), not only when the limit is near. Write each task's close-out (review result plus 'task N complete; next') as ONE commit.
- **Restart safety.** The cloud container can restart at any time and kill running subagents, and a session that ends keeps only what was pushed.
  - Commit each finished step, and push before every long step: the full e2e, the full test suite, or a staging ship. While no phase PR is open, a push fires nothing. Once the PR is open, keep to one push per fix round.
  - Save each review report verbatim, nits and notes included, in the round it arrives: one file per report in `{{LEDGERS}}<phase>-reviews/`, named after the review and its round, committed as soon as the review returns and never only in a git-ignored workspace. The ledger holds the findings by id and the rulings, and links the files. A report posted as a PR comment is already saved.
  - After a restart, or after stopping any agent that edits files before it reports (a builder, a fixer, a reviewer that plants mutants), in order:
    1. Run `git status` and `git log origin/<branch>..HEAD`, and push any stranded commits.
    2. Check uncommitted edits (`git diff`) before keeping them. Undo only what a stopped agent left (a planted mutant, a half-made edit), hunk by hunk, never by a whole-file or whole-tree checkout over your own uncommitted work.
    3. Restart local services such as the test database.
    4. Restore files that a cut-off run regenerated or mutated: compare the work files' hashes with those saved before the run, so no mutation is left in place.
    5. Re-run the interrupted step in full.
    6. Record the incident in the ledger.
- **Agents.** Apart from the design-review lenses (and, in local mode, the parallel builds that `/autodeliver:loop` describes), run one build or fix agent at a time; when several units of work wait, the one closest to done goes first. Only the main session starts runs on shared infrastructure (remote runners, servers shared with live systems): a sub-agent hands over a hash manifest and is given no route to start them.

## No dependency on the user

Sessions resolve everything themselves. The user acts only at the hard-limit gates below.

- **Visual checks:**
  - take Playwright screenshots of every touched page or rendered output, in each locale ({{LOCALES}}), at desktop and mobile widths;
  - assert layout facts in code;
  - have the `visual-checker` agent review them;
  - commit the evidence under `{{EVIDENCE}}<phase>/`.

  A FAIL is a defect: fix it.
- **Session-written translations:** a `translation-reviewer` agent pass, with the fixes made. People-facing texts ("Phase workflow" step 1, "Decisions") get it in every locale before the design review closes; other strings get it in the build.
- **Product and policy questions:** a ruling with its cost if wrong, citing a `researcher` brief when it depends on external facts (laws, platform rules, vendor terms). Prefer the safest reversible option, made configurable where that is cheap.
- **Owner-only facts** (legal name, address, hosting): derive them from the repo, docs, config and public sources (a `researcher` brief, with sources), or use wording that is true without them. Never ship `TODO(user)`.
- **Stalls, caps and blockers:** the Worker takes the work over (systematic-debugging, re-plan, or split it), never the user.
- `{{DECISIONS}}` has "Open items (sessions resolve)", "Resolved by sessions" and "Hard-limit gates". Only the last is for the user.

## Hard-limit gates (the only user actions)

{{GATES_LIST}}

Prepare each gate fully so that it is a single action: gather the evidence, rehearse the runbook, and write one notice line under "Hard-limit gates".

**Make the owner's part one-time and early.** Give the owner the scripts in `templates/owner/`:
- real data is placed once and kept root-only until a verified final restore;
- owner-only credentials are staged in a root-only file through hidden prompts.

Then the remaining owner action is just the go-ahead in chat.

## Hard limits (never crossed)

{{HARD_LIMITS_LIST}}

A limit over files ("no X in any file") covers every file the project writes: live files, backups, scratch files, plans, ledgers and logs. A copy that must keep X, such as a pinned original, is named as an exception in the limit itself, and the proof scans exactly that set.

## Phase workflow (fixed order)

1. **Research, then plan.** Get a sourced brief from the `researcher` agent into `{{PLANS}}<phase>-research.md`. Then write the phase plan in `{{PLANS}}<phase>-plan.md`. Before the first design-review round, measure every signal the design assumes on the real inputs. When a feature's existence depends on a quality that can be measured (recognition accuracy, speed, how a platform behaves), run a short throwaway spike for it, put the numbers in the plan, and drop or redesign the feature if they don't hold. The plan is a design document as well as a task list, with these sections:
   - **Goal and why:** the roadmap row, the problem it solves, and what done looks like.
   - **Context:** the parts of `{{SYSTEM}}` this phase touches, and links to the research brief and the rulings it relies on. If `{{SYSTEM}}` is still the empty template, the plan's first task fills it from the code as it stands. When this phase applies a change another plan asked for, quote that plan's current text verbatim, with its path and section: the requesting plan's text wins over any paraphrase, summary or older version.
   - **Design:** components, interfaces and data flow, at that level only.
   - **Alternatives considered:** each with the reason it was rejected.
   - **Risks and fail-safe:** failure modes, absent services, security and privacy, rollback.
     - For each guard on an irreversible or privacy-relevant act, list every term of its condition with what can change between the check and the act, and what re-checks it right before the act (or why nothing can change).
     - Word each accepted residual (a gap the plan knowingly leaves open) by its precondition in the real world, for example "a record already open before the watcher started", never by one example sequence. Tests and oracles allow exactly that precondition and nothing wider.
     - Keep rate limits, lockout counters and audit de-duplication, which are security state, in their own store with expiry bound to their window, never in a cache that evicts entries or applies a default timeout: a flood or an idle gap would reset them silently. A multi-step counter sequence that must stay consistent runs in one transaction.
     - A phase that adds or changes authentication, authorization, rate limits, lockouts, audit records or secrets says here that it is **security-heavy**: the gate then budgets a mutation sweep into every round ("Review gate").
   - **Decisions:** every choice a builder would otherwise have to make (schemas, API shapes, file locations, dependencies, error handling, edge cases, and, when the work reads data inputs, the data contract: the inputs read, their shape, the point at which they freeze, and where outputs go, never into an input folder), each as a ruling with its cost if wrong.
     - For each rule about an action (who may do it, what blocks it, what must come before or after it), one **ways-in table**, stated once: a row for every way into the action (page, API, command line, timer, hardware key, file, intent or deep link from another app) with what the rule does there. Other sections point to the table.
     - **People-facing texts** (consent, notice and warning texts, and texts that make people a promise or ask them to agree), word for word in every locale.
   - **File boundary:** the exact repository-relative paths to create, change or delete. Use globs only for generated output. The delivery files listed under "Where things live", lockfiles and the evidence folder are exempt and need no listing.
   - **Tasks:** each with steps and a done-when. Mark each platform fact nobody has measured as `unmeasured`, here and where the design relies on it; measuring those facts is the first task, before any task that depends on them, and a result that contradicts the plan stops the build until a ruling changes the plan. Include the end-of-phase steps below and the `{{SYSTEM}}` update when the phase changes the system's shape.
   - **Test plan:** named cases, happy path and edge cases (for non-software profiles, the profile's checks). Also:
     - **Data path.** When an output must reflect facts that people add to a source (notes, records, documents), trace the
       path from that source to the output section before changing any limit or prompt. The dry run plants a known fact
       in the source and finds it in the output.
     - **Third-party deep links.** A link that relies on undocumented search or filter behaviour in another product's UI
       is clicked in the dry run of any change to that output. Prefer stable one-item URLs.
     - **Data sent to an outside service.** When a change widens what goes to an outside service (an AI model, an API),
       add a test that plants personal data and credentials in each new field and asserts they are stripped.
     - **Numbers already sent.** When a figure must match numbers already sent to people, recover the exact query or
       script and its window first (from the repo or the session that sent them). That query is the spec, and the sent
       counts are the test oracle.
     - **Data coverage per tenant.** Before a figure is compared with an outside number or shown for every tenant, read
       the store's coverage (first and last date per tenant) and, per tenant, the distinct values and fill rate of each
       field it reads. Older rows of a newly added field need a backfill; the figure is not shown for a tenant whose
       values do not fit.
     - **Live system with no staging copy.** For a change to a live system with no staging copy, the dry-run cases and
       the live-vs-source check (see step 5).
     - A test that pins a formula or an ordering rule has a case for each term alone, for the tie-break and for each filter, so that changing any one of them fails a test. A sort that is not stable also gets a case whose expected order flips, not only reversed input.
     - A test that pins a guard condition has a case for each of its terms, written in the same task as the guard, so that dropping or inverting any one term fails a test. Every guard on an irreversible act (delete, send, overwrite, publish) or a privacy-relevant one gets this matrix: the gate's mutation sweep then confirms it rather than discovering it.
     - **Call-site arguments.** For a guarded pure function, each argument its caller computes (a window start, a
       filtered set, a flag) has at least one integration-level test through the caller that fails when the argument
       is swapped for a plausible wrong value (another anchor time, a narrower or wider set).
     - A privacy or safety guard over a state machine whose input events can be lost, reordered or never seen gets a seeded, model-based test with the guard's first version, not after the gate finds leaks. The test generates event sequences, simulates the real-world state with its own oracle (independent of the code under test) and asserts the invariant, for example "no output reveals X", on every sequence except the accepted residuals named in the plan. Hand-written cases alone miss other members of the same leak class.
     - An "at most N per window" rule (a rate limit, a lockout, a de-duplication) has a case that drives the worst-case shape, many keys each retried enough to cross each threshold, not only the literal flood. A cap or bound also has a case showing that the record it must still produce is produced: a cap can suppress the very record it was meant to limit.
     - A multi-step counter sequence that must stay consistent has a test that drives it from real concurrent threads, each with its own connection. Nesting the steps on one thread runs the inner transactions as savepoints and proves nothing about two writers.
     - A performance or time-budget measurement records machine-wide CPU with each sample, and the plan sets the other-process load above which a scenario's run is invalid. On a shared machine it runs in a quiet slot, with no other heavy work running (in local mode, `/autodeliver:loop` "Quiet slot for measurements").
     - A document section that other files or outputs point to (a heading named by a link, a prompt or a test) gets a test that pins its heading and key line.
     - When the phase writes documents that say what the product does (what it records, keeps, sends, deletes or protects), the plan states that behaviour once, as one numbered fact block in a file it names, and every other document points to fact ids instead of restating them. A claims table ties each fact id to the code that does it, and a test checks that the fact ids in the documents match the table. Each restatement is one more paraphrase that can drift from the code.
     - Each people-facing sentence that says what the product does or promises has a behaviour test that fails when the product stops doing it; a sentence that points to a fact id is covered by that fact's test. A test that pins only the wording can pin a false sentence.
     - A test on a file that later phases also edit (service units, install scripts, server config) asserts the lines it owns, never a span that runs to the end of the file.
2. **Design review (goldfish), before any building.** Dispatch the `design-reviewer` agent once per lens, in parallel: `zoom-out`, `comprehension`, `critic` and `readiness` (or the lenses set in `design_review.lenses` in `.autodeliver/config.json`).
   - **Isolation is the point.** Each brief contains only the lens, the plan path, the research brief path, the paths of this file, the roadmap and `{{SYSTEM}}`, and the round number. Never send a summary of your reasoning, the alternatives you liked, or why you think the plan is right.
   - Resolve every Blocking and Should-fix finding yourself: change the plan, or write a ruling with its cost if wrong. Re-dispatch only the lenses that had findings, with their previous findings. After each change to the plan, re-read every people-facing sentence that depends on what changed, and correct the ones it made false.
   - **Cut before a third patch.** When the same feature or rule gets a Blocking in two rounds in a row, don't patch it a third time. If the plan may decide, cut it: a ruling with its cost if wrong, and a roadmap row for what was cut. If the owner asked for it, put the cut to the owner; in an unattended run, move it to its own roadmap row, index the ruling in `{{DECISIONS}}`, name it in the end-of-run report, and go on without it. If the phase has no goal without it, re-plan that part from its root cause. Never cut a guard that something you keep still needs.
   - **People-facing texts:** before the review closes, the `translation-reviewer` agent passes each one in every locale, the source included, with the plan path in its brief; run it again on each text changed since. Never leave this to the build.
   - Stop after `design_review.rounds` rounds (default 2). Anything still open becomes a ruling with its cost if wrong, and building starts. The design review never waits for the user.
   - **Close the review before any build starts:** every round has run, its plan changes and rulings are written into the plan, and the people-facing texts have passed. Never start building while a round is open, and never send plan amendments to a builder that is already running.
   - **Except:** an open Blocking that crosses a hard limit or makes the design fail unsafe can't be accepted by ruling. Change the plan or split the phase, even past the round cap.
   - Record each round in the ledger as ONE commit, pushed as soon as the lenses return: each lens's verdict and findings, what changed in the plan, and the rulings made, with each lens's report saved verbatim ("Restart safety").
3. **Each task:**
   - test-first or check-first work;
   - guard skills if available (clean-code, test, docs);
   - a per-task review;
   - a commit with its ledger line, made only when the proof's own exit code is 0. Run each proof command on its own, never through a pipe: with `| tail` the shell reports `tail`'s exit code, not the proof's;
   - a product gap found while writing about the product (the code does not do what the document would say) goes to the roadmap as a product item the moment it is found, with a ruling. The document lists it in its gap list, and the gate notice line names it, so no document promises the fix.

   **Values the plan pins are recomputed first.** When the plan states expected values that come from data (counts, groupings, totals), compute them from the data before building. On any disagreement, stop: write both values in the ledger, settle the rule by a ruling, then build.

   **A check covers the rule, not one instance of it.** This holds for every new or changed check, and for every check the Fixer writes for a finding:
   - it covers the rule or finding as written: each value, view, layout (width), entry route and input method it names or implies. List them in the ledger and map each one to an assertion;
   - it finds the members of a class from the output itself (every link on the page, every view, every file in the named set), with a minimum count, never from a fixed list, so new members are covered;
   - it exercises behaviour, not presence: open the control, read what it shows, return focus. Reach each state by every path the work offers (for a page: resize, hash change, its own back link, the browser's Back), and assert side effects such as a history push or replace;
   - it is shown red by one mutation per distinct way the rule can break (another value, view, entry route, width or input method), not one mutation per finding.

   **Expected values come from the source** data or a hand-written table, never from the artefact or field under test.

   **A new view gets its checks first.** A new view of rendered output (a page, a state, a dialog) is not built until the fit, contrast and text checks cover it at every width, with every state open; for other profiles, until the profile's checks cover it.

   **Inputs are frozen; outputs live elsewhere.** No output (a deliverable, a generated or work copy, a run result) is written into an input folder, meaning the frozen data the proof reads as given. Inputs are fingerprinted before the build, and a later change to one is a declared change: a ruling, a rebuild and a re-recorded fingerprint.

   **Proof runs.**
   - Run one proof or mutation run at a time, never two at once. Checks inside one run may run in parallel, each in its own process with a time limit; a timeout, a crash, a runner error or a missing completeness line (checks expected against checks run) reads as FAIL.
   - **Probe first:** the new and changed checks (a run of about a minute that the builder can start and read itself), then the full proof, then the mutation chain. A change to a proof file restarts from the probe. After a fix, run the mutations whose checks or anchors the change touches; the full mutation chain runs once, before the gate.
   - **A result counts only for the file state it ran on:** name its hash manifest in the result file. A run started before an edit is void.
   - Save the hashes of the work files before a mutation run and compare them after it, so no mutation is left in place. Re-run alone any mutation that stayed green in a batch.
4. **End of phase:**
   - ONE simplify pass over the whole phase diff (its own `refactor(simplify)` commit), limited to files the phase already changed. When it moves a per-key guarantee from a query into an in-memory lookup, it adds a test with an item whose own key differs from the key it is looked up for;
   - then the full proof: `{{PROOF_FULL}}`, each command as its own step after the previous one has finished (never chained in one shell command, never beside another heavy process). Record any heap or memory flag a step needed;
   - **claims check**, when the phase's documents say what the product does: first the **claims sweep**, where the builder greps those documents for the whole words `never`, `only`, `all`, `no`, `not recorded` and `deleted` (`grep -niwE 'never|only|all|no|not recorded|deleted' <file>`), checks each hit against the code, fixes the false ones, and commits the list of hits with the code that backs each to `{{EVIDENCE}}<phase>/claims-sweep.md`. Then a fresh strong-tier subagent that did not write the documents checks each fact in the fact block against the code, and its result is committed in the same folder;
   - the final whole-phase review.

   Each step above uses the matching skill from "Skills" below when it is available.
5. **Staging** (if the project has it): ship; run the phase checks; then run the **log scan**, where any error the phase caused is a Should-fix. Record the results.
   **No staging, live system** (an admin console, a hosted editor, an API write to production): before go-live, a **dry run** with a switch that turns every write into "would do X", on the platform's own runner, with real inputs covering each path the change touches (check whether the runner executes the saved version or the open buffer; if a path can't be dry-run, name the first real event that will prove it). After deploy, keep the pre-change copy, read the deployed version back, compare it with the reviewed source ignoring whitespace, and confirm the switch is off and test output removed. Record both in the evidence.
6. **Evidence and write-up:**
   - commit the evidence;
   - update the roadmap;
   - open the PR (cloud) or run `/autodeliver:loop` (local).

## Models

- **The strong tier is the floor.** Building, reviewing, fixing and security work is never handed to a model below the strong tier: `models.strong` in the config, or Opus when it is not set (what the review and fix agents run on).
- **A planning-tier model plans; it does not build.** A local session is on a planning-tier model when its own model id contains one of the names in `models.plan` (default: `fable`, `mythos`). It keeps that model for understanding the task, research, the plan and its decisions, resolving the design review, rulings, dispatching agents and checking what they return. It may write the plan, the ledger and notes, and make a one-line fix that is needed to hand work over. It hands the build, the simplify pass and every fix to strong-tier subagents, and never finishes the build itself. `/autodeliver:loop` has the steps: the brief, the checks on return and the retry limit. When it hands several phases to builders at once (local mode only), `/autodeliver:loop` "Parallel builds" has the rules: a worktree per builder (the worktree folder git-ignored, explicit paths staged), shared helpers first, a roster for direct messages between builders, and the requesting plan's text copied verbatim for cross-plan requests.
- **Cloud routines keep their tiers:** Worker, Reviewer, Fixer and security sweep on the strong model. Don't set a routine to a planning-tier model.
- A session on the strong tier, or on a lower model the user chose, works as before.

## Skills (use them when available)

Skills make the steps above more reliable. They never replace the rules in this file: when a skill and this file disagree, this file wins. A skill is available when the Skill tool lists it. In cloud sessions that means `.claude/skills/<name>/` is committed, because plugins don't load there; a skill's reference to `superpowers:<name>` then means the bare `<name>`. Locally, the plugin names work too.

- **Where a skill says to ask, wait for, discuss with or get permission from "your human partner"**, write a ledger ruling with its cost if wrong, and continue.
- **The design review (step 2) replaces any human plan review a skill asks for.**
- **Report the way the routine prompt says, not the way a skill says.** That means marker comments on the PR and lines in the ledger, never review-thread replies.
- **Severity:** a skill's Critical, Important and Minor map to Blocking, Should-fix and Nit. Minor items go into the ledger, never just "for later".

| Step | Skill | Without it |
|---|---|---|
| Write the phase plan | `writing-plans`, with three changes: save the plan to `{{PLANS}}<phase>-plan.md` with every section of step 1; leave out its "REQUIRED SUB-SKILL" header line; and **skip its Execution Handoff**, so you don't ask for a plan review and don't start `subagent-driven-development` or `executing-plans`. Go on to step 2 (design review), then step 3 | the sections in step 1 |
| Each task | `test-driven-development` | test-first by hand |
| Per-task review | `requesting-code-review` | a review subagent with a narrow brief |
| Simplify pass | Claude Code's `/simplify origin/{{MAIN}}...HEAD` (four cleanup reviewers, then the fixes; always pass the range, because the default diff can be empty on a pushed branch), committed as one `refactor(simplify)`, limited to files the phase already changed | review the diff yourself for reuse, simplification, efficiency and altitude |
| Before any "done", "green" or PR | `verification-before-completion` | run the proof, each command on its own and never through a pipe, and quote its output and exit code before claiming anything |
| Answering review findings (Fixer) | `receiving-code-review`, then `test-driven-development` | verify each finding, then fix it test-first |
| Stuck PR, repeated finding, failing proof | `systematic-debugging` | root cause before any fix |

**Never, in any run:**
- `subagent-driven-development` and `executing-plans`: they replace the playbook's build with their own. They keep their own uncommitted ledger, run their own reviews, and skip the design review;
- `finishing-a-development-branch` and `using-git-worktrees`: they merge or move the work outside the gate, and they stop to ask.

**Only with a person present:** `brainstorming` has a hard gate that needs the user's approval, and `using-superpowers` sends you to brainstorming first. Use them at `/autodeliver:init`, where the owner is present, never for phase work. If the superpowers session hook loads them in a local session, still don't use them for autodeliver work.

**Only in the security sweep:** `security-audit` (Cloudflare's audit skill, if the project has it in `.claude/skills/`). The sweep's own prompt says how it runs. Phase work never runs it, in either of its modes: not the Worker, not the Fixer, not the local loop. A full audit there would multiply cost and write run files in the middle of a phase.

The Reviewer uses none of these skills, and not `security-audit` either: the gate keeps its own fixed rules.

## Review gate

- The gate classifies findings as Blocking, Should-fix or Nit.
- **PASS = zero Blocking, zero Should-fix, full proof green, no flaky failures.**
- The gate runs each proof command as its own step after the previous one has finished (never chained in one shell command, never beside another heavy process), and records any heap or memory flag a step needed.
- These are Should-fix:
  - a flaky test;
  - missing fail-safe handling of an absent service;
  - a missing translation;
  - a `TODO(user)`;
  - a parked item;
  - an undelivered plan item;
  - a missing design-review record in the ledger;
  - a file changed outside the plan's file boundary with no ruling that extends it (delivery files, lockfiles and the evidence folder are exempt);
  - an implementation that departs from the plan's design or decisions with no ruling recording the change;
  - a change to the system's shape (components, interfaces, data, outside services) without the matching `{{SYSTEM}}` update;
  - a fixed finding with a part (a value, view, layout, entry route or input method it names) that no check asserts ("Phase workflow" step 3);
  - a change deployed to a live system with no staging copy whose evidence lacks the dry-run outputs or the live-vs-source result;
  - a deliverable derived from the reviewed work (an export, workbook, bundle or merged copy) that differs from it: the gate reviews every derived deliverable;
  - an argument a caller computes for a guarded pure function that can be swapped for a plausible wrong value with no test failing (the gate mutates call-site arguments, not only the function body);
  - a per-key guarantee moved from a query into an in-memory lookup without a test with an item whose own key differs from the key it is looked up for.
- **A broken proof is Blocking:** a check that crashed or timed out, or counts that don't add up (checks run against checks expected; mutations caught, survived and retired against those planted).
- **Report a test gap in full.** When a test pins a formula, an ordering rule or a guard condition, the gate checks the whole matrix from step 1's test plan in the first round that sees the rule and lists every case no test catches, never one per round. A guard on an irreversible or privacy-relevant act always gets a mutation sweep: one mutant per term, dropped or inverted, each of which must fail a test, run in a throwaway copy, never in the work under review.
- **Prove the oracle.** For a model-based test from step 1's test plan, the gate plants known leaks as mutants in the same throwaway copy and shows the test fails on each. A planted leak that the oracle files as an accepted residual the ruling does not cover is a Should-fix. A finding in a test or its oracle names its closing check: a planted case that must fail once the fix is in, not only the edit.
- **Diff the documents.** In every round, the gate diffs each changed document against its version on the base branch (the last version that passed the gate). A section removed or rewritten that no task or finding asked for is a Should-fix.
- **Sweep the claims.** When the gate finds one sentence about what the product does that the code does not back, it runs the claims sweep from step 4 over every changed document and reports every false sentence together, never one per round. A test that bans false claims by regex is only a smoke check: a gap in its pattern's breadth is a Nit, while a false sentence the pattern missed stays a Should-fix.
- **Remove, don't rewrite a third time.** When a sentence that a fix round added (it is not in the base-branch version) fails review a second time, the fixer removes it rather than rewriting it again. If a finding or a plan task needs its content, the fixer replaces it with a pointer to the fact id that states it. The fixer re-runs the claims sweep on the document lines it changed.
- **Re-read the promises after each fix.** A fix that changes behaviour can make a sentence elsewhere false. After each fix, the fixer re-reads every people-facing sentence (interface, notices and documents, in every locale) that depends on what changed, and corrects it or reports it; in later rounds the gate re-reads the same sentences, changed or not, and a false one is a Should-fix.
- **Limits and counters.** Rate limits, lockout counters or audit de-duplication kept in a cache that evicts entries or applies a default timeout; a multi-step counter sequence outside one transaction, or with no test from real concurrent threads; an "at most N per window" rule with no worst-case-shape test; a cap with no test of the record it must still produce: each is a Should-fix (Blocking when it is shown to let a limit be crossed). A fix that adds a cap or bound tests both the bound and that record.
- **Security-heavy phases get a sweep every round.** For a phase that step 1 marks security-heavy, every round, round 1 included, runs a mutation sweep over the phase's security code (each guard, bound and counter check), not only over the delta, with each mutant run against the whole test files that cover that code, and reports every survivor together. On a shared machine it follows the heavy-work rule below.
- **Measurements count only from quiet samples.** A performance or budget result counts only from samples whose recorded other-process load stayed under the plan's threshold. The gate never runs mutants or other heavy work while a measurement runs.
- **Heavy work on a shared machine** (a local run: mutation sweeps, full proofs): one process at a time, at below-normal priority (`nice` on POSIX, the below-normal priority class on Windows), never several in parallel. A sweep keeps one spec file per mutant and saves each result as it finishes, both in the throwaway copy, so a run killed for lack of memory resumes from the next spec instead of starting over.
- Accepted decisions (cite them) and later-phase items (cite the roadmap row) are not findings.
- **The boundary grows by ruling, not by accident.** When a task needs a file outside the boundary, add it with a ruling in the ledger (why, and the cost if wrong) before changing it. The simplify pass stays within files the phase already changed.
- **Fail safe:** never treat an unsent notice as sent, and never take an irreversible step that relies on a call that didn't happen. An upload or send that returns an empty success is verified at the destination (list it, read it back, count it) before it is reported done.

## Security sweep intake

At the start of each phase, and whenever a new `{{PFX}}-SECURITY` report or `{{PFX}}-SECURITY-NOTE` lands:
- route every confirmed finding into the current phase (if it touches its area) or into the roadmap follow-ups, with a ruling;
- route each item in the report's `## Drift` section the same way: fix the code, or correct `{{SYSTEM}}` with a ruling saying the doc was stale;
- never drop one.

## Environment

- **Staging settings and secrets:** use the gate verbs (`config-show`, `gen-secret`, `set-config`, `apply-config`, `run-cli`). Don't wait for an operator.
- **Server file changes** (gate, deploy script, compose): list them under "Pending installs" in the staging README. The operator installs them.

{{ENVIRONMENT_NOTES}}
