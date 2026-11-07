#!/usr/bin/env python3
"""autodeliver merge gate: completes pull requests that the independent Reviewer has passed.

Cloud routines can't reliably merge their own PRs: the auto-mode permission check can refuse a
routine completing a PR it is part of ("Merge Without Review", "Self-Approval"), even after an
independent reviewer posted PASS. This gate runs OUTSIDE the routines, on a schedule (an Azure
Pipeline or a GitHub Actions workflow in a repo the routines never write to). It merges a PR only
when every rule in decide() holds, pinned to the reviewed head sha.

Standard library only. Configuration comes from environment variables (see README.md):

  MERGE_GATE_HOST        ado | github
  MERGE_GATE_TARGET      target branch name, e.g. main (exact match; never a pattern)
  MERGE_GATE_RULES       comma list of <branch prefix>=<review marker>, e.g. "work/=ACME-REVIEW"
  MERGE_GATE_TRUSTED     comma list of identities whose markers count (ADO uniqueName or id; GitHub login)
  MERGE_GATE_TOKEN       ADO PAT (Code: read & write) or GitHub token (pull requests + contents: write)
  MERGE_GATE_DRY_RUN     merges only when exactly "false"; anything else (or unset) is a dry run
  ADO:    MERGE_GATE_ADO_ORG (https://dev.azure.com/<org>), MERGE_GATE_ADO_PROJECT, MERGE_GATE_ADO_REPO
  GitHub: MERGE_GATE_REPO (owner/name)

Exit code: 0 when the run completed (whatever it decided), 1 on a configuration or API error,
so a broken gate shows up as a failed pipeline run instead of silently merging nothing.
"""
import base64
import json
import os
import re
import sys
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
    best = None
    for prefix, marker in rules:
        if source.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, marker)
    return best[1] if best else None


def verdicts(comments, marker, trusted):
    """Review verdicts in time order: [(time, id, sha, verdict)], only from trusted authors and
    only when the comment's FIRST line is exactly '<marker> <40-hex sha> VERDICT: PASS|FAIL'."""
    pattern = re.compile(r"^\s*" + re.escape(marker) + r" ([0-9a-f]{40}) VERDICT: (PASS|FAIL)\b")
    out = []
    for c in comments:
        if c.get("author") not in trusted:
            continue
        first = (c.get("body") or "").splitlines()[0] if (c.get("body") or "").strip() else ""
        m = pattern.match(first)
        if m:
            out.append((c.get("time") or "", str(c.get("id") or ""), m.group(1), m.group(2)))
    out.sort()
    return out


def decide(pr, comments, cfg):
    """Return ('merge' | 'skip', reason). pr: {target, source, open, draft, mergeable, head};
    cfg: {target, rules, trusted}. mergeable is True, False or None (not computed yet)."""
    if pr.get("target") != cfg["target"]:
        return "skip", f"target is {pr.get('target')!r}, not {cfg['target']!r}"
    marker = marker_for(pr.get("source") or "", cfg["rules"])
    if not marker:
        return "skip", f"source {pr.get('source')!r} matches no Worker branch prefix"
    if not pr.get("open"):
        return "skip", "not open"
    if pr.get("draft"):
        return "skip", "draft"
    head = (pr.get("head") or "").lower()
    if not SHA_RE.match(head):
        return "skip", "head sha unknown"
    if pr.get("mergeable") is not True:
        return "skip", "not mergeable yet" if pr.get("mergeable") is None else "has conflicts or is blocked"
    current = [v for v in verdicts(comments, marker, cfg["trusted"]) if v[2] == head]
    if not current:
        return "skip", f"no trusted {marker} verdict for head {head[:12]}"
    if current[-1][3] != "PASS":
        return "skip", f"latest {marker} verdict for head {head[:12]} is FAIL"
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
    """Azure DevOps Services REST 7.1."""

    def __init__(self, env, api=None):
        org = env["MERGE_GATE_ADO_ORG"].rstrip("/")
        self.base = f"{org}/{urllib.parse.quote(env['MERGE_GATE_ADO_PROJECT'])}/_apis/git/repositories/" \
                    f"{urllib.parse.quote(env['MERGE_GATE_ADO_REPO'])}"
        token = base64.b64encode((":" + env["MERGE_GATE_TOKEN"]).encode()).decode()
        self.api = api or Api("Basic " + token)

    def open_prs(self, target):
        q = urllib.parse.urlencode({"searchCriteria.status": "active",
                                    "searchCriteria.targetRefName": f"refs/heads/{target}",
                                    "$top": 200, "api-version": "7.1"})
        return [self.normalize(p) for p in self.api.call("GET", f"{self.base}/pullrequests?{q}").get("value", [])]

    @staticmethod
    def normalize(p):
        strip = lambda ref: (ref or "").replace("refs/heads/", "", 1)
        return {"id": p.get("pullRequestId"), "title": p.get("title", ""),
                "target": strip(p.get("targetRefName")), "source": strip(p.get("sourceRefName")),
                "open": p.get("status") == "active", "draft": bool(p.get("isDraft")),
                "mergeable": {"succeeded": True, "queued": None, "notSet": None}.get(p.get("mergeStatus"), False),
                "head": ((p.get("lastMergeSourceCommit") or {}).get("commitId") or "").lower()}

    def comments(self, pr):
        threads = self.api.call("GET", f"{self.base}/pullRequests/{pr['id']}/threads?api-version=7.1").get("value", [])
        out = []
        for t in threads:
            for c in t.get("comments", []):
                if c.get("isDeleted") or c.get("commentType") not in ("text", 1, None):
                    continue
                a = c.get("author") or {}
                for who in {a.get("uniqueName"), a.get("id")} - {None}:
                    out.append({"author": who, "body": c.get("content", ""),
                                "time": c.get("publishedDate", ""), "id": f"{t.get('id')}.{c.get('id')}"})
        return out

    def merge(self, pr, reason):
        body = {"status": "completed", "lastMergeSourceCommit": {"commitId": pr["head"]},
                "completionOptions": {"mergeStrategy": "noFastForward", "deleteSourceBranch": False,
                                      "mergeCommitMessage": f"Merge {pr['title']} (#{pr['id']})"}}
        self.api.call("PATCH", f"{self.base}/pullrequests/{pr['id']}?api-version=7.1", body)
        back = self.api.call("GET", f"{self.base}/pullrequests/{pr['id']}?api-version=7.1")
        done = back.get("status") == "completed"
        self.api.call("POST", f"{self.base}/pullRequests/{pr['id']}/threads?api-version=7.1",
                      {"comments": [{"parentCommentId": 0, "commentType": 1,
                                     "content": f"{NOTE_PREFIX} {pr['head']} {'completed' if done else 'completion requested'}: {reason}"}],
                       "status": "closed"})
        return done


