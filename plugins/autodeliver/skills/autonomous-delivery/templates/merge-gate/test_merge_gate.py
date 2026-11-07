"""Tests for merge_gate.py. Run: python -m pytest -q (from this folder)."""
import pytest

import merge_gate as mg

HEAD = "a" * 40
OLD = "b" * 40
CFG = {"target": "main", "rules": [("work/", "ACME-REVIEW"), ("ops/", "OPS-REVIEW")], "trusted": {"bot"}, "dry_run": True}


def pr(**kw):
    base = {"id": 7, "title": "P03", "target": "main", "source": "work/p03-x", "open": True, "draft": False,
            "mergeable": True, "head": HEAD}
    base.update(kw)
    return base


def c(body, author="bot", time="2026-11-07T10:00:00Z", id=1):
    return {"author": author, "body": body, "time": time, "id": id}


PASS = f"ACME-REVIEW {HEAD} VERDICT: PASS\n(round 1, full)"
FAIL = f"ACME-REVIEW {HEAD} VERDICT: FAIL\n(round 2, delta)"


# --- the happy path
def test_merges_on_trusted_pass_for_current_head():
    assert mg.decide(pr(), [c(PASS)], CFG)[0] == "merge"


# --- target and source rules
def test_wrong_target_is_skipped_even_with_pass():
    assert mg.decide(pr(target="release"), [c(PASS)], CFG)[0] == "skip"


def test_target_must_match_exactly_not_by_prefix():
    assert mg.decide(pr(target="main-old"), [c(PASS)], CFG)[0] == "skip"


def test_source_outside_worker_prefixes_is_skipped():
    assert mg.decide(pr(source="feature/x"), [c(PASS)], CFG)[0] == "skip"


def test_each_prefix_needs_its_own_marker():
    ri = pr(source="ops/p01")
    assert mg.decide(ri, [c(PASS)], CFG)[0] == "skip"
    assert mg.decide(ri, [c(f"OPS-REVIEW {HEAD} VERDICT: PASS")], CFG)[0] == "merge"


def test_longest_prefix_wins():
    rules = [("work/", "ACME-REVIEW"), ("work/ops-", "OPS-REVIEW")]
    assert mg.marker_for("work/ops-p1", rules) == "OPS-REVIEW"
    assert mg.marker_for("work/p1", rules) == "ACME-REVIEW"


# --- PR state
@pytest.mark.parametrize("change", [{"open": False}, {"draft": True}, {"mergeable": False}, {"mergeable": None}])
def test_pr_state_blocks(change):
    assert mg.decide(pr(**change), [c(PASS)], CFG)[0] == "skip"


def test_unknown_head_is_skipped():
    assert mg.decide(pr(head=""), [c(PASS)], CFG)[0] == "skip"


# --- verdict rules
def test_pass_for_an_older_head_does_not_count():
    old_pass = f"ACME-REVIEW {OLD} VERDICT: PASS"
    assert mg.decide(pr(), [c(old_pass)], CFG)[0] == "skip"


def test_later_fail_wins_over_earlier_pass():
    comments = [c(PASS, time="2026-11-07T10:00:00Z", id=1), c(FAIL, time="2026-11-07T10:05:00Z", id=2)]
    assert mg.decide(pr(), comments, CFG)[0] == "skip"


def test_later_pass_wins_over_earlier_fail():
    comments = [c(FAIL, time="2026-11-07T10:00:00Z", id=1), c(PASS, time="2026-11-07T10:05:00Z", id=2)]
    assert mg.decide(pr(), comments, CFG)[0] == "merge"


def test_untrusted_author_is_ignored():
    assert mg.decide(pr(), [c(PASS, author="someone")], CFG)[0] == "skip"


def test_untrusted_fail_does_not_block_trusted_pass():
    comments = [c(PASS, time="2026-11-07T10:00:00Z"), c(FAIL, author="someone", time="2026-11-07T10:05:00Z", id=2)]
    assert mg.decide(pr(), comments, CFG)[0] == "merge"


