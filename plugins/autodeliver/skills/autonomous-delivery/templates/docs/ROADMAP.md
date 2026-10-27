# {{PROJECT}}: roadmap

Phases run top to bottom. A session takes the first row that isn't done and whose dependencies are done. A **GATE** row waits for the owner; prepare it fully, then stop.

| Phase | Scope | Depends on | Done when | Status |
|---|---|---|---|---|
| P01 | {{FIRST_PHASE_SCOPE}} | — | {{FIRST_PHASE_DONE_WHEN}} | todo |
| P02 | | P01 | | todo |
| READY | **Production readiness** (for anything that goes live): a capacity plan (measure the host under load; memory limits with headroom for neighbours; no-cost options first, an upgrade only as an owner decision); encrypted backups (to a key the server doesn't hold) with retention, an off-server copy and a proven restore test; a production-watch routine (health, error logs, backup freshness, TLS expiry, disk and memory); a dependency batch for critical and high advisories | last build phase | measurements in the runbook; restore test timed; watch prompt committed; advisories cleared with the full proof | todo |
| REHEARSAL | Run the cutover on an isolated copy of real data (counts only) | READY | timings and checks recorded; data copy kept for the gate | todo |
| GATE | {{FINAL_GATE}} (owner approval) | all build phases, READY, REHEARSAL | the evidence and rehearsed runbook are linked in DECISIONS_LOG "Hard-limit gates" | waiting |

## Follow-ups

Findings routed here from reviews and security sweeps, each with the phase that will take it:

-
