---
description: Fresh-eyes review of any plan, spec, design doc or RFC before anything is built - four isolated reviewers (zoom-out, comprehension, critic, readiness) that never see your reasoning. No setup needed
argument-hint: "<document> [--lens zoom-out,comprehension,critic,readiness] [--drift]"
---

# /autodeliver:design-review

Document: $ARGUMENTS

Design with full context, review with fresh eyes. The idea comes from Google's [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model). This session knows why the document says what it says; the reviewers must not. That isolation is what makes the review worth running.

## 1. Inputs

- The document path is required. If none is given, look for an obvious candidate: a plan or spec changed on this branch, `docs/designs/*`, `*plan*.md` or `*spec*.md`. Ask only if there are several.
- The lenses: `--lens` lists them; the default is `design_review.lenses` from `.autodeliver/config.json`, else `zoom-out`, `comprehension`, `critic` and `readiness`.
- `--drift`: instead of reviewing a plan, compare the document (a system doc, design or README) with the code as it is now. This runs only the `drift` lens.
- Referenced material: the files the document links or names, and `HANDOFF.md`, `ROADMAP.md` and the system doc if the project has `.autodeliver/config.json`.

## 2. Dispatch, in parallel, one fresh agent per lens

Use the `design-reviewer` agent (`autodeliver:design-reviewer` if `.claude/agents/` doesn't have it). Each brief holds **only**:
- the lens;
- the document path;
- the paths of the referenced material;
- round 1.

**Never** add a summary, your reasoning, the alternatives you considered, or what you think of the document. If you wrote the document in this session, that rule matters most.

## 3. Report

Write the replies, merged, to a file beside the document named after it without its extension: `docs/plan.md` gives `docs/plan.design-review.md`.
It contains:
- a header with the date, the lenses and their verdicts (CLEAR or FINDINGS);
- the comprehension paraphrase, so the author can check it against the intent (a wrong paraphrase is itself a finding);
- the findings grouped as Blocking, Should-fix and Nit, each with its lens and location, with duplicates across lenses merged;
- each lens's notes on what it couldn't check.

In chat, give only the verdict line per lens, the counts, and the report path. Don't paste the report.

## 4. Next

- If the user wants to act on the findings, help them resolve each one: change the document, or record a decision and its cost if wrong. Then re-run only the lenses that had findings, with their previous findings, as round 2.
- In an autodeliver project, the Worker and `/autodeliver:loop` already run this step for every phase. This command is for any other document.

Read-only apart from the report file. Never edit the document unless the user asks.
