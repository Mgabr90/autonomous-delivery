---
description: Set up autonomous delivery in this project (local loop or cloud routines) — config, charter docs, agents, and optionally routines, webhooks and a loop test
argument-hint: "[local|cloud] [profile…]  e.g. 'cloud software' or 'local docs'"
---

# /autodeliver:init

Set up the autonomous delivery loop for the current project. Arguments (optional): $ARGUMENTS

First load the `autonomous-delivery` skill, and read `references/playbook.md`, `references/profiles.md` and `references/config.md`. In cloud mode, also read `references/cloud-setup.md`.

## 1. Detect (no questions yet)

- Check whether this is a git repo, find the remote (`git remote get-url origin`), and get the main branch (`git symbolic-ref refs/remotes/origin/HEAD`, or `main`).
- Find the tooling: `package.json` scripts, `pyproject.toml`, `Makefile`, `go.mod`, `Cargo.toml`, `pom.xml`/`build.gradle`, CI files, docs generators (mkdocs, docusaurus, sphinx), notebooks, Terraform. Propose the proof commands from these.
- Find locales: i18n folders and catalogue files.
- Look for existing `CLAUDE.md`, `.claude/`, `.autodeliver/config.json`. If a config exists, offer to update it instead of starting over.

## 2. Ask once (AskUserQuestion, up to 4 questions, with detected defaults pre-selected)

1. **Mode:**
   - local: one session, with subagents;
   - cloud: routines fired by GitHub; needs a GitHub repo and a claude.ai/code environment.
2. **Profiles:** software, docs, data, infra, migration or research. Allow several.
3. **Proof commands:** confirm or edit the detected `proof_full` (and `proof_touched`).
4. **Gates:** what may only happen with the owner's approval, for example production deploy, publication or a production data write. Default: "Production deploy".

Derive the rest without asking:
- `project` from the repo or folder name;
- `marker_prefix` as an uppercase slug;
- `label` as `<slug>-review-fail`;
- `branch_prefix` as `work/`;
- `locales` from detection;
- `loop.cap` 5 and `fail_review_cap` 10.

In cloud mode, also ask for the claude.ai/code `environment_id`, and whether there is a staging host (if so, its URL).

## 3. Write files (show the list first, then write)

- `.autodeliver/config.json`.
- From `templates/docs/`, filling every `{{…}}`:
  - `docs/delivery/HANDOFF.md`;
  - `docs/delivery/DECISIONS_LOG.md` (today's date);
  - `docs/delivery/ROADMAP.md`;
  - `docs/delivery/ledgers/` and `docs/delivery/plans/`;
  - `docs/delivery/evidence/` (with a `.gitkeep`).

  Ask in one line for the goal and the first phase, or derive a draft from the README and say it is a draft.
- `CLAUDE.md`: add or append a short section "Ongoing work: read `docs/delivery/HANDOFF.md` first; work autonomously within its hard limits."
- `.claude/agents/`: copy this plugin's agents (`delivery-reviewer`, `delivery-fixer`, `visual-checker`, `translation-reviewer`, `usage-inspector`), so cloud sessions get them. Optionally, if the official `pr-review-toolkit` plugin is installed locally, offer to copy `silent-failure-hunter`, `pr-test-analyzer`, `type-design-analyzer` and `comment-analyzer` too, with its LICENSE as `.claude/agents/PR-REVIEW-TOOLKIT-LICENSE.txt`.
- Staging (if any): copy `templates/staging/stg.sh` to `tools/stg.sh`, and point the user to `templates/staging/README.md` for the server side. Never ask for or store a token.
- `.gitignore`: add `.autodeliver/token_log*`, `.autodeliver/*.state.json` and `.autodeliver/loop_state.json`.

## 4. Cloud mode only (confirm before each persistent change)

1. **Label and alerts:** create `<label>` with `gh`, and offer to enable dependency alerts.
2. **Routines:** for each of the five templates in `templates/routines/`:
   - fill the placeholders from the config (proof lists joined with `; `, gates and hard limits as `;`-separated sentences);
   - show the routine name, trigger and model;
   - after one confirmation for all five, create them with RemoteTrigger (body shape in `references/cloud-setup.md`, with a fresh uuid each), then attach the webhooks.

   Save the trigger ids into `config.routines`.
3. **Commit and push** the setup files on a branch `<branch_prefix>setup`, and open a PR. That PR is the **deliberate loop test**: the Reviewer must review and merge it.
4. **Trigger the usage inspector and the security sweep once by hand** after the first merge, and read their first reports.

## 5. Local mode

- Explain `/autodeliver:loop <task>`.
- The token log is **on by default** (`"token_log": true` in the config). The plugin's Stop and SubagentStop hooks append rows to `.autodeliver/token_log.csv` (git-ignored). Say so in one line, and mention that `"token_log": false` turns it off.
- Offer a seeded-defect dry run: create a small sample with 3 planted defects, run the reviewer on it, and confirm it catches all 3.

## 6. Check

Run `grep -rn "{{" docs/delivery .claude/agents CLAUDE.md` (and the routine prompts you sent). It must return nothing except `LEDGER.md`-style per-phase templates kept on purpose. Fill anything left using `references/config.md` → "Template placeholders".

## 7. Finish

Print a short summary:
- what was written;
- for cloud mode, the routines created with their ids and next run times;
- the gates;
- what happens next.

Never print or commit secrets. Never cross a hard limit while setting up.
