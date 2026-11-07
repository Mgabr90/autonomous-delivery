#!/usr/bin/env python3
"""autodeliver merge gate (optional): completes pull requests the independent Reviewer has passed.

Runs on a schedule, outside the routines, from a repo they never write to. See README.md for why it
exists, the exact rules (decide()) and setup. Standard library only. Configuration (environment):

  MERGE_GATE_HOST        ado | github
  MERGE_GATE_TARGET      the one branch it may merge into (exact name)
  MERGE_GATE_RULES       comma list of <branch prefix>=<review marker>, e.g. "work/=ACME-REVIEW"
  MERGE_GATE_TRUSTED     comma list of identities whose verdicts count (ADO uniqueName or id; GitHub login)
  MERGE_GATE_TOKEN       ADO PAT (Code: read & write) or GitHub token (pull requests + contents: write)
  MERGE_GATE_DRY_RUN     merges only when exactly "false"; otherwise it only logs
  ADO:    MERGE_GATE_ADO_ORG (https://dev.azure.com/<org>), MERGE_GATE_ADO_PROJECT, MERGE_GATE_ADO_REPO
  GitHub: MERGE_GATE_REPO (owner/name)

Exit code 1 on a configuration error or when any API call failed, so a broken gate shows up as a
failed pipeline run; one failing PR never stops the others from being processed.
"""
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

NOTE_PREFIX = "MERGE-GATE"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


# ---------------------------------------------------------------- the decision (pure, tested)

def parse_rules(text):
    """'work/=ACME-REVIEW, ops/=OPS-REVIEW' -> [('work/', 'ACME-REVIEW'), ('ops/', 'OPS-REVIEW')]."""
    rules = []
    for part in (text or "").split(","):
        part = part.strip()
        if not part:
            continue
        prefix, sep, marker = part.partition("=")
        if not sep or not prefix.strip() or not marker.strip():
            raise ValueError(f"bad MERGE_GATE_RULES entry: {part!r} (want <branch prefix>=<marker>)")
        rules.append((prefix.strip(), marker.strip()))
    if not rules:
        raise ValueError("MERGE_GATE_RULES is empty")
    return rules


def marker_for(source, rules):
    """The review marker that governs a source branch, or None. The longest matching prefix wins."""
    matches = [(len(p), m) for p, m in rules if source.startswith(p)]
    return max(matches)[1] if matches else None


def head_verdicts(comments, marker, trusted, head):
    """The set of verdicts ('PASS'/'FAIL') trusted authors posted for this head. A verdict counts only
    when a comment's FIRST line is exactly '<marker> <40-hex sha> VERDICT: PASS|FAIL'."""
    pattern = re.compile(r"^\s*" + re.escape(marker) + r" ([0-9a-f]{40}) VERDICT: (PASS|FAIL)\b")
    found = set()
    for c in comments:
        if not trusted & {a.casefold() for a in c.get("authors", ())}:
            continue
        body = c.get("body") or ""
        m = pattern.match(body.splitlines()[0] if body.strip() else "")
        if m and m.group(1) == head:
            found.add(m.group(2))
    return found


def precheck(pr, cfg):
    """Checks that need no comments. Returns (marker, None) or (None, reason to skip)."""
    if pr.get("target") != cfg["target"]:
        return None, f"target is {pr.get('target')!r}, not {cfg['target']!r}"
    marker = marker_for(pr.get("source") or "", cfg["rules"])
    if not marker:
        return None, f"source {pr.get('source')!r} matches no Worker branch prefix"
    if pr.get("fork"):
        return None, "from a fork"
    if not pr.get("open"):
        return None, "not open"
    if pr.get("draft"):
        return None, "draft"
    if not SHA_RE.match(pr.get("head") or ""):
        return None, "head sha unknown"
    return marker, None


def decide(pr, comments, cfg):
    """Return ('merge' | 'skip', reason). pr: {target, source, fork, open, draft, mergeable, head};
    cfg: {target, rules, trusted}. mergeable is True, False or None (not computed yet).
    Any trusted FAIL for the current head blocks: every re-review is of a new head, so a PASS and a
    FAIL on one head mean two reviewers disagreed, and the FAIL's findings must be fixed first."""
    marker, reason = precheck(pr, cfg)
    if not marker:
        return "skip", reason
    head = pr["head"]
    found = head_verdicts(comments, marker, cfg["trusted"], head)
    if "FAIL" in found:
        return "skip", f"a trusted {marker} FAIL exists for head {head[:12]}"
    if "PASS" not in found:
        return "skip", f"no trusted {marker} PASS for head {head[:12]}"
    if pr.get("mergeable") is not True:
        return "skip", "not mergeable yet" if pr.get("mergeable") is None else "has conflicts or is blocked"
    return "merge", f"{marker} PASS for head {head[:12]}"


