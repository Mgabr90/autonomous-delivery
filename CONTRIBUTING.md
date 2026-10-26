# Contributing

Thanks for helping. This project runs on its own method: improvements go through review like any other work.

1. **Open an issue first** for anything larger than a typo. Say what problem it solves and which profile or mode it affects.
2. **Keep it generic.** No project-specific names, hosts, ids or secrets in templates or docs. Use `{{PLACEHOLDERS}}`, and document new ones in `references/config.md`.
3. **Quality first.** Changes must not weaken the gate:
   - PASS needs zero Blocking, zero Should-fix and the full proof;
   - the hard limits stay;
   - nothing is parked for the user.
4. **Validate** before you open a PR:
   ```
   claude plugin validate . --strict
   claude plugin validate plugins/autodeliver --strict
   python -m py_compile plugins/autodeliver/scripts/token_log.py
   ```
5. **Lessons learned:** if you hit a new failure mode in real use, add a row to the lessons table in `references/playbook.md`, describing what happened and the rule that prevents it.
6. **Versioning:** bump `version` in both `plugin.json` and `marketplace.json`, and add a `CHANGELOG.md` entry.

Maintainers: @Mgabr90 and @Ahmed0623.
