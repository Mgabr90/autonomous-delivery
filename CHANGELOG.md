# Changelog

## 0.1.0 (2026-10-26)

First public release.
- **Commands:** `/autodeliver:init`, `/autodeliver:loop`, `/autodeliver:status` and `/autodeliver:doctor`.
- **Agents:** `delivery-reviewer`, `delivery-fixer`, `visual-checker`, `translation-reviewer` and `usage-inspector`.
- **Skill:** `autonomous-delivery`, with the playbook, the profiles (software, docs, data, infra, migration, research), and config and cloud-setup references.
- **Templates:** the five cloud routine prompts (Worker, Reviewer, Fixer, Usage inspector, Security sweep), the charter docs, and the staging ops gate.
- **Token log:** records token usage per role and round. It is on by default in new configs; set `"token_log": false` to turn it off.
