# Merge gate (optional workaround)

**Not the default.** By default the Reviewer routine merges a PR itself on PASS, pinned to the reviewed sha. If that merge is refused, it posts `<PFX>-MERGE-PENDING` and the owner merges (playbook section 10). Use this gate only when a project keeps hitting that refusal and wants merges to happen without the owner.

## Why it exists

In unattended cloud runs, the auto-mode permission check can refuse a routine completing a PR it is part of. The categories reported are "Merge Without Review" and "Self-Approval", and a force-push gets "Git Destructive". This happens even after an independent reviewer subagent posts PASS, and prompt text can't count as approval. One project had a passed PR sit unmerged for 13 hours.

The official fix is a server-managed `autoMode` setting from an organisation Owner. Without one, this gate moves the merge out of the routines: a scheduled pipeline, in a repo the routines never write to, completes only the PRs the Reviewer passed.

## What it merges

A PR is merged only when **all** of these hold (see `decide()` in `merge_gate.py`):
- the target is exactly `MERGE_GATE_TARGET`;
- the source branch starts with a Worker prefix from `MERGE_GATE_RULES`, and that prefix names the marker that must pass it;
- the PR is open, not a draft, and the host says it can merge (Azure DevOps `mergeStatus = succeeded`; GitHub `mergeable` with a clean state, so branch protection still applies);
- the newest verdict for the **current head** is `<marker> <40-character sha> VERDICT: PASS`, on the first line of a comment by a `MERGE_GATE_TRUSTED` identity. A later FAIL wins over an earlier PASS, and anyone else's markers are ignored.

It merges pinned to that head (Azure DevOps `lastMergeSourceCommit`, no fast-forward; GitHub `sha`, merge commit), keeps the branch, and posts `MERGE-GATE <sha> …` on the PR. PRs from other branches are left alone and get no comment. **The Reviewer must post the full 40-character head sha** in its verdict line, which the 0.8.0 Reviewer template does.

## Set it up

1. **A separate repo.** Put `merge_gate.py` and `test_merge_gate.py` in a repo the routines never push to. If the gate lived in the repo it merges, a Worker PR could loosen the gate and then be merged by it.
2. **Azure DevOps** (`azure-pipelines.yml`):
   - create the pipeline from the file, and fill in the `edit` lines;
   - add the secret variable `MERGE_GATE_PAT`: a PAT from the identity the routines use, with Code: Read & write, renewed before it expires. The build service's own `System.AccessToken` usually lacks "Contribute to pull requests", and only a Project Administrator can grant it;
   - secrets reach the script only through `env:`. An unset secret arrives as the literal `$(MERGE_GATE_PAT)`, which the gate treats as missing;
   - a self-hosted pool needs a pool administrator to permit the pipeline; `ubuntu-latest` doesn't.
3. **GitHub** (`github-merge-gate.yml` → `.github/workflows/merge-gate.yml` in the separate repo):
   - add the secret `MERGE_GATE_TOKEN`: a fine-grained PAT on the target repo with Pull requests and Contents read & write;
   - set `MERGE_GATE_TRUSTED` to the login the Reviewer routine posts as;
   - an alternative is branch protection with a required status plus auto-merge, but that path hasn't been tested with routines.
4. **Dry run first.** The gate only logs what it would do until `MERGE_GATE_DRY_RUN` is exactly `false`. Before going live, check its decisions against PRs you already merged by hand: every PASS head should say "merge", and nothing else should.
5. **Switch the routines over:** set `"merge": {"by": "gate"}` in `.autodeliver/config.json` and update the live Reviewer and Worker prompts (edit the live prompt; never rebuild it from an old copy). From then on, the Reviewer posts its PASS and stops, and the Worker treats a PR open at a PASS head as waiting for the gate, not as stuck.

## Run the tests

`python -m pytest -q` in this folder. Standard library only; pytest only for the tests.

The gate's rules and the no-heredoc rule in the routine prompts came from a team running two unattended Azure DevOps cloud Workers, where both were proven live in November 2026.
