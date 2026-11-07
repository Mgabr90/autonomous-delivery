# autodeliver

The plugin behind [Autonomous Delivery](../../README.md).

Install:

```
/plugin install autodeliver --marketplace Mgabr90/autonomous-delivery
```

| Component | Files |
|---|---|
| Commands | `commands/init.md`, `loop.md`, `status.md`, `doctor.md` |
| Agents | `agents/delivery-reviewer.md`, `delivery-fixer.md`, `design-reviewer.md`, `researcher.md`, `visual-checker.md`, `translation-reviewer.md`, `usage-inspector.md` |
| Skill | `skills/autonomous-delivery/`: playbook, profiles, config, cloud setup, templates |
| Third-party licences | `licenses/EGM-LICENSE.txt`: `design-reviewer` is adapted from Google's [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model) (Apache 2.0) |
| Hook | `hooks/hooks.json` and `scripts/token_log.py`: the token log, active in projects with an `.autodeliver/config.json` (on by default; `"token_log": false` turns it off) |
