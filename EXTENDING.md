# Extending appqa

The engine is deliberately hackable: one markdown skill + one Python script + per-project config. Everything below is fair game for your team to change — the only design rule worth keeping is the **engine/config split**.

## The one rule: engine vs project

- **Engine** (`skills/appqa/SKILL.md`): behaviour that's true for *every* project — the checks, the gates, the evidence loop, the ticket shape.
- **Project** (`qa.config.md` + your `BUG_PATTERNS.md`): everything that's true for *your app only* — URLs, auth, trackers, rulings, quirks.

When you're about to hard-code something into the skill, ask: would this be true for a different app? If not, it goes in the config or the patterns file. This keeps your fork mergeable with upstream improvements.

## Common extensions

### Add team-specific QA rules
Don't touch the skill — append to your project's `BUG_PATTERNS.md`. The skill reads it every round. Rulings ("our empty states always show an illustration", "we never use browser alerts") belong there; ten lines of patterns beat a fork.

### Add a connector (new tracker, comms, analytics…)
The skill talks to tools through whatever MCP connectors the operator has attached. To route output somewhere new (Slack summaries, Jira, a test-rail):
1. Connect the MCP in Claude Code (`/mcp`).
2. Add a section to your `qa.config.md` describing what to send there (e.g. "after each round, post the wrap-up summary to Slack #qa via the Slack connector").
3. If it should be default behaviour for all your projects, add one line to the skill's wrap-up section.

### Change the ticket format
The body template lives in the skill (section 4). Edit it — but keep the fix-prompt's first line (the self-referencing "read this ticket first" context line); dev-side AIs rely on it to self-serve context.

### New evidence styles
`tools/gen_evidence.py` is ~90 lines. It takes a JSON config of panels + annotation boxes and emits an annotated HTML page. Add annotation types (circles, diff-highlights, numbered steps) by extending `svg_annos()`. Whatever you add, keep the **mandatory render-verify loop** — generate, render headless, look at it, confirm every box lands before publishing. That loop is why the evidence is trustworthy.

### New triggers / automations
Rounds are just prompts, so anything that can prompt Claude Code can trigger QA:
- **Scheduled tasks** (see README recipes) — poll the board, react to statuses.
- **CI hooks** — a deploy pipeline step that opens a Claude Code run with `/appqa smoke-test the staging deploy`.
- **Chat-ops** — a Slack workflow that files a "run QA on X" request wherever your operator will see it.

### Multiple apps / monorepos
One `qa.config.md` per app (e.g. `apps/web/qa.config.md`, `apps/admin/qa.config.md`). Invoke with the path: `/appqa using apps/admin/qa.config.md`.

### Harden it for your stack
First round on a new app always discovers quirks (auth flows, click-immune components, headless crashers). The skill appends them to your config's known-quirks section — review that section after round one and correct anything it got wrong. It's the difference between a demo and a dependable teammate.

## Contributing upstream

If an improvement is engine-grade (true for any project), PR it back. Good candidates: new evidence annotation types, better browser fallbacks, tracker adapters, smarter dedupe. Project-specific rules and configs stay in your repos.
