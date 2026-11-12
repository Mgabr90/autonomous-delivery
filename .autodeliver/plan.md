# Plan: use Cloudflare's `security-audit` skill in the security sweep (autodeliver 0.10.0)

Revision 3 (after design review rounds 1 and 2; the record is in `.autodeliver/loop-log.md`). Branch: `autodeliver-0.10.0-security-audit`. Placeholders are written here as `<NAME>`; in the templates they keep the double-brace form. Paths are under `plugins/autodeliver/` unless they start with "root".

## 1. Goal

The weekly security sweep finds issues with ad-hoc subagents. Cloudflare's `security-audit` skill (github.com/cloudflare/security-audit-skill, MIT) gives the same job a tested method: a coverage ledger, isolated hunters, a fresh verifier per candidate, and records checked by two validators. Use it in the sweep when a project has it, keep the sweep working without it, and stop it from doing anything the playbook forbids.

Out of scope: bundling the skill's files in this repo; any use of the skill by the Worker, Fixer, Reviewer or local loop; a local-mode sweep command; keeping the skill's ledgers between cloud runs; new config fields or placeholders.

## 2. How the sweep works today

`skills/autonomous-delivery/templates/routines/5-security-sweep.prompt.md` is a weekly, read-only cloud routine on the whole main branch:

- Header comment line 4 lists its tools and says Write is "only for request bodies and the report file". Line 5 says: "Optional vendored security skills: entry-point-analyzer, semgrep, supply-chain-risk-auditor, a secure-review skill."
- The `**Unattended run:**` line (CI checks its prefix) forbids heredocs and multi-line inline scripts and says "Use Write only for request bodies and report files".
- Step 2 SWEEP runs these bullets "with the available skills and narrow-brief subagents, in parallel": (a) every entry point and its guards; (b) auth, crypto, secrets in logs and responses, injection, uploads, SSRF; (c) semgrep; (d) dependency alerts; (e) the `researcher` agent for each HIGH or CRITICAL advisory; (f) the staging tooling and ops gate; (g) the profile's own risks. Step 2b runs the drift check in parallel.
- Step 3 VERIFY: each finding needs file:line and a concrete scenario; every CRITICAL and HIGH is confirmed on staging (at most 2 or 3 safe requests) and marked `runtime-confirmed`, `runtime-refuted` or `static-only` (say why).
- Step 4 CLASSIFY as CRITICAL, HIGH, MEDIUM or LOW. Step 5 REPORT: one `<PFX>-SECURITY <date>` comment, posted as the host doc (`docs/delivery/HOST.md`) says, with a "what you ran" and a "what you couldn't check" part.

Other places that carry the rules: `templates/docs/HANDOFF.md` section "Skills" (the charter every role reads; when a skill and HANDOFF disagree, HANDOFF wins; its last line says "The Reviewer uses none of these skills"); `templates/routines/2-reviewer.prompt.md` lines 5 and 9 (the Reviewer may use Skill "only for vendored security or review checks"); `references/playbook.md` section 5b (skills) and section 11 (cost controls, the "Weekly security sweep" bullet); `commands/init.md` "Skills" step (offers to copy superpowers skills into `.claude/skills/` with a licence and a version file); `commands/doctor.md` row 16 (checks those copies); `references/cloud-setup.md` (line 45: what the read-only routines may write; "Unattended runs": cloud sessions pre-approve file edits, so Write and Edit never prompt; "Plugins don't load in cloud sessions").

## 3. Facts about the skill

