# Governance

This document defines how the quota-scout project is governed.

## 1. Project role: Benevolent Dictator For Life (BDFL)

quota-scout is governed by a **BDFL model**. The BDFL is **David
([@newdeme](https://github.com/newdeme))**, the project founder.

The BDFL:

- Has final decision authority on all disputes, including scope, roadmap,
  compliance, and governance changes
- Owns the compliance red lines (Section 5) — these are non-negotiable
- May delegate day-to-day review to Maintainers, but may veto any merged
  change and revert it with cause

This model is chosen deliberately at project inception because the project's
core value is **data trustworthiness**, which requires a single accountable
final arbiter, especially for provider-compliance judgments.

## 2. Contributor ladder

| Level | Role | How to reach it | Powers |
|---|---|---|---|
| L0 | Bystander | — | Open issues, participate in discussions |
| L1 | Contributor | 1 merged PR | Listed in release notes / data attribution |
| L2 | Regular | ≥ 3 merged PRs | May be assigned to pending channel-report issues |
| L3 | Domain Reviewer | Nominated by BDFL + passing a small review task | Reviews PRs in their domain (channel reports, bad_model fixes, docs, i18n) |
| L4 | Maintainer | Very few, appointed by BDFL | Full review/merge rights |

Rules:

- Promotions are reviewed by the BDFL **monthly, in batch** (low ceremony).
- Inactive members become **dormant, never removed**; their attribution is
  preserved permanently.
- L3/L4 roles can be suspended by the BDFL for violations of Section 5.
- The first 10 contributors with a merged PR receive a permanent
  **founding contributor** mention.

## 3. Decision process

1. **Normal changes** (docs, new channel reports with sources, bad_model
   fixes, i18n): PR reviewed by any L3+ reviewer or the BDFL.
2. **Schema changes** (`data/channels.json` structure, status semantics):
   require BDFL review — enforced via `CODEOWNERS`.
3. **Governance / compliance / roadmap changes**: BDFL decides after open
   discussion; decisions are recorded in the repository (issue or PR body).

## 4. Attribution and credit

- Channel entries in `data/channels.json` may carry an optional
  `contributors` field. Contributed channels render with contributor names in
  the README status table and release notes.
- Accepted ROADMAP proposals credit the proposer with a link.

## 5. Compliance red lines (non-negotiable, BDFL-owned)

The following are rejected on sight, regardless of author:

1. Only **official public API endpoints** of providers; standard personal API
   keys. Provider-plan-specific keys and reverse-engineered web-to-API or
   scraping approaches are rejected.
2. No advertising, affiliate links, or sponsored placements — the project
   must stay free of commercial influence to remain trustworthy.
3. No tracking, analytics beacons, or user data collection.

## 6. Contribution Licensing (DCO)

Contributions are accepted under the
[Developer Certificate of Origin (DCO)](https://developercertificate.org/):
by submitting a PR you certify you have the right to submit it under the
project's licenses. Sign each commit with `git commit -s` (adds a
`Signed-off-by` line). No CLA is required; no copyright assignment happens.

## 7. Changes to this document

Amendments require a PR tagged `governance` and BDFL approval. The change
history lives in git history.
