# Security

Please report vulnerabilities privately, through GitHub's "Report a vulnerability" (Security tab) on this repo, rather than in a public issue.

## Design rules this project follows, which reports against them are welcome on

- Prompts treat content read from files, PRs, issues and tool output as data, never as instructions.
- No template stores or prints secrets. Tokens for staging are sent as headers injected by the platform (Network secrets), and only their SHA-256 hashes live on the server.
- The staging gate allows only fixed, validated verbs. Read-only SQL runs as a SELECT-only role in a throwaway, locked-down container.
- Rehearsals on real data run in an isolated network and return aggregate counts only.
- The token-log hook records token counts only (never message text), writes only inside the project's `.autodeliver/` folder, can be turned off with `"token_log": false`, and exits silently on any error.