Read at commit `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`: `README.md`, `SKILL.md`, `RECONNAISSANCE.md`, `HUNTING.md`, `VALIDATION-AND-REPORTING.md` and the file tree. Scanned at the same commit, not read in full: the eleven attack-class and domain companion files (hunting checklists that hunters receive as text; a search found no fenced shell block and no prescribed `curl`, `npm`, `pip`, heredoc or inline-script command in them) and the two validators (each loads only Node's `fs`, `path` and `util`; a search found no network, child-process, environment or file-writing call). Not read: `report-schema.json` and the validators' tests.

- One folder, `skills/security-audit/`: `SKILL.md`, 13 companion `.md` files, `report-schema.json`, two zero-dependency Node validators and their tests. The LICENSE is at the upstream repo root, outside that folder. It needs Node.js and an agent with subagents.
- Two modes. Guidance (the default): advice, no files. Full audit: six phases. The coordinating session ("parent") alone writes the run files: `run-metadata.json`, `architecture.md`, `coverage-ledger.json`, `findings.json`, `REPORT.md`, `FINDINGS-DETAIL.md`, `NEEDS-VALIDATION.md`.
- What it makes agents do. Reconnaissance agents read source and return facts; they write nothing. Hunters and verifiers read source and return one JSON object; they write only to a per-agent `scratch/` folder, and only when they run target code. The only shell commands the workflow prescribes are `node <skill-dir>/validate-findings.cjs <file>` and `node <skill-dir>/validate-coverage-ledger.cjs <file>`. None of the files read or scanned prescribes a heredoc or an inline script.
- Target code runs only inside an OS-enforced sandbox (no network, empty environment, read-only target, resource limits), and evidence files leave `scratch/` only through a descriptor-based copy by trusted parent code. Without all of that, nothing runs and the lead is recorded as `needs_validation`. A `confirmed` record requires a bounded local observed result. **So in a session with no such sandbox, almost every real lead ends as `needs_validation`, not `confirmed`.**
- Verdicts: `confirmed` (severity critical, high, medium, low or informational), `needs_validation` (a source trace plus one exact unresolved fact; no severity) and `rejected`.
- Where it asks or stops for a person: "ask one focused question" when the mode is unclear; "stop and request an external path" when the output folder is inside the target without being chosen by the user and ignored by version control; "ask for a larger budget" when a budget cannot fund the minimum run. If the request stays unchanged it records `run_status: "incomplete"` with a reason.
- Output folder: outside the target by default (`~/security-audit-skill/<repo>/run-<N>`); inside the target only when the user explicitly selects it and the parent verifies that version control ignores the whole folder.
- Profiles: `quick` (one hunter wave, one critic pass, one verifier per candidate; must present itself as partial coverage), `standard` (the default; waves repeat until a clean critic pass) and `deep`. A budget is a maximum number of agent calls; the minimum reserve is four reconnaissance calls, one critic and one verifier.
- It never contacts deployed endpoints, never installs dependencies and never changes target source.

## 4. Design

### 4.1 Routine 5: the only place the skill runs

All sweep-specific rules live in routine 5 and nowhere else. HANDOFF and the playbook carry only the cross-role rule (4.2) and a short description.

**Header comment.** Line 4's Write note becomes: "Write only for request bodies, the report file and the `security-audit` run files under `.autodeliver/security-audit/`". Line 5 becomes: "Optional vendored security skills: security-audit (Cloudflare, MIT; step 2 says how it runs), entry-point-analyzer, semgrep, supply-chain-risk-auditor. Dependency alerts enabled on the repo."

"A secure-review skill" leaves the list on purpose: `security-audit` now fills that slot by name.

**Role sentence (line 7).** "Your writes are one report comment, plus throwaway test accounts on STAGING (if the project has staging) for runtime checks." becomes "Your writes are one report comment, the `security-audit` run files in their git-ignored folder (step 2), plus throwaway test accounts on STAGING (if the project has staging) for runtime checks."

**Unattended-run line.** "Use Write only for request bodies and report files" becomes "Use Write only for request bodies, report files and the `security-audit` run files under `.autodeliver/security-audit/` (step 2)". The rest of the line is unchanged, including its `**Unattended run:**` prefix.

**Step 2.** The bullet list stays. A new paragraph before it says how bullets (a) and (b) are covered:

1. *When the skill runs.* Use `security-audit` for bullets (a) and (b) only when all three hold: the Skill tool lists it; `node --version` works; and `git -c core.excludesFile= check-ignore -q .autodeliver/security-audit/` succeeds (the folder is ignored; keep the trailing slash, because without it git answers "not ignored" for a folder that does not exist yet. Checked in a scratch repo on 2026-11-12: exit 0 with the slash and the ignore line, exit 1 without the slash). Otherwise do (a) and (b) with narrow-brief subagents as before, and name the missing condition under "what you ran".
2. *Order.* Start bullets (c) to (g) and the drift check as subagents first, then run the skill in this session, which is the skill's parent. The skill run never gates the other bullets. When the skill runs, do not also run `entry-point-analyzer` for (a) and (b); `semgrep` and `supply-chain-risk-auditor` still serve their own bullets.
3. *Fixed settings, so the skill has nothing to ask:* full audit mode; profile `quick`; budget 40 agent calls; target = the checkout; scope = everything except `.claude/skills/` (vendored skills, so the skill does not audit itself) and `.autodeliver/`, both recorded `out_of_scope`; output folder `.autodeliver/security-audit/run-<YYYY-MM-DD>/`, selected here explicitly and verified ignored in point 1.
4. *Source review only.* A cloud session has no OS-enforced sandbox that meets the skill's controls. Say so at the start of the run: no target code is run, no dependency is installed, and hunters and verifiers write no files; they return their JSON result. All the skill's delegated agents (reconnaissance, hunters, critics, verifiers) are ordinary subagents of this session.
5. *Unattended rule in every brief.* Add this routine's unattended-run rule to every brief the skill has this session send, after the skill's own required text.
6. *Never ask, never wait.* Wherever the skill says to ask, to stop and request, or to wait for the user, decide by these rules, continue, and name the decision under "what you ran". If the budget cannot fund the minimum run, the skill records the run as incomplete: treat it as point 7 says.
7. *How the run ended.* The three cases cover every end state:
   - **Clean:** both validators pass and `run_status` is `complete`. Use the records. A `quick` run with a budget still leaves ledger units `deferred` or `blocked`: cover each of them with one narrow-brief subagent where that is possible, and list the rest by name under "what you couldn't check".
   - **Usable:** anything else where `validate-findings.cjs` passes (`run_status` is `incomplete`, still `in_progress` or missing, or `validate-coverage-ledger.cjs` fails). Use the records in `findings.json`. Make no coverage claim from the ledger. Cover by hand, the same way, each `deferred` or `blocked` unit and each unvalidated candidate the ledger names; if the ledger is invalid, do bullets (a) and (b) by hand for everything the records do not touch. List what is left under "what you couldn't check".
   - **Unusable:** `validate-findings.cjs` fails, you correct the records it names once, and it fails again; or there is no `findings.json`. Use no skill record as a finding. Do bullets (a) and (b) by hand, using the skill's notes only as leads, and say so under "what you ran".
8. *Nothing leaves the folder whole.* The run files are never committed, pushed or posted. They are inputs to the report.

**Step 3 additions** (the existing text stays):

- Skill records are leads that pass through this step like any other finding. A `confirmed` record keeps its severity as the starting point: critical, high, medium and low become CRITICAL, HIGH, MEDIUM and LOW; informational becomes LOW. A `needs_validation` record is a source-grounded lead without a severity: verify its file:line and scenario yourself, and classify it in step 4 by this routine's own scale. A `rejected` record is not reported.
- For every lead rated CRITICAL or HIGH, and for every `needs_validation` lead whose unresolved fact a staging request can settle within the limits above, do the staging check. This is the sweep's own check under HANDOFF, done after the skill has finished; the skill's "no deployed endpoints" rule covers the skill run only. Mark the result `runtime-confirmed` or `runtime-refuted`. A lead that staging cannot settle is `static-only`, with the skill's unresolved fact as the reason. Never drop a lead because the skill gave it no severity. Beyond the CRITICAL and HIGH leads, check at most 10 `needs_validation` leads on staging per sweep, the most serious first; the others are `static-only` with the reason "not checked this week".
- Merge leads with the same root cause from different sources (the skill, semgrep, the by-hand bullets) into one finding.

**Step 5, "what you ran"** names one of: the skill ran (profile, budget used, whether both validators passed, `run_status` and its reason, the coverage counts from the ledger, and that a `quick` run is partial coverage); or the skill did not run, with the cause (not vendored, no Node.js, output folder not ignored).

Steps 1, 2b, 4 and the rest of 5 are unchanged. The report is still ONE `<PFX>-SECURITY` comment, and "confirmed finding" in the Worker prompt and in HANDOFF "Security sweep intake" keeps its meaning (a finding the sweep's report lists), so neither changes.

### 4.2 Cross-role rule (HANDOFF "Skills")

Two edits in `templates/docs/HANDOFF.md`:

- After the "Only with a person present" paragraph, add: "**Only in the security sweep:** `security-audit` (Cloudflare's audit skill, if the project has it in `.claude/skills/`). The sweep's own prompt says how it runs. Phase work never runs it, in either of its modes: not the Worker, not the Fixer, not the local loop. A full audit there would multiply cost and write run files in the middle of a phase."
- The last line becomes: "The Reviewer uses none of these skills, and not `security-audit` either: the gate keeps its own fixed rules."

`templates/routines/2-reviewer.prompt.md`: line 5 "Skill only for vendored security or review checks, never the superpowers or /simplify skills in HANDOFF "Skills"" becomes "Skill only for vendored security or review checks, never `security-audit` and never the superpowers or /simplify skills in HANDOFF "Skills""; line 9 "Use no superpowers skills and no `/simplify`" becomes "Use no superpowers skills, no `/simplify` and no `security-audit`".

No change to the Worker and Fixer prompts, `agents/delivery-fixer.md`, `agents/delivery-reviewer.md` (it names no skills) or `commands/loop.md`: each already points at HANDOFF "Skills" for what is excluded.

### 4.3 `/autodeliver:init`

In the optional "Skills" step, after the superpowers offer, a second offer, **in cloud mode only** (the sweep exists only there):

- Clone `https://github.com/cloudflare/security-audit-skill` into a temporary folder and check out the pinned commit `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` (the version this plugin's sweep rules were written against).
- Copy the whole `skills/security-audit/` folder to `.claude/skills/security-audit/`; copy the repo's `LICENSE` to `.claude/skills/SECURITY-AUDIT-LICENSE.txt` (MIT, Cloudflare); write the commit sha to `.claude/skills/SECURITY-AUDIT-VERSION`.
- If the clone or checkout fails, say so and skip: the sweep falls back to its own steps. Never copy from another source or another commit. Remove the temporary folder afterwards.
- If `.claude/skills/security-audit/` already exists: skip when `SECURITY-AUDIT-VERSION` equals the pinned commit; otherwise offer to replace the whole folder.
- **The live routine comes first.** Make the offer only when routine 5 will carry this version's prompt: either init creates the routines in this same run, or, on a project that already has routines, the live routine 5 prompt already names `.autodeliver/security-audit/`. If it does not, say that routine 5 must be updated first (`references/cloud-setup.md` "Updates"), offer to do that update, and vendor the skill only after it succeeds. An old routine 5 says only "SWEEP with the available skills": with the skill present it would run with none of the fixed settings.
- Say that the sweep's cloud environment needs Node.js, and that the first hand-fired sweep (init's own section 4 "Cloud mode only", step 4, which already exists) is the test that the skill runs without stalling.

The `.gitignore` bullet gains `.autodeliver/security-audit/` (always, so the folder is ignored whenever the skill is added later).

### 4.4 `/autodeliver:doctor` row 16

Append: if `.claude/skills/security-audit/` exists, then:
- ❌ cloud: the live routine 5 prompt does not name `.autodeliver/security-audit/` (the routine predates the skill's rules: update routine 5, or remove the folder until then). This is the one hard failure; the rest are ⚠️ only, since the sweep has a fallback. Doctor only reports; it changes nothing;
- it holds `SKILL.md`, `RECONNAISSANCE.md`, `HUNTING.md`, `VALIDATION-AND-REPORTING.md`, `ATTACK-CLASSES.md`, `report-schema.json`, `validate-findings.cjs` and `validate-coverage-ledger.cjs`, and `SECURITY-AUDIT-LICENSE.txt` is beside it;
- `SECURITY-AUDIT-VERSION` equals the pinned commit above (otherwise ⚠️ "not the version the sweep rules were written for");
- `git -c core.excludesFile= check-ignore -q .autodeliver/security-audit/` succeeds;
- cloud: the latest `<PFX>-SECURITY` report (found as the host doc's section 4 says) is less than 8 days old (otherwise ⚠️ "the sweep may be stalled: read its last run"; "not checked" when there is no report yet);
- (`ATTACK-CLASSES.md` is in the list because the hunting phase copies its blocks into every hunter brief; the other companions are chosen per target);
- Node.js in the cloud environment is "not checked" here.

### 4.5 Reference text

- `references/playbook.md` section 5b: title becomes "Skills: superpowers, /simplify and security-audit". Add one paragraph at the end: what the skill is; that only the security sweep runs it, in a bounded `quick` pass on source only; that its records are leads the sweep verifies, confirms on staging and classifies itself; that `init` copies one pinned commit, and the pin moves only in a plugin release after the skill is re-read against the sweep's rules; what it is expected to add without a sandbox (a coverage ledger that names what was and was not looked at, and a fresh verifier per candidate); and a "Measure it" sentence (compare a few sweeps with and without the skill: findings kept after verification, and tokens, counting the sweep session's own tokens on the first run, since it writes every brief). Section 11, "Weekly security sweep" bullet: add "It uses the `security-audit` skill when the project has it (section 5b)." Section 2 (roles table): no change. Section 10 (lessons): no change, nothing has failed in real use yet.
- `references/cloud-setup.md`: line 45 gains a sentence: "The security sweep also writes the `security-audit` skill's run files, only under the git-ignored `.autodeliver/security-audit/` folder." In "Plugins don't load in cloud sessions", add: "`init` offers `security-audit` for the security sweep the same way; its validators need Node.js in the sweep's environment."
- `skills/autonomous-delivery/SKILL.md` skills paragraph: add one sentence: the security sweep uses Cloudflare's `security-audit` when the project has it; no other role does.
- Root `README.md`: line 80 ("Proven skills") adds Cloudflare's `security-audit` for the weekly sweep, with its link; line 91 (the weekly sweep bullet) is unchanged.
- Root `CHANGELOG.md`: a `## 0.10.0 (2026-11-12)` entry at the top. It names: the skill and where it runs; the fixed settings (quick, 40 calls, source only, git-ignored folder); how its records are handled; that no other role uses it and the Reviewer prompt says so; the init offer with the pinned commit and the doctor checks; and, for existing projects, "update routine 5 before adding the skill". Both manifests: `0.10.0`.

## 5. Decisions

| # | Decision | Why | Cost if wrong |
|---|---|---|---|
| D1 | Only the sweep runs the skill; no guidance-mode use elsewhere | The goal is the sweep; other uses add four more copies of a rule for no stated problem | A project wanting advice-mode in a phase must run it by hand |
| D2 | `needs_validation` records are leads the sweep verifies, checks on staging and classifies itself | With no sandbox nearly every real lead ends there; leaving them unclassified would make the sweep weaker than today and park work on the owner | Some leads the skill doubted get a severity; step 3 already drops the unsubstantiated |
| D3 | HANDOFF wins on staging confirmation | The playbook lesson (a HIGH from code reading, refuted live) is why the rule exists; the skill has finished by then | None for the skill |
| D4 | Profile `quick`, budget 40 agent calls, fixed in the prompt; no config field | A weekly run on shared usage limits needs a ceiling; `quick` is one wave and says it is partial; a project can edit the line in its own routine | Less coverage per week than `standard`; the report says so each time |
| D5 | Output folder inside the checkout, git-ignored | Cloud sessions pre-approve file edits in the repo; a write to the home folder is unverified and could prompt. The skill allows this when the folder is chosen explicitly and verified ignored | A project that never ran the new init line has no ignore entry: the skill does not run and the report says why |
| D5a | The ignore check runs with `-c core.excludesFile=` (added after the build, see the round log) | A machine-wide ignore file can make the plain check pass for a project whose own `.gitignore` lacks the entry; the cloud session has no such file, so doctor would show a pass while the sweep skips the skill. The check must depend on the repo's own rules only | `.git/info/exclude` still counts, which is also not in the clone; it is rarely used |
| D6 | Source review only | No cloud sandbox meets the skill's controls; saying so up front stops any attempt to run target code or write scratch files | Leads lack local reproduction; staging check and D2 cover it |
| D7 | `init` copies one pinned commit; the files are not bundled here | The copied text and Node programs run unattended with credentials in reach; only the reviewed commit is known. Same licence-and-version pattern as superpowers | The pin ages; moving it is a release task |
| D8 | Sweep rules live once, in routine 5 | Eight rules in three files would drift | A reader of HANDOFF must open routine 5 for detail; HANDOFF says so |
| D9 | No test that runs the full audit unattended in this loop | It needs a cloud routine and a target repo; this repo has neither. What stands in: the workflow files were read (section 3), every prescribed command is short, writes stay inside the repo, the rule goes into every brief, `init` already hand-fires the first sweep, and doctor flags a sweep with no report for 8 days | A stall on the first unattended run of a project: seen at the hand-fired run or by doctor, and removed by deleting `.claude/skills/security-audit/` |
| D10 | Version 0.10.0 | New behaviour in a routine prompt | — |

## 6. File boundary

- `skills/autonomous-delivery/templates/routines/5-security-sweep.prompt.md`
- `skills/autonomous-delivery/templates/routines/2-reviewer.prompt.md` (lines 5 and 9 only)
- `skills/autonomous-delivery/templates/docs/HANDOFF.md` ("Skills" section only)
- `skills/autonomous-delivery/references/playbook.md` (sections 5b and 11)
- `skills/autonomous-delivery/references/cloud-setup.md`
- `skills/autonomous-delivery/SKILL.md`
- `commands/init.md`, `commands/doctor.md`
- `.claude-plugin/plugin.json`; root `.claude-plugin/marketplace.json`
- root `CHANGELOG.md`, root `README.md`
- root `.autodeliver/` (`config.json`, both plans and the round log; all committed)

Not touched: everything else, including the Worker and Fixer prompts, all agents, `commands/loop.md`, `references/config.md`, `merge-gate/`, scripts, and the untracked root `CLAUDE.md`.

## 7. Tasks

| # | Task | Done when |
|---|---|---|
| 1 | Routine 5, per 4.1 | Every numbered point of 4.1 is in the prompt; steps 1, 2b and 4 are byte-identical to before; the `**Unattended run:**` prefix is intact |
| 2 | HANDOFF and Reviewer prompt, per 4.2 | Both HANDOFF edits and both Reviewer lines read as written in 4.2 |
| 3 | `init.md` and `doctor.md`, per 4.3 and 4.4 | The pinned sha is identical in both files; the `.gitignore` bullet has the new entry |
| 4 | Playbook, cloud-setup, SKILL.md, README, per 4.5 | Each named sentence is present |
| 5 | Versions and CHANGELOG | Both manifests say 0.10.0; the entry is first in the file |
| 6 | Reread the whole diff once for repeated or conflicting wording (this stands in for `/simplify`, which is for code), run the proof, commit | Proof output quoted; one or two commits on the branch |

Writing style for all new text: plain, short sentences, the same voice as the surrounding file; no project names; double-brace placeholders only inside `templates/`, and only ones that already exist.

## 8. Test plan

1. **Proof:** every command in `.autodeliver/config.json` `proof_full`, with output.
2. **Greps:** `security-audit` appears in routine 5, the Reviewer prompt, HANDOFF, playbook, cloud-setup, SKILL.md, init, doctor, README and CHANGELOG, and in no other file under `plugins/`; under `plugins/`, the 40-character sha appears in exactly `init.md` and `doctor.md`, identical; in a scratch repo, `git -c core.excludesFile= check-ignore -q .autodeliver/security-audit/` exits 0 with the ignore line and no such folder, and 1 without the line (run it and quote the output); both manifests say 0.10.0; `git diff --name-only main` lists only boundary files; `git ls-files --eol` shows LF for each changed file.
3. **Read-through cases** for routine 5 (prompt text → expected action), each checked by the reviewer:
   - skill not vendored → bullets (a) and (b) by hand; "what you ran" says "not vendored";
   - vendored, `node --version` fails → by hand; cause named;
   - vendored, output folder not ignored → by hand; cause named; nothing written;
   - clean run → records used; (c) to (g) and drift were started first;
   - clean `quick` run with `deferred` units → each covered by hand or listed by name;
   - `incomplete` with valid `findings.json` → records used, gaps covered by hand or listed;
   - findings valid but the ledger validator fails, or `run_status` still `in_progress` → records used, no coverage claim, gaps by hand or listed;
   - findings validator fails, one correction, fails again; or no `findings.json` → no skill record used as a finding; by hand;
   - more than 10 `needs_validation` leads → 10 checked on staging, the rest `static-only`;
   - the three write statements (header line 4, role sentence line 7, unattended-run line) agree;
   - init on a project whose live routine 5 is old → routine updated first, or no vendoring; doctor shows ❌ for a vendored skill with an old routine;
   - `confirmed` informational → LOW;
   - `needs_validation` lead that staging can settle → staging check, then `runtime-confirmed` or `runtime-refuted`, with a severity;
   - `needs_validation` lead that staging cannot settle → listed as a finding, `static-only` with the reason; never dropped;
   - `rejected` → not reported;
   - the skill would ask (mode, output path, budget) → no question; decision named in the report;
   - no heredoc and no multi-line script anywhere in the prompt; every write lands in a request body, the report file or `.autodeliver/security-audit/`;
   - still exactly one `<PFX>-SECURITY` comment.
4. **Read-through cases elsewhere:** a Reviewer reading its prompt cannot use `security-audit`; a Worker or Fixer reading HANDOFF "Skills" cannot run it in either mode; `init` in local mode makes no offer; `init` with a failed clone skips and says so; each doctor ⚠️ condition in 4.4 has its sentence.
