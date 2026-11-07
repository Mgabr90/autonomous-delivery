#!/usr/bin/env python3
"""autodeliver loop report: summarises .autodeliver/token_log.csv as Markdown.

Usage: loop_report.py [token_log.csv] [--loop LOOP_ID] [--since YYYY-MM-DD]

Per loop: rounds, rows, tokens by role (input, output, cache read, cache write), and wall time;
then totals by role and by model. Only the standard library; never writes anything.
"""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

TOKEN_FIELDS = ["input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"]


def num(value):
    try:
        n = float(value or 0)
    except (TypeError, ValueError):
        return 0.0
    return n if math.isfinite(n) else 0.0


def fmt(n):
    n = int(round(n))
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 10_000:
        return f"{n / 1000:.0f}K"
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def parse_args(argv):
    path, loop, since = Path(".autodeliver/token_log.csv"), None, None
    it = iter(argv)
    for arg in it:
        if arg == "--loop":
            loop = next(it, None)
        elif arg == "--since":
            since = next(it, None)
        elif arg in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        else:
            path = Path(arg)
    return path, loop, since


def is_round(value):
    return (value or "").strip().isdigit()


def main(argv):
    try:
        return run(argv)
    except Exception as exc:  # a report must never crash the caller
        print(f"Could not read the token log: {type(exc).__name__}: {exc}")
        return 0


def run(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    path, only_loop, since = parse_args(argv)
    if not path.is_file():
        print(f"No token log at {path}. The log is on by default in projects with .autodeliver/config.json "
              f"(\"token_log\": true); it fills as sessions and subagents finish.")
        return 0
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        rows = [r for r in csv.DictReader(f)
                if (not only_loop or r.get("loop_id") == only_loop)
                and (not since or (r.get("utc") or "") >= since)]
    if not rows:
        print("The token log has no rows for this filter.")
        return 0

    loops = defaultdict(list)
    for r in rows:
        loops[r.get("loop_id") or "(no loop)"].append(r)

    print(f"# Loop report\n\nSource: `{path}`, {len(rows)} rows, "
          f"{min(r.get('utc') or '' for r in rows)} to {max(r.get('utc') or '' for r in rows)}\n")
    print("Total = input + output + cache write; cache reads are listed apart because they are billed far lower.\n")

    print("## Per loop\n")
    print("| Loop | Rounds | Role | Runs | Input | Output | Cache read | Cache write | Total | Time (min) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for loop_id, lrows in sorted(loops.items(), key=lambda kv: min(r.get("utc") or "" for r in kv[1])):
        rounds = sorted({r["round"].strip() for r in lrows if is_round(r.get("round"))}, key=int)
        by_role = defaultdict(lambda: defaultdict(float))
        for r in lrows:
            d = by_role[r.get("role") or "?"]
            d["runs"] += 1
            d["duration_s"] += num(r.get("duration_s"))
            for k in TOKEN_FIELDS:
                d[k] += num(r.get(k))
        first = True
        for role, d in sorted(by_role.items()):
            total = d["input_tokens"] + d["output_tokens"] + d["cache_write_tokens"]
            print(f"| {loop_id if first else ''} | {len(rounds) if first else ''} | {role} | {int(d['runs'])} | "
                  f"{fmt(d['input_tokens'])} | {fmt(d['output_tokens'])} | {fmt(d['cache_read_tokens'])} | "
                  f"{fmt(d['cache_write_tokens'])} | {fmt(total)} | {d['duration_s'] / 60:.1f} |")
            first = False

    for key, title in (("role", "By role"), ("model", "By model")):
        agg = defaultdict(lambda: defaultdict(float))
        for r in rows:
            d = agg[r.get(key) or "?"]
            d["runs"] += 1
            for k in TOKEN_FIELDS:
                d[k] += num(r.get(k))
        grand = sum(d["input_tokens"] + d["output_tokens"] + d["cache_write_tokens"] for d in agg.values()) or 1
        print(f"\n## {title}\n")
        print(f"| {key.capitalize()} | Runs | Total | Share | Cache read |")
        print("|---|---|---|---|---|")
        for name, d in sorted(agg.items(), key=lambda kv: -(kv[1]["input_tokens"] + kv[1]["output_tokens"] + kv[1]["cache_write_tokens"])):
            total = d["input_tokens"] + d["output_tokens"] + d["cache_write_tokens"]
            print(f"| {name} | {int(d['runs'])} | {fmt(total)} | {100 * total / grand:.0f}% | {fmt(d['cache_read_tokens'])} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