# ---------------------------------------------------------------- hosts (thin REST adapters)

class Api:
    def __init__(self, auth_header, extra_headers=None):
        self.headers = {"Authorization": auth_header, "Content-Type": "application/json",
                        "User-Agent": "autodeliver-merge-gate", **(extra_headers or {})}

    def call(self, method, url, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            raise RuntimeError(f"{method} {url.split('?')[0]} -> HTTP {e.code}: {detail}") from None


class Ado:
    """Azure DevOps Services REST 7.1. Mirrors HOST-ado.md 'Merge pinned to the sha'."""
    done_words = ("completed", "completion requested")

    def __init__(self, env, api=None):
        org = env["MERGE_GATE_ADO_ORG"].rstrip("/")
        self.base = f"{org}/{urllib.parse.quote(env['MERGE_GATE_ADO_PROJECT'])}/_apis/git/repositories/" \
                    f"{urllib.parse.quote(env['MERGE_GATE_ADO_REPO'])}"
        token = base64.b64encode((":" + env["MERGE_GATE_TOKEN"]).encode()).decode()
        self.api = api or Api("Basic " + token)

    def open_prs(self, target):
        out, skip = [], 0
        while True:
            q = urllib.parse.urlencode({"searchCriteria.status": "active",
                                        "searchCriteria.targetRefName": f"refs/heads/{target}",
                                        "$top": 100, "$skip": skip, "api-version": "7.1"})
            page = self.api.call("GET", f"{self.base}/pullrequests?{q}").get("value", [])
            out += [self.normalize(p) for p in page]
            if len(page) < 100:
                return out
            skip += 100

    @staticmethod
    def normalize(p):
        strip = lambda ref: (ref or "").replace("refs/heads/", "", 1)
        return {"id": p.get("pullRequestId"), "title": p.get("title", ""),
                "target": strip(p.get("targetRefName")), "source": strip(p.get("sourceRefName")),
                "fork": bool(p.get("forkSource")), "open": p.get("status") == "active", "draft": bool(p.get("isDraft")),
                "mergeable": {"succeeded": True, "queued": None, "notSet": None}.get(p.get("mergeStatus"), False),
                "head": ((p.get("lastMergeSourceCommit") or {}).get("commitId") or "").lower()}

    def refresh(self, pr):
        return pr  # the list call already carries mergeStatus

    def comments(self, pr):
        threads = self.api.call("GET", f"{self.base}/pullRequests/{pr['id']}/threads?api-version=7.1").get("value", [])
        out = []
        for t in threads:
            for c in t.get("comments", []):
                if c.get("isDeleted") or c.get("commentType") not in ("text", 1, None):
                    continue
                a = c.get("author") or {}
                out.append({"authors": {x for x in (a.get("uniqueName"), a.get("id")) if x},
                            "body": c.get("content", "")})
        return out

    def complete(self, pr, title):
        body = {"status": "completed", "lastMergeSourceCommit": {"commitId": pr["head"]},
                "completionOptions": {"mergeStrategy": "noFastForward", "deleteSourceBranch": False,
                                      "mergeCommitMessage": title}}
        res = self.api.call("PATCH", f"{self.base}/pullrequests/{pr['id']}?api-version=7.1", body)
        return res.get("status") == "completed"  # completion is often asynchronous: 'requested' is normal

    def note(self, pr, text):
        self.api.call("POST", f"{self.base}/pullRequests/{pr['id']}/threads?api-version=7.1",
                      {"comments": [{"parentCommentId": 0, "commentType": 1, "content": text}], "status": "closed"})


class GitHub:
    """GitHub REST. Mirrors HOST-github.md 'Merge pinned to the sha'."""
    done_words = ("merged", "merge requested")

    def __init__(self, env, api=None, wait=time.sleep):
        self.base = f"https://api.github.com/repos/{env['MERGE_GATE_REPO']}"
        self.api = api or Api("Bearer " + env["MERGE_GATE_TOKEN"],
                              {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
        self.wait = wait

    def _pages(self, path):
        out, page = [], 1
        while True:
            batch = self.api.call("GET", f"{self.base}/{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
            out += batch
            if len(batch) < 100:
                return out
            page += 1

    def open_prs(self, target):
        q = urllib.parse.urlencode({"state": "open", "base": target})
        return [self.normalize(p) for p in self._pages(f"pulls?{q}")]  # list items: mergeable unknown (None)

    @staticmethod
    def normalize(p):
        head, base = p.get("head") or {}, p.get("base") or {}
        mergeable = p.get("mergeable")
        if mergeable is True and p.get("mergeable_state") not in ("clean", "unstable", "has_hooks"):
            mergeable = False  # blocked by protection, behind, or dirty
        return {"id": p.get("number"), "title": p.get("title", ""), "target": base.get("ref"), "source": head.get("ref"),
                "fork": (head.get("repo") or {}).get("full_name") != (base.get("repo") or {}).get("full_name"),
                "open": p.get("state") == "open", "draft": bool(p.get("draft")),
                "mergeable": mergeable, "head": (head.get("sha") or "").lower()}

    def refresh(self, pr):
        """GitHub computes 'mergeable' lazily on the single-PR call; ask twice if it isn't ready."""
        for attempt in range(2):
            full = self.normalize(self.api.call("GET", f"{self.base}/pulls/{pr['id']}"))
            if full["mergeable"] is not None or attempt:
                return full
            self.wait(5)

    def comments(self, pr):
        return [{"authors": {(c.get("user") or {}).get("login") or ""}, "body": c.get("body", "")}
                for c in self._pages(f"issues/{pr['id']}/comments")]

    def complete(self, pr, title):
        res = self.api.call("PUT", f"{self.base}/pulls/{pr['id']}/merge",
                            {"sha": pr["head"], "merge_method": "merge", "commit_title": title})
        return bool(res.get("merged"))

    def note(self, pr, text):
        self.api.call("POST", f"{self.base}/issues/{pr['id']}/comments", {"body": text})


# ---------------------------------------------------------------- run

def load_config(env):
    token = env.get("MERGE_GATE_TOKEN") or ""
    if not token or token.startswith("$("):  # an unset Azure Pipelines secret arrives as the literal "$(NAME)"
        raise ValueError("MERGE_GATE_TOKEN is not set (map the secret into the step's env)")
    host = (env.get("MERGE_GATE_HOST") or "").lower()
    if host not in ("ado", "github"):
        raise ValueError("MERGE_GATE_HOST must be 'ado' or 'github'")
    target = (env.get("MERGE_GATE_TARGET") or "").strip()
    if not target or any(ch in target for ch in "*?["):
        raise ValueError("MERGE_GATE_TARGET must be one exact branch name")
    trusted = {t.strip().casefold() for t in (env.get("MERGE_GATE_TRUSTED") or "").split(",") if t.strip()}
    if not trusted:
        raise ValueError("MERGE_GATE_TRUSTED is empty: name the identity the Reviewer posts as")
    return host, {"target": target, "rules": parse_rules(env.get("MERGE_GATE_RULES")), "trusted": trusted,
                  "dry_run": env.get("MERGE_GATE_DRY_RUN", "true").strip().lower() != "false"}


def run(host, cfg, log=print):
    """Process every open PR into the target. Returns (merged, errors)."""
    merged = errors = 0
    for pr in host.open_prs(cfg["target"]):
        marker, why = precheck(pr, cfg)
        if not marker:
            if marker_for(pr.get("source") or "", cfg["rules"]):
                log(f"PR #{pr['id']}: skip ({why})")  # stay silent about people's own PRs
            continue
        try:
            comments = host.comments(pr)
            if head_verdicts(comments, marker, cfg["trusted"], pr["head"]) == {"PASS"}:
                pr = host.refresh(pr)  # the expensive state check only for PASS candidates
            action, reason = decide(pr, comments, cfg)
            log(f"PR #{pr['id']} {pr['source']} -> {pr['target']}: {action} ({reason})")
            if action != "merge":
                continue
            if cfg["dry_run"]:
                log(f"  dry run: would merge at {pr['head']}")
                continue
            done = host.complete(pr, f"Merge {pr['title']} (#{pr['id']})")
            merged += done
            host.note(pr, f"{NOTE_PREFIX} {pr['head']} {host.done_words[0 if done else 1]}: {reason}")
            log(f"  {host.done_words[0 if done else 1]} at {pr['head']}")
        except (RuntimeError, OSError) as e:  # a refused merge, a failed call or a network error: report it, carry on
            errors += 1
            log(f"  error on PR #{pr['id']}: {e}")
    log(f"done: {merged} merged, {errors} errors{' (dry run)' if cfg['dry_run'] else ''}")
    return merged, errors


def main(env=None):
    env = dict(os.environ if env is None else env)
    try:
        host_name, cfg = load_config(env)
        host = Ado(env) if host_name == "ado" else GitHub(env)
        return 1 if run(host, cfg)[1] else 0
    except (ValueError, KeyError, RuntimeError) as e:
        print(f"merge gate error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
