"""Tests for merge_gate.py. Run: python -m pytest -q (from this folder)."""
import pytest

import merge_gate as mg

HEAD = "a" * 40
OLD = "b" * 40
CFG = {"target": "main", "rules": [("work/", "ACME-REVIEW"), ("ops/", "OPS-REVIEW")], "trusted": {"bot"}, "dry_run": True}


def pr(**kw):
    base = {"id": 7, "title": "P03", "target": "main", "source": "work/p03-x", "fork": False, "open": True,
            "draft": False, "mergeable": True, "head": HEAD}
    base.update(kw)
    return base


def c(body, author="bot"):
    return {"authors": {author}, "body": body}


PASS = f"ACME-REVIEW {HEAD} VERDICT: PASS\n(round 1, full)"
FAIL = f"ACME-REVIEW {HEAD} VERDICT: FAIL\n(round 2, delta)"


# --- the happy path
def test_merges_on_trusted_pass_for_current_head():
    assert mg.decide(pr(), [c(PASS)], CFG)[0] == "merge"


# --- target and source rules
@pytest.mark.parametrize("target", ["release", "main-old", "Main"])
def test_target_must_match_exactly(target):
    assert mg.decide(pr(target=target), [c(PASS)], CFG)[0] == "skip"


def test_source_outside_worker_prefixes_is_skipped():
    assert mg.decide(pr(source="feature/x"), [c(PASS)], CFG)[0] == "skip"


def test_each_prefix_needs_its_own_marker():
    ops = pr(source="ops/p01")
    assert mg.decide(ops, [c(PASS)], CFG)[0] == "skip"
    assert mg.decide(ops, [c(f"OPS-REVIEW {HEAD} VERDICT: PASS")], CFG)[0] == "merge"


def test_longest_prefix_wins():
    rules = [("work/", "ACME-REVIEW"), ("work/ops-", "OPS-REVIEW")]
    assert mg.marker_for("work/ops-p1", rules) == "OPS-REVIEW"
    assert mg.marker_for("work/p1", rules) == "ACME-REVIEW"
    assert mg.marker_for("feature/p1", rules) is None


# --- PR state
@pytest.mark.parametrize("change", [{"open": False}, {"draft": True}, {"mergeable": False}, {"mergeable": None},
                                    {"fork": True}, {"head": ""}, {"head": "abc"}])
def test_pr_state_blocks(change):
    assert mg.decide(pr(**change), [c(PASS)], CFG)[0] == "skip"


# --- verdict rules
def test_pass_for_an_older_head_does_not_count():
    assert mg.decide(pr(), [c(f"ACME-REVIEW {OLD} VERDICT: PASS")], CFG)[0] == "skip"


@pytest.mark.parametrize("order", [[PASS, FAIL], [FAIL, PASS]])
def test_any_trusted_fail_on_the_head_blocks_whatever_the_order(order):
    assert mg.decide(pr(), [c(b) for b in order], CFG)[0] == "skip"


def test_fail_on_an_older_head_does_not_block():
    assert mg.decide(pr(), [c(f"ACME-REVIEW {OLD} VERDICT: FAIL"), c(PASS)], CFG)[0] == "merge"


def test_untrusted_author_is_ignored():
    assert mg.decide(pr(), [c(PASS, author="someone")], CFG)[0] == "skip"


def test_untrusted_fail_does_not_block_trusted_pass():
    assert mg.decide(pr(), [c(PASS), c(FAIL, author="someone")], CFG)[0] == "merge"


def test_trusted_identity_is_case_insensitive_and_any_alias_counts():
    cfg = dict(CFG, trusted={"delivery@example.com"})
    comment = {"authors": {"Delivery@Example.com", "1234-guid"}, "body": PASS}
    assert mg.decide(pr(), [comment], cfg)[0] == "merge"


@pytest.mark.parametrize("body", [
    f"Looks good. ACME-REVIEW {HEAD} VERDICT: PASS",           # not on the first line
    f"\nACME-REVIEW {HEAD} VERDICT: PASS",                     # first line empty
    f"ACME-REVIEW {HEAD[:12]} VERDICT: PASS",                  # short sha
    f"ACME-REVIEW {HEAD.upper()} VERDICT: PASS",               # not lowercase hex
    f"ACME-REVIEWX {HEAD} VERDICT: PASS",                      # different marker
    f"ACME-REVIEW-CLAIM {HEAD}",                               # the Reviewer's claim, not a verdict
    f"ACME-REVIEW {HEAD} VERDICT: PASSED",                     # not the exact word
    f"> ACME-REVIEW {HEAD} VERDICT: PASS",                     # a quote of the marker
    "",
])
def test_malformed_markers_do_not_count(body):
    assert mg.decide(pr(), [c(body)], CFG)[0] == "skip"


# --- config
def test_rules_parse_and_reject_bad_entries():
    assert mg.parse_rules(" work/=A , ops/=B ") == [("work/", "A"), ("ops/", "B")]
    for bad in ["", "work/", "=A", "work/="]:
        with pytest.raises(ValueError):
            mg.parse_rules(bad)


BASE_ENV = {"MERGE_GATE_HOST": "github", "MERGE_GATE_TARGET": "main", "MERGE_GATE_RULES": "work/=ACME-REVIEW",
            "MERGE_GATE_TRUSTED": "Bot", "MERGE_GATE_TOKEN": "t", "MERGE_GATE_REPO": "o/r"}