@pytest.mark.parametrize("body", [
    f"Looks good. ACME-REVIEW {HEAD} VERDICT: PASS",           # not on the first line
    f"\nACME-REVIEW {HEAD} VERDICT: PASS",                     # first line empty
    f"ACME-REVIEW {HEAD[:12]} VERDICT: PASS",                  # short sha
    f"ACME-REVIEW {HEAD.upper()} VERDICT: PASS",               # not lowercase hex
    f"ACME-REVIEWX {HEAD} VERDICT: PASS",                      # different marker
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
            "MERGE_GATE_TRUSTED": "bot", "MERGE_GATE_TOKEN": "t", "MERGE_GATE_REPO": "o/r"}


def test_dry_run_is_the_default():
    assert mg.load_config(BASE_ENV)[2]["dry_run"] is True
    assert mg.load_config(dict(BASE_ENV, MERGE_GATE_DRY_RUN="False"))[2]["dry_run"] is False
    assert mg.load_config(dict(BASE_ENV, MERGE_GATE_DRY_RUN="no"))[2]["dry_run"] is True


@pytest.mark.parametrize("change", [{"MERGE_GATE_TOKEN": ""}, {"MERGE_GATE_TOKEN": "$(MERGE_GATE_PAT)"},
                                    {"MERGE_GATE_TARGET": "release/*"}, {"MERGE_GATE_TRUSTED": " "},
                                    {"MERGE_GATE_HOST": "gitlab"}])
def test_bad_config_is_refused(change):
    with pytest.raises(ValueError):
        mg.load_config(dict(BASE_ENV, **change))


def test_pat_fallback_name_is_accepted():
    env = dict(BASE_ENV, MERGE_GATE_TOKEN="")
    env["MERGE_GATE_PAT"] = "p"
    assert mg.load_config(env)[1]["MERGE_GATE_TOKEN"] == "p"


def test_main_returns_1_on_bad_config(capsys):
    assert mg.main(dict(BASE_ENV, MERGE_GATE_TOKEN="")) == 1
    assert "MERGE_GATE_TOKEN" in capsys.readouterr().err


# --- host payloads
def test_ado_normalize():
    p = {"pullRequestId": 5, "title": "t", "status": "active", "isDraft": False, "mergeStatus": "succeeded",
         "targetRefName": "refs/heads/main", "sourceRefName": "refs/heads/work/p1",
         "lastMergeSourceCommit": {"commitId": HEAD.upper()}}
    n = mg.Ado.normalize(p)
    assert (n["target"], n["source"], n["open"], n["mergeable"], n["head"]) == ("main", "work/p1", True, True, HEAD)
    assert mg.Ado.normalize(dict(p, mergeStatus="conflicts"))["mergeable"] is False
    assert mg.Ado.normalize(dict(p, mergeStatus="queued"))["mergeable"] is None


def test_github_normalize_blocked_is_not_mergeable():
    p = {"number": 3, "title": "t", "state": "open", "draft": False, "mergeable": True, "mergeable_state": "clean",
         "base": {"ref": "main"}, "head": {"ref": "work/p1", "sha": HEAD}}
    assert mg.GitHub.normalize(p)["mergeable"] is True
    assert mg.GitHub.normalize(dict(p, mergeable_state="blocked"))["mergeable"] is False
    assert mg.GitHub.normalize(dict(p, mergeable=None))["mergeable"] is None


# --- end to end with a fake host
class FakeHost:
    def __init__(self, prs, comments, merge_ok=True):
        self.prs, self.cm, self.merge_ok, self.merged = prs, comments, merge_ok, []

    def open_prs(self, target):
        return [p for p in self.prs if p["target"] == target]

    def comments(self, p):
        return self.cm.get(p["id"], [])

    def merge(self, p, reason):
        self.merged.append(p["id"])
        return self.merge_ok


def test_run_dry_run_merges_nothing():
    host = FakeHost([pr()], {7: [c(PASS)]})
    assert mg.run(host, CFG, log=lambda *_: None) == 0 and host.merged == []


def test_run_live_merges_only_passing_worker_prs():
    prs = [pr(id=1), pr(id=2, source="feature/y"), pr(id=3)]
    host = FakeHost(prs, {1: [c(PASS)], 2: [c(PASS)], 3: [c(FAIL)]})
    assert mg.run(host, dict(CFG, dry_run=False), log=lambda *_: None) == 1
    assert host.merged == [1]


def test_run_counts_a_refused_merge_as_not_merged():
    host = FakeHost([pr()], {7: [c(PASS)]}, merge_ok=False)
    assert mg.run(host, dict(CFG, dry_run=False), log=lambda *_: None) == 0
