# Profiles

A profile tells the loop what **proof** means for this kind of work, what the **reviewer** checks beyond the generic list, what **evidence** to commit, and which **gates** are typical. `/autodeliver:init` writes the chosen profiles into `.autodeliver/config.json`, which you can edit at any time. You can combine profiles; for example, a migration usually also uses software.

The generic review checklist applies to every profile:
- **correctness** against the brief and plan;
- **plan completeness** (every task done or deferred by a ruling);
- **nothing parked for the user**;
- **fail safe** when an outside service is absent;
- **no secrets**;
- **no `TODO(user)`**;
- **evidence committed**;
- **stable findings** (each defect reported once, with a fix).

---

## software

- **Proof (full):** every test suite, typechecks, lint (new issues only), build, a schema or migration drift check, and e2e when the UI changed. Detect the commands from `package.json`, `pyproject.toml`, `Makefile`, `go.mod`, `Cargo.toml`, `pom.xml` or CI files, and confirm them during init.
- **Proof (touched):** the suites for the changed files, plus typechecks.
- **Reviewer adds:**
  - security (authn/authz, injection, secrets in responses and logs, SSRF, uploads);
  - concurrency and races, including sibling writers of the same rows;
  - migrations that are safe on real-shaped data;
  - error paths end to end, with a user-facing message for each new error;
  - tests that test real behaviour;
  - a strict test-database guard;
  - every user-facing string translated for each locale.
- **Specialist agents (optional):** if installed, `silent-failure-hunter`, `pr-test-analyzer`, `type-design-analyzer` and `comment-analyzer` from the official `pr-review-toolkit` plugin.
- **Evidence:** test counts, staging checks, Playwright screenshots in every locale (desktop and mobile), and a post-deploy log scan.
- **Gates:** production deploy; production data migration.

## docs (guides, courses, reports, policies, manuals)

- **Proof (full):** the project's validators (schema or front-matter checks, custom verify scripts), a link checker, render or build (static site, PDF, slides), and spelling and style lint. Also check word, heading or structure limits from the brief.
- **Proof (touched):** the same checks on the changed files.
- **Reviewer adds:**
  - accuracy against the cited sources, with each claim traceable;
  - completeness against the brief or outline;
  - audience, reading level and tone;
  - consistency of terms, numbering and cross-references;
  - accessibility (headings, alt text, contrast in rendered output);
  - translations reviewed by the `translation-reviewer` agent.
- **Evidence:** rendered output (HTML/PDF screenshots via the `visual-checker` agent), the source list, and the validator output.
- **Gates:** publication or sending to an external audience.

## data (analysis, notebooks, dashboards, pipelines, models)

- **Proof (full):** a reproducible run from a clean environment (fixed seeds, pinned inputs), data tests (`great_expectations`, `dbt test`, `pandera` or asserts), reconciliation counts and totals against the source, schema checks, and notebook execution end to end.
- **Proof (touched):** the changed steps, plus their downstream checks.
- **Reviewer adds:**
  - method soundness;
  - leakage and train/test separation;
  - sampling and bias;
  - units and time zones;
  - null handling;
  - charts that don't mislead;
  - **privacy**: no row-level personal data in outputs, logs or commits, aggregates only.
- **Evidence:** run logs, counts, and charts rendered and reviewed.
- **Gates:** writing to production data; sharing results externally.

## infra (IaC, configuration, servers, CI)

- **Proof (full):** `terraform plan`, `pulumi preview`, `kubectl diff` or `ansible --check`; policy-as-code (OPA, Checkov, tfsec); lint; apply to staging; health checks; and a log scan.
- **Reviewer adds:**
  - blast radius and rollback plan;
  - least privilege;
  - secrets never in argv, files or logs;
  - isolation from neighbouring workloads on shared hosts;
  - resource limits;
  - no public ports unless intended;
  - backups before destructive steps.
- **Evidence:** plan output, staging health, the log scan.
- **Gates:** production apply; anything destructive.

## migration (port, rewrite, upgrade, re-platform)

- **Proof (full):** golden tests generated from the source of truth, a parity matrix (every source behaviour mapped to a status), plus the software proof.
- **Reviewer adds:**
  - the source wins on conflicts unless a ruling says otherwise;
  - nothing silently dropped;
  - data-migration safety on real-shaped data;
  - a rehearsal of the cutover on an isolated copy before the gate.
- **Evidence:** the parity matrix, golden-test counts and the rehearsal report (counts only).
- **Gates:** cutover; placing real data for the rehearsal.

## research (decisions, designs, investigations, competitive or market analysis)

- **Proof (full):** every source reachable and quoted correctly, every claim traced to a source, no fabricated citations, and the structure required by the brief.
- **Reviewer adds:**
  - evidence quality and recency;
  - alternatives considered;
  - a cost-if-wrong for each recommendation;
  - separating fact from inference;
  - a balanced treatment.
- **Evidence:** the source list with access dates, and a decision record.
- **Gates:** sign-off on the decision.

---

## Defining your own profile

Add an entry to `profiles` in `.autodeliver/config.json`:

```json
{
  "name": "marketing-site",
  "proof_full": ["npm run build", "npx playwright test", "npx linkinator dist"],
  "proof_touched": ["npm run build"],
  "review_checklist": ["brand voice", "claims backed by a source", "every CTA works"],
  "evidence": ["screenshots in docs/delivery/evidence/<phase>/"],
  "gates": ["Publishing to the live site"]
}
```
