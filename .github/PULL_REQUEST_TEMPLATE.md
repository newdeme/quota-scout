<!--
  Before submitting:
  - Channel reports MUST include an official source link (see checklist below)
  - Reverse-engineered web-to-API / scraping approaches are rejected
  - Sign your commit: git commit -s (DCO, see CONTRIBUTING.md)
-->

## What does this PR change?

<!-- Feature / channel report / bug fix / docs / i18n -->

## Verification (mandatory)

**For channel report PRs (new or modified channel), ALL of these are required:**

- [ ] Endpoint is an **official public** URL (paste it below)
- [ ] I tested it myself with a standard personal key / anonymous access and it returned the documented status
- [ ] Source of the free-tier info (official pricing/docs page URL):
- [ ] `free_tier` / `free_tier_en` fields follow the existing style in `data/channels.json`

Paste your test evidence (command + status code / truncated response, no keys!):

```
<paste here — REDACT any API key or token>
```

**For other PRs**, describe how you verified:

- [ ] Ran locally (command + result): 

## Self-check

- [ ] No API keys, tokens, or personal information committed
- [ ] `git commit -s` applied (DCO)
- [ ] Did not hand-edit files under `data/` that are CI-generated (`results.json`, `history.jsonl`, `badge-*.json`)
