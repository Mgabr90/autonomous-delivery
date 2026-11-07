# {{PROJECT}}: system (living doc)

What is built **now**, as it stands on `{{MAIN}}`. It is not a plan and not a history: each phase that changes the shape of the system updates this file in the same PR, and the weekly sweep checks it against the code for drift. New sessions and design reviewers read it to learn the system without reading every file.

Keep it short and at the level of components, interfaces and data flow. Code-level detail belongs in the code.

## Purpose

{{GOAL}}

## Components

| Component | Where (paths) | Does | Talks to |
|---|---|---|---|
| | | | |

## Data

Stores, main entities and their key fields, who writes each one, and what holds personal data.

## Outside services

Each service, what it is used for, and what happens when it is absent (fail safe).

## Key decisions

The decisions a newcomer would otherwise get wrong, each linked to its ruling in `{{DECISIONS}}` or a phase ledger.

## Not built yet

Pointers to roadmap rows, so that readers don't mistake a gap for drift.
