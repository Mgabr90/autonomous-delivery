#!/usr/bin/env python3
"""Token log for /autodeliver (Stop and SubagentStop hooks).

Active in every project that has an .autodeliver/config.json, unless that config sets "token_log": false
(projects without the config are never touched). It appends
one CSV row per finished turn (main session) or subagent run, with token counts summed from the transcript lines
added since the previous row. Any error exits 0 silently: a hook must never block or disturb a session.
"""
import csv, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ["utc", "session_id", "loop_id", "round", "role", "model", "input_tokens", "output_tokens",
          "cache_read_tokens", "cache_write_tokens", "assistant_turns", "duration_s", "event"]


def find_config(start: Path):
    for d in [start, *start.parents]:
        cfg = d / ".autodeliver" / "config.json"
        if cfg.is_file():
            return d, json.loads(cfg.read_text(encoding="utf-8"))
        if (d / ".git").exists():
            return None, None
    return None, None


def summarize(path: Path, offset: int):
    tot = {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0}
    models, turns, first, last = set(), 0, None, None
    with path.open("rb") as f:
        f.seek(offset)
        data = f.read()
        end = offset + len(data)
    for raw in data.splitlines():
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        ts = d.get("timestamp")
        if ts:
            first = first or ts
            last = ts
        m = d.get("message")
        if not isinstance(m, dict) or not isinstance(m.get("usage"), dict):
            continue
        u = m["usage"]
        turns += 1
        tot["input_tokens"] += int(u.get("input_tokens") or 0)
        tot["output_tokens"] += int(u.get("output_tokens") or 0)
        tot["cache_read_tokens"] += int(u.get("cache_read_input_tokens") or 0)
        tot["cache_write_tokens"] += int(u.get("cache_creation_input_tokens") or 0)
        if m.get("model"):
            models.add(m["model"])
    dur = ""
    try:
        if first and last:
            p = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
            dur = round((p(last) - p(first)).total_seconds(), 1)
    except ValueError:
        pass
    return tot, ",".join(sorted(models)), turns, dur, end


def main():
    event = json.loads(sys.stdin.read() or "{}")
    root, cfg = find_config(Path(event.get("cwd") or os.getcwd()))
    if not cfg or cfg.get("token_log", True) is False:
        return
    name = event.get("hook_event_name", "")
    if name == "SubagentStop":
        transcript, role = event.get("agent_transcript_path"), event.get("agent_type") or "subagent"
    else:
        transcript, role = event.get("transcript_path"), "main"
    if not transcript or not Path(transcript).is_file():
        return
    state_path = root / ".autodeliver" / "token_log.state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    tot, model, turns, dur, end = summarize(Path(transcript), int(state.get(transcript, 0)))
    state[transcript] = end
    state_path.write_text(json.dumps(state), encoding="utf-8")
    if turns == 0:
        return
    loop = {}
    try:
        loop = json.loads((root / ".autodeliver" / "loop_state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    out = root / cfg.get("token_log_path", ".autodeliver/token_log.csv")
    new = not out.exists()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "session_id": event.get("session_id", ""),
                    "loop_id": loop.get("loop_id", ""), "round": loop.get("round", ""), "role": role, "model": model,
                    **tot, "assistant_turns": turns, "duration_s": dur, "event": name})


if __name__ == "__main__":
    try:
        main()
    except Exception:  # never disturb the session
        pass
    sys.exit(0)
