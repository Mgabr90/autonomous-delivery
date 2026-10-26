## What and why

<!-- One or two sentences. Link the issue: Closes #… -->

## Checklist

- [ ] `claude plugin validate . --strict` and `claude plugin validate plugins/autodeliver --strict` pass (CI runs them too)
- [ ] Generic: no project names, hosts, ids or secrets. New `{{PLACEHOLDERS}}` are listed in `references/config.md`
- [ ] Quality first: the gate, the hard limits and "no dependency on the user" are not weakened
- [ ] If behaviour changed: `version` bumped in `plugin.json` **and** `marketplace.json`, plus a `CHANGELOG.md` entry
- [ ] If you hit a new failure mode: a row added to the lessons table in `references/playbook.md`
