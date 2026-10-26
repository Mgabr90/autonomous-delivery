# autodeliver

The plugin behind [Autonomous Delivery](../../README.md).

Install:

```
/plugin install autodeliver --marketplace Mgabr90/autonomous-delivery
```

| Component | Files |
|---|---|
| Commands | `commands/init.md`, `loop.md`, `status.md`, `doctor.md` |
| Agents | `agents/delivery-reviewer.md`, `delivery-fixer.md`, `visual-checker.md`, `translation-reviewer.md`, `usage-inspector.md` |
| Skill | `skills/autonomous-delivery/`: playbook, profiles, config, cloud setup, templates |
| Hook | `hooks/hooks.json` and `scripts/token_log.py`: the token log, active in projects with an `.autodeliver/config.json` (on by default; `"token_log": false` turns it off) |
