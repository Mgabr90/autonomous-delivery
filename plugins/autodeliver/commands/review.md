---
description: One-shot independent review gate on your current changes, a branch, a PR or files - no setup needed. Runs the full proof itself and returns PASS or FAIL with Blocking, Should-fix and Nit findings
argument-hint: "[diff range | PR number | files…]  [--fix] [--comment]"
---

# /autodeliver:review

Scope: $ARGUMENTS

The fastest way to try autodeliver: an independent reviewer that did not write the code checks it as a gate, and runs the project's tests, typechecks, lint and build itself before any PASS. It works in any repo, with or without `/autodeliver:init`.

## 1. Find the scope (no questions unless it is ambiguous)

- **No argument:** everything on this branch that isn't on the main branch, plus uncommitted and new files: `git diff $(git merge-base HEAD <base>)` (this includes uncommitted changes to tracked files) plus the untracked files from `git ls-files --others --exclude-standard`. `<base>` is `origin/<main>`, where `<main>` comes from `git symbolic-ref refs/remotes/origin/HEAD`; with no remote, it is the local `main` or `master` branch if one exists and differs from the current branch. Otherwise, use the uncommitted changes and untracked files, or the last commit if the tree is clean.
- **A number:** a pull request. Read it with `gh pr view <n>` and `gh pr diff <n>` (on Azure DevOps, the REST call in the host doc if the repo has one).
- **A range** (`a..b`, `a...b`) or **files:** use them as given.
- If the scope is empty, say so and stop.

Say the scope in one line (files and line counts) before dispatching.

## 2. Find the proof

- If `.autodeliver/config.json` exists, use its `profiles`, `proof_full`, `e2e`, `review_checklist` and `locales`.
- Otherwise detect the commands from `package.json` scripts, `pyproject.toml`, `Makefile`, `go.mod`, `Cargo.toml`, `pom.xml` or `build.gradle`, and CI files (tests, typecheck, lint, build). Infer the profile from the repo (software by default, docs for a docs site, and so on). Say what you detected, and that `/autodeliver:init` makes it permanent.
- Find the intent: the PR description, the commit messages, a plan or spec the changes reference, or the user's words. A review without intent can only judge correctness, so say which one you used.

## 3. Review

Dispatch the `delivery-reviewer` agent (`autodeliver:delivery-reviewer` if `.claude/agents/` doesn't have it) with the scope (including the untracked files by path), the intent, the proof commands and the profile (state them explicitly when there is no config), round 1, and "no plan" unless a plan covers these changes. **Don't review the work yourself, and don't send your opinion of it.** The reviewer runs the proof itself.

## 4. Report

Show the verdict as the reviewer returned it: the first line `VERDICT: PASS | FAIL`, then Blocking, Should-fix, Nits, plan completeness (if there was a plan) and what it ran. Then one line: the counts, and the next step.

- **`--fix`:** on FAIL, continue as `/autodeliver:loop` on the same scope from round 1's findings (fix the listed items, then re-review until PASS or the cap). Stop at PASS.
- **`--comment`:** only for a PR scope, and only when the flag is given. Post the verdict as one PR comment with `gh pr comment`. Never post without the flag.

Never edit files without `--fix`, never push, and never print secrets.
