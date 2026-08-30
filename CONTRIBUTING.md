# Contributing to quota-scout

Thank you for helping keep the free-tier radar honest. Please read this once
before your first PR — it is short on purpose.

## Ways to contribute

Good first issues are labeled `good first issue`. Typical areas:

1. **Channel reports** — new free-tier providers or fixes to existing entries
2. **bad_model fixes** — dead model IDs in `data/channels.json`
3. **CN prober script** — probing script contributed by the community
4. **Docs & i18n** — README translations, contributor onboarding docs
5. **Tests & CI hardening**

## The one rule that matters: channels

quota-scout's entire value is trustworthy data. For anything touching
`data/channels.json`:

**Allowed**

- Official public API endpoints only (the provider's own documented domain)
- Standard personal API keys, or anonymous public endpoints
- Every claim about free tier backed by an **official source link**
  (pricing page / docs) in the PR description

**Rejected on sight**

- Reverse-engineered web-to-API endpoints, scraping, session hijacking
- Plan- or campaign-specific keys (e.g. a key tied to a paid subscription
  plan — those endpoints behave differently and poison the data)
- Vendors that cannot be verified from an official source
- "It works for me" without a testable command

**Status semantics**: do not change the meaning of existing statuses
(`ok` / `anon_ok` / `rate_limited` / `no_key` / `auth_invalid` /
`bad_model` / `quota_out` / `down` / `retired`) — that is a schema change
owned by the maintainer (see GOVERNANCE.md and CODEOWNERS).

## Testing your channel report

```bash
# Probe just your channel (does not overwrite other channels' results):
python3 scripts/probe.py --only <channel_id>

# Re-render README/table/badges from data:
python3 scripts/render.py
```

Paste the command output (with any key redacted) into your PR.

## Commit sign-off (DCO)

Sign every commit — this certifies you may submit it under the project
licenses (no CLA, no copyright assignment):

```bash
git commit -s
```

If you forgot, amend: `git commit -s --amend --no-edit`.

## What happens after you open a PR

- Reviews are batched; expect a response within about a week (this is a
  solo-maintainer project worked on in limited time windows).
- Your merged channel entries credit you via the optional `contributors`
  field — attribution travels with the data.

## Code style

- `probe.py` stays standard-library-only (no third-party deps)
- Don't hand-edit CI-generated files (`results.json`, `history.jsonl`,
  `badge-*.json`)
- Don't commit real keys; `.env` is git-ignored, use `.env.example`

## License

By contributing you agree your contributions are licensed under
Apache-2.0 (code) and CC BY 4.0 (data), per the DCO above.