def test_dry_run_is_the_default_and_trusted_is_casefolded():
    host, cfg = mg.load_config(BASE_ENV)
    assert host == "github" and cfg["dry_run"] is True and cfg["trusted"] == {"bot"}
    assert mg.load_config(dict(BASE_ENV, MERGE_GATE_DRY_RUN="False"))[1]["dry_run"] is False
    for v in ["no", "", "$(MERGE_GATE_DRY_RUN)"]:
        assert mg.load_config(dict(BASE_ENV, MERGE_GATE_DRY_RUN=v))[1]["dry_run"] is True


@pytest.mark.parametrize("change", [{"MERGE_GATE_TOKEN": ""}, {"MERGE_GATE_TOKEN": "$(MERGE_GATE_PAT)"},
                                    {"MERGE_GATE_TARGET": "release/*"}, {"MERGE_GATE_TRUSTED": " "},
                                    {"MERGE_GATE_HOST": "gitlab"}])
def test_bad_config_is_refused(change):
    with pytest.raises(ValueError):
        mg.load_config(dict(BASE_ENV, **change))


def test_main_returns_1_on_bad_config(capsys):
    assert mg.main(dict(BASE_ENV, MERGE_GATE_TOKEN="")) == 1
    assert "MERGE_GATE_TOKEN" in capsys.readouterr().err


# --- host payloads
def test_ado_normalize():
    p = {"pullRequestId": 5, "title": "t", "status": "active", "isDraft": False, "mergeStatus": "succeeded",
         "targetRefName": "refs/heads/main", "sourceRefName": "refs/heads/work/p1",
         "lastMergeSourceCommit": {"commitId": HEAD.upper()}}
    n = mg.Ado.normalize(p)
    assert (n["target"], n["source"], n["open"], n["mergeable"], n["head"], n["fork"]) == ("main", "work/p1", True, True, HEAD, False)
    assert mg.Ado.normalize(dict(p, mergeStatus="conflicts"))["mergeable"] is False
    assert mg.Ado.normalize(dict(p, mergeStatus="queued"))["mergeable"] is None
    assert mg.Ado.normalize(dict(p, forkSource={"name": "refs/heads/x"}))["fork"] is True


def gh_pr(**kw):
    p = {"number": 3, "title": "t", "state": "open", "draft": False, "mergeable": True, "mergeable_state": "clean",
         "base": {"ref": "main", "repo": {"full_name": "o/r"}}, "head": {"ref": "work/p1", "sha": HEAD, "repo": {"full_name": "o/r"}}}
    p.update(kw)
    return p


def test_github_normalize():
    assert mg.GitHub.normalize(gh_pr())["mergeable"] is True
    assert mg.GitHub.normalize(gh_pr(mergeable_state="blocked"))["mergeable"] is False
    assert mg.GitHub.normalize(gh_pr(mergeable=None))["mergeable"] is None
    assert mg.GitHub.normalize(gh_pr())["fork"] is False
    fork = gh_pr(head={"ref": "work/p1", "sha": HEAD, "repo": {"full_name": "someone/r"}})
    assert mg.GitHub.normalize(fork)["fork"] is True
    deleted_fork = gh_pr(head={"ref": "work/p1", "sha": HEAD, "repo": None})
    assert mg.GitHub.normalize(deleted_fork)["fork"] is True


def test_github_refresh_asks_again_when_mergeable_is_not_ready():
    answers = [gh_pr(mergeable=None), gh_pr()]

    class FakeApi:
        def call(self, method, url, body=None):
            return answers.pop(0)

    waits = []
    gh = mg.GitHub(BASE_ENV, api=FakeApi(), wait=waits.append)
    assert gh.refresh({"id": 3})["mergeable"] is True and waits == [5]


# --- end to end with a fake host
class FakeHost:
    done_words = ("merged", "merge requested")

    def __init__(self, prs, comments, fail_on=()):
        self.prs, self.cm, self.fail_on = prs, comments, set(fail_on)
        self.merged, self.notes, self.comment_calls, self.refreshes = [], [], [], []

    def open_prs(self, target):
        return [p for p in self.prs if p["target"] == target]

    def comments(self, p):
        self.comment_calls.append(p["id"])
        return self.cm.get(p["id"], [])

    def refresh(self, p):
        self.refreshes.append(p["id"])
        return p

    def complete(self, p, title):
        if p["id"] in self.fail_on:
            raise RuntimeError("PUT .../merge -> HTTP 409: Head branch was modified")
        self.merged.append(p["id"])
        return True

    def note(self, p, text):
        self.notes.append((p["id"], text))


QUIET = dict(log=lambda *_: None)


def test_run_dry_run_merges_nothing():
    host = FakeHost([pr()], {7: [c(PASS)]})
    assert mg.run(host, CFG, **QUIET) == (0, 0) and host.merged == []


def test_run_live_merges_only_passing_worker_prs_and_notes_them():
    prs = [pr(id=1), pr(id=2, source="feature/y"), pr(id=3), pr(id=4, draft=True)]
    host = FakeHost(prs, {1: [c(PASS)], 2: [c(PASS)], 3: [c(FAIL)], 4: [c(PASS)]})
    assert mg.run(host, dict(CFG, dry_run=False), **QUIET) == (1, 0)
    assert host.merged == [1] and host.notes[0][1].startswith(f"MERGE-GATE {HEAD} merged")
    assert host.comment_calls == [1, 3]   # no comment fetch for people's own PRs or drafts
    assert host.refreshes == [1]          # the state check only for a PASS candidate


def test_one_refused_merge_does_not_stop_the_others():
    host = FakeHost([pr(id=1), pr(id=2)], {1: [c(PASS)], 2: [c(PASS)]}, fail_on={1})
    assert mg.run(host, dict(CFG, dry_run=False), **QUIET) == (1, 1)
    assert host.merged == [2]
