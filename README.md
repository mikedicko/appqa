# appqa — AI QA rounds for any web app

A Claude Code skill that drives your live web app like a real user, plays with every flow, compares what it finds against your source of truth (Figma designs **or** written specs in Notion), and either **files annotated bug tickets** to your tracker or **fixes the bugs in-session** — with screenshot evidence, red/green annotations that go through a verify-before-publish loop, dedup against your existing tickets and roadmap, and a per-project learning file that gets sharper every round.

**Engine vs config:** this repo is the engine (skill + evidence tooling + templates). Everything project-specific — app URL, auth, where designs live, where bugs go, what's intentionally unfinished — lives in a `qa.config.md` **inside each project's own repo**. One engine, any number of projects.

---

## Setup (per operator, ~5 min)

```bash
git clone https://github.com/mikedicko/appqa.git ~/appqa
mkdir -p ~/.claude/skills
ln -s ~/appqa/skills/appqa ~/.claude/skills/appqa
```

Connect the MCP servers your project uses in Claude Code (`/mcp`): Notion and/or Linear for the tracker, the official Figma MCP if designs live there, GitHub for code refs.

## Onboarding a project (~10 min, once)

1. Copy `templates/qa.config.md` into the project repo root as `qa.config.md` and fill it in (app URL + auth recipe, source of truth, tracker mapping, report-vs-fix mode, evidence hosting, intentionally-unfinished list).
   - Or skip this: run `/appqa` in the project and the skill will interview you and scaffold the config itself.
2. Copy `templates/BUG_PATTERNS.md` to the path you named in the config — this becomes the project's learning file.
3. Decide evidence hosting. Recommended: an `evidence/` folder in a repo the whole team can read (GitHub renders PNGs — zero sharing friction).
4. **Figma projects: register your design sections** (see below) so the skill knows exactly which frames are gospel.

Then, in Claude Code from the project directory:

```
/appqa
```

Give it a scope ("full round", "checkout flow only", "re-test the QA column") and let it run.

## Adding Figma designs (do this the right way)

The skill needs stable references to your design **sections** — not the whole file, not individual elements.

1. Open your design file in **Figma → Dev Mode**.
2. **Select a section** (e.g. "Wallet", "Onboarding", "Settings") on the canvas — a section, not the page and not a single component.
3. In the right-hand panel, copy the **MCP link** for that selection.
4. Paste the link into Claude Code and say what it is (e.g. "this is the Checkout section — save it") — Claude saves it to the project's frame map / memory so every future round can pull those frames directly.
5. Repeat per section of the app.

**Why sections, specifically:**
- ❌ **Full page/file links** are too big — the Figma MCP times out trying to enumerate them, and the skill can't tell which part is relevant.
- ❌ **Individual element/component links** are too granular — components in a library aren't necessarily what's shipped; **page designs are gospel, component sets are not**.
- ✅ **Section links** are the sweet spot: small enough to fetch, complete enough to compare a whole screen/flow against.

## What a round produces

- **Report mode:** tickets in your tracker — plain-English issue → expected → a self-contained fix prompt for the assigned dev's AI (opens with "read this ticket and follow its links") → acceptance bullets → links (annotated screenshot, design/spec, related epic, repro path). Deduped against existing tickets AND your roadmap — it won't file what a planned epic already owns.
- **Fix mode:** root-caused fixes committed atomically per bug, each verified live in the app before commit, plus a list of anything needing a product decision (asked, not guessed) or out of scope (filed instead).
- **Evidence:** annotated full-page screenshots (green box = expected, red box = issue) that pass a mandatory render-verify loop before publishing — no mislabeled arrows.
- **Learning:** every new bug type and every rejected ticket's reason lands in the project's patterns file, so the next round hunts for what YOUR team cares about.

## House rules baked into the engine

- Page designs are gospel; Figma component sets are not. In Notion mode, the spec pages are gospel.
- Re-test "missing" claims live before filing — teams ship between rounds.
- Never file what the roadmap already owns — cross-reference epics; banner with "defer to epic" when in doubt.
- Reject-with-comment (never delete) — rejections train the next round.
- Gate visibility server-side: client-hidden data still leaks via the network tab.
- No real-money / destructive actions unless the project config explicitly allows them.
