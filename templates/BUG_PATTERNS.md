# Bug patterns — <project name> (living file)

Calibration catalogue for /appqa rounds on this project. One line per pattern; add every new bug type; record every rejection reason so it's never re-filed. Seeded with cross-project universals — prune what doesn't apply.

## Numbers & formatting
- Currency with wrong decimals or missing thousands separators; large quantities as raw floats (use compact notation in lists, full precision in detail views).
- Values that should move but don't (0.00 everywhere, frozen live prices, empty stat blocks).

## Data wiring (looks built, never populated)
- Cells/fields rendered but never mapped from the API (permanent dashes).
- Counts inconsistent with lists; aggregates inconsistent with rows.
- Notifications/emails not generated despite the surface + toggles existing.

## Copy nits
- Wrong plurals, missing spaces, double punctuation, literal HTML entities, typos, hardcoded mock data shown to users (test emails, lorem strings).

## State/visibility logic
- Role/tier/subscription gating leaks (and gate server-side — client-hidden data leaks via the network tab).
- Mode toggles (demo/live, draft/published) leaking state or executing in the wrong mode.

## Flows & journeys (test end-to-end, not per-screen)
- Destructive/paid actions without working confirmations; payment steps missing entirely.
- First-interaction/stale-closure bugs (first submit sends empty payload; inputs not reset on option switch).
- Success screens with wrong headline data; feedback prompts with wrong-direction copy.
- Dead back buttons / navigation traps.

## Third-party integrations
- Raw upstream errors leaking into themed UI; broken widgets silently blocking flows.

## Process rules learned (do not re-violate)
- Open every sub-flow, not just the sheet/menu that leads to it.
- A divergence from design may be a pending epic, not a bug — check the roadmap first.
- Re-test "missing" claims live before filing — teams ship between rounds.
- Reject-with-comment, never delete — rejections train the next round.
- <add this project's rulings here as they happen>
