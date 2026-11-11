# Merge pipeline (optional workaround)

**Not the default.** By default the Reviewer routine merges a PR itself on PASS, pinned to the reviewed sha. If that merge is refused, it posts `<PFX>-MERGE-PENDING` and the owner merges. Use this pipeline only when a project keeps hitting that refusal and wants merges to happen without the owner.

**Why it exists:** in unattended cloud runs, the auto-mode permission check can refuse a routine completing its own PR, even after an independent review posted PASS. The official fix is an organisation-managed `autoMode` setting. This pipeline is the fallback when there isn't one: it moves the merge out of the routines. The full background is in the plugin's `references/cloud-setup.md`, section "Unattended runs".

## What it merges

A PR is merged only when **all** of these hold (`precheck()` and `decide()` in `merge_gate.py`):
- the target is exactly `MERGE_GATE_TARGET`;
- the source branch starts with a Worker prefix from `MERGE_GATE_RULES`, which names the marker that must pass it, and the PR isn't from a fork;
- the PR is open, not a draft, and the host says it can merge (Azure DevOps `mergeStatus = succeeded`; GitHub `mergeable` with a clean state, so branch protection still applies);
- a `MERGE_GATE_TRUSTED` identity posted `<marker> <40-character sha> VERDICT: PASS` on the first line of a comment, for the **current head**;
- **no trusted FAIL exists for that head.** Every re-review is of a new head, so a PASS and a FAIL on one head mean two reviewers disagreed. The FAIL's findings must be fixed first.

It merges pinned to that head (Azure DevOps `lastMergeSourceCommit`, no fast-forward; GitHub `sha`, merge commit), keeps the branch, and posts `MERGE-GATE <sha> …` on the PR. Other PRs are left alone and get no comment. A refused merge on one PR is logged and doesn't stop the others; any failed API call makes the run exit 1, so the pipeline shows red. The Reviewer template (0.8.0 and later) writes the full 40-character head sha that the pipeline needs.

## Trust: what this pipeline can and can't tell

- **It trusts an identity, not a role.** When every routine posts as one identity (usual on Azure DevOps, where they share one PAT), any routine could post a PASS marker, including one manipulated by content it read. Where the host allows it, give the Reviewer its own identity and list only that one in `MERGE_GATE_TRUSTED`.
- **The pipeline's own repo must be out of the routines' reach.** If the routines could push to it, they could loosen its rules and then be merged by it. A Code read & write PAT can often reach every repo in an Azure DevOps project, so:
  - deny the routines' identity Contribute on the pipeline's repo; or
  - protect its `main` with a required human review that identity can't bypass.

  On GitHub, keep the pipeline's repo out of the routines' app installation and tokens.

## Set it up

1. **A separate repo:** put `merge_gate.py` and `test_merge_gate.py` there, protected as described above.
2. **Azure DevOps** (`azure-pipelines.yml`):
   - create the pipeline from the file, and fill in the `edit` lines;
   - add the secret variable `MERGE_GATE_PAT`: a PAT with Code: Read & write, renewed before it expires. The build service's own `System.AccessToken` usually lacks "Contribute to pull requests", and only a Project Administrator can grant it;
   - secrets reach the script only through `env:`. An unset secret arrives as the literal `$(MERGE_GATE_PAT)`, which the pipeline treats as missing;
   - a self-hosted pool needs a pool administrator to permit the pipeline; `ubuntu-latest` doesn't.
3. **GitHub** (`github-merge-gate.yml` → `.github/workflows/merge-gate.yml` in the separate repo):
   - add the secret `MERGE_GATE_TOKEN`: a fine-grained PAT on the target repo with Pull requests and Contents read & write;
   - set `MERGE_GATE_TRUSTED` to the login the Reviewer routine posts as;
   - GitHub turns off scheduled workflows in a public repo after 60 days without activity. Re-enable the workflow if `doctor` reports PASS heads waiting, or keep the repo private;
   - an alternative is branch protection with a required status plus auto-merge, but that path hasn't been tested with routines.
4. **Dry run first.** The pipeline only logs what it would do until `MERGE_GATE_DRY_RUN` is exactly `false`. Before going live, check its decisions against PRs you already merged by hand: every PASS head should say "merge", and nothing else should.
5. **Switch the routines over:** set `"merge": {"by": "pipeline", "pending_after_min": 180}` in `.autodeliver/config.json`. The 0.8.0 Reviewer and Worker prompts read that setting. Routines created from older templates need their live prompts updated once (edit the live prompt; never rebuild it from an old copy).

## Run it on a server you control (no pipeline minutes)

If you already run a Linux server (staging, for example), a systemd timer can run the same script there, with no CI minutes used. The files are in `server/`. This takes an operator who can log in as root; sessions can't install them, and the owner places the token.

1. **Install as root:**
   - `useradd --system --no-create-home --shell /usr/sbin/nologin merge-gate`
   - `install -d -m 755 /opt/merge-gate /etc/merge-gate`
   - copy `merge_gate.py` to `/opt/merge-gate/` (644);
   - copy `server/install-token.sh` to `/opt/merge-gate/` (700);
   - copy `server/config.env` to `/etc/merge-gate/config.env` and fill it in (644; it holds no secret);
   - copy `server/merge-gate.service` and `server/merge-gate.timer` to `/etc/systemd/system/`;
   - then run `systemctl daemon-reload && systemctl enable --now merge-gate.timer`.
2. **What the units do:**
   - the timer runs every 10 minutes;
   - the service runs as the unprivileged `merge-gate` user, with `MemoryMax=96M`, no capabilities and a read-only system;
   - it does nothing until `/etc/merge-gate/token.env` exists.

   If the server hosts other projects, this adds no ports and no containers, and it reads nothing of theirs.
3. **The owner places the token** from their own machine. Create a fine-grained token for the target repo only, with Pull requests and Contents set to Read and write. Then pipe it in:
   - **bash:** `read -rs T && printf 'MERGE_GATE_TOKEN=%s
' "$T" | ssh <server> /opt/merge-gate/install-token.sh; unset T`
   - **PowerShell:** read it with `Read-Host -AsSecureString`, then pipe `"MERGE_GATE_TOKEN=$token"` into `ssh <server> /opt/merge-gate/install-token.sh`. The script strips the CR that PowerShell adds.

   `install-token.sh` stores the token root-only, runs one dry run, and switches to live only if that run reports `0 errors`.
4. **Check it:**
   - `journalctl -u merge-gate -n 50` shows its decisions;
   - `systemctl start merge-gate.service` runs it at once.

   Before going live, feed a merged PR's real comments to `decide()` the way the tests do: its PASS head must say "merge", and an earlier FAIL head must say "skip".
5. **Set `merge.pending_after_min` to about 30.** That covers the 10-minute timer with a margin.

A scheduled task on the owner's PC can run the same script, but it only merges while that PC is on. Use it as a backup, not as the gate.

The tests run on every push to the pipeline's repo (`python -m pytest -q` in this folder), not on the hourly schedule. Standard library only; pytest only for the tests.

The pipeline's rules come from a team that ran it with two unattended Azure DevOps cloud Workers in November 2026.