class GitHub:
    def __init__(self, env, api=None):
        self.repo = env["MERGE_GATE_REPO"]
        self.base = f"https://api.github.com/repos/{self.repo}"
        self.api = api or Api("Bearer " + env["MERGE_GATE_TOKEN"],
                              {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})

    def open_prs(self, target):
        q = urllib.parse.urlencode({"state": "open", "base": target, "per_page": 100})
        out = []
        for p in self.api.call("GET", f"{self.base}/pulls?{q}"):
            full = self.api.call("GET", f"{self.base}/pulls/{p['number']}")  # 'mergeable' is only on the single-PR call
            out.append(self.normalize(full))
        return out

    @staticmethod
    def normalize(p):
        state = p.get("mergeable_state")
        mergeable = p.get("mergeable")
        if mergeable is True and state not in ("clean", "unstable", "has_hooks"):
            mergeable = False  # blocked by protection, behind, or dirty
        return {"id": p.get("number"), "title": p.get("title", ""),
                "target": (p.get("base") or {}).get("ref"), "source": (p.get("head") or {}).get("ref"),
                "open": p.get("state") == "open", "draft": bool(p.get("draft")),
                "mergeable": mergeable, "head": ((p.get("head") or {}).get("sha") or "").lower()}

    def comments(self, pr):
        out, page = [], 1
        while True:
            batch = self.api.call("GET", f"{self.base}/issues/{pr['id']}/comments?per_page=100&page={page}")
            for c in batch:
                out.append({"author": (c.get("user") or {}).get("login"), "body": c.get("body", ""),
                            "time": c.get("created_at", ""), "id": c.get("id")})
            if len(batch) < 100:
                return out
            page += 1

    def merge(self, pr, reason):
        res = self.api.call("PUT", f"{self.base}/pulls/{pr['id']}/merge",
                            {"sha": pr["head"], "merge_method": "merge",
                             "commit_title": f"Merge {pr['title']} (#{pr['id']})"})
        done = bool(res.get("merged"))
        self.api.call("POST", f"{self.base}/issues/{pr['id']}/comments",
                      {"body": f"{NOTE_PREFIX} {pr['head']} {'merged' if done else 'merge refused'}: {reason}"})
        return done


# ---------------------------------------------------------------- run

def load_config(env):
    token = env.get("MERGE_GATE_TOKEN") or env.get("MERGE_GATE_PAT") or ""
    if not token or token.startswith("$("):  # an unset Azure Pipelines secret arrives as the literal "$(NAME)"
        raise ValueError("MERGE_GATE_TOKEN is not set (map the secret into the step's env)")
    env = dict(env, MERGE_GATE_TOKEN=token)
    host = (env.get("MERGE_GATE_HOST") or "").lower()
    if host not in ("ado", "github"):
        raise ValueError("MERGE_GATE_HOST must be 'ado' or 'github'")
    target = (env.get("MERGE_GATE_TARGET") or "").strip()
    if not target or any(ch in target for ch in "*?["):
        raise ValueError("MERGE_GATE_TARGET must be one exact branch name")
    trusted = {t.strip() for t in (env.get("MERGE_GATE_TRUSTED") or "").split(",") if t.strip()}
    if not trusted:
        raise ValueError("MERGE_GATE_TRUSTED is empty: name the identity the routines post as")
    cfg = {"target": target, "rules": parse_rules(env.get("MERGE_GATE_RULES")), "trusted": trusted,
           "dry_run": env.get("MERGE_GATE_DRY_RUN", "true").strip().lower() != "false"}
    return host, env, cfg


def run(host_client, cfg, log=print):
    merged = 0
    for pr in host_client.open_prs(cfg["target"]):
        if not marker_for(pr.get("source") or "", cfg["rules"]):
            continue  # not a Worker PR: say nothing about people's own PRs
        action, reason = decide(pr, host_client.comments(pr), cfg)
        log(f"PR #{pr['id']} {pr['source']} -> {pr['target']}: {action} ({reason})")
        if action == "merge":
            if cfg["dry_run"]:
                log(f"  dry run: would merge at {pr['head']}")
            elif host_client.merge(pr, reason):
                merged += 1
                log(f"  merged at {pr['head']}")
            else:
                log("  the host refused the merge (head moved, policy or conflict); will retry next run")
    log(f"done: {merged} merged{' (dry run)' if cfg['dry_run'] else ''}")
    return merged


def main(env=None):
    env = dict(os.environ if env is None else env)
    try:
        host, env, cfg = load_config(env)
        client = Ado(env) if host == "ado" else GitHub(env)
        run(client, cfg)
        return 0
    except (ValueError, KeyError, RuntimeError) as e:
        print(f"merge gate error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
