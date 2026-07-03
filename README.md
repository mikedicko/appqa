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

### Connect your MCP servers (required before the first round)

The skill posts bugs to your tracker and reads your designs through MCP connectors — **without them it can find bugs but can't file them or compare against designs.**

**Notion (the tracker — required if your bug board is in Notion):**
1. In Claude Code, run `/mcp` (or in the desktop app: Settings → Connectors) and add the **Notion** connector.
2. Authorize it against the workspace that contains your bug board, and make sure the integration is granted access to that board's database (in Notion: the database page → ••• → Connections).
3. Verify: ask Claude *"fetch my bug board and list the last 3 tickets"*. If it can read them, it can also create and update them.

**Figma (required if designs are your source of truth):** add the official **Figma MCP** connector the same way and sign in to an account with access to the design file.

**Linear / GitHub Issues:** connect the matching MCP instead of Notion; set the tracker section of `qa.config.md` accordingly.

### Browser access — how the skill drives your app

The skill controls a real browser and authenticates as **you**, using a session token you hand it for that session:

1. Log in to your app normally in Chrome.
2. Open DevTools → **Application → Cookies** → find your session cookie (the config's auth recipe names it — e.g. `session`, `auth`, `token`).
3. When the round starts, the skill asks for the value — paste it in. It's injected into the QA browser for this session only, never stored or committed.

Browser engines, in order of preference: any headless browser tooling already installed in your Claude Code setup; the **Claude in Chrome** extension (you watch it click in real time — note some sites, e.g. crypto/wallet apps, are blocked by its safety rules); or the **reverse workflow** as the universal fallback — the skill hands you an exact shot list, you paste screenshots, it annotates and files. Document which works for your app in `qa.config.md`'s known-quirks section after the first round.

> Tip: token expiry matters. If your session tokens are short-lived, the smoothest long-term setup is an env-gated QA auto-login on staging (e.g. `?qa_token=…`) — put whatever your team builds into the auth recipe.

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
