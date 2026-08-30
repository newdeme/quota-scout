# Security Policy

## Supported versions

This project is a data-pipeline repository. Only the latest commit on
`main` is supported.

## Reporting a vulnerability

**Do NOT open a public issue for security reports.**

Use GitHub's private vulnerability reporting:
`https://github.com/newdeme/quota-scout/security/advisories/new`

Or contact the maintainer via GitHub (@newdeme) privately.

You will get a response within 7 days. If confirmed, a fix will be released
and you will be credited (unless you prefer otherwise).

## Scope

In scope:

- Secret leakage via workflows, scripts, or committed files
- Injection into the rendering pipeline (`scripts/render.py`,
  `scripts/probe.py`) via repository data
- Workflow privilege issues (e.g. pull_request triggers with secrets access)
- Anything that could turn the published data files into an attack vector
  for downstream consumers

Out of scope:

- Availability of third-party provider endpoints (that is what the project
  *reports on*, not what it operates)
- Rate limiting or blocking by providers

## Design invariants (please check any PR against these)

1. Secrets enter workflows only via `env:` from GitHub Secrets; never echoed,
   never written to files, never interpolated into `run:` strings.
2. `scripts/render.py` performs only local file rendering: no network calls,
   no subprocess, no `eval`/`exec`.
3. `probe.py` makes outbound HTTPS requests only to endpoints listed in
   `data/channels.json`.
4. User-controlled input never reaches shell execution; workflows do not run
   on untrusted PR code with secrets available.
