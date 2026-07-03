# appqa — an AI QA teammate for your web app

**What it is:** a Claude Code skill that QAs your app like a person would — it logs in, clicks through every flow, compares what it sees against your Figma designs or Notion specs, screenshots and annotates every issue, and files ready-to-fix tickets to your board (or just fixes the bugs itself, committing atomically). **And it learns:** every bug your team files by hand and every ticket you reject teaches it what to hunt for next round.

```
you:    /appqa — automatically check all parts of the checkout section
appqa:  *drives the app, compares against your designs, files 6 annotated
         tickets to your board, each with a fix prompt for the assigned dev*
```

---

## Get running (4 steps)

### 1. Install (per operator, ~2 min)
```bash
git clone https://github.com/mikedicko/appqa.git ~/appqa
mkdir -p ~/.claude/skills
ln -s ~/appqa/skills/appqa ~/.claude/skills/appqa
```

### 2. Connect your tools (~5 min)
The skill files bugs through MCP connectors — **without them it can find bugs but can't file them.**

**Notion (if your bug board is in Notion) — required:**
1. In Claude Code run `/mcp` (desktop app: Settings → Connectors) → add **Notion**.
2. Authorize the workspace, then in Notion grant the integration access to the bug board itself (database page → ••• → Connections).
3. Verify: ask Claude *"fetch my bug board and list the last 3 tickets."* If it reads them, it can write them.

**Figma (if designs are your source of truth):** add the official **Figma MCP** connector, signed into an account with file access.

**Linear / GitHub Issues:** connect that MCP instead and point the config's tracker section at it.

### 3. Configure your project (~10 min, once per project)
Drop a `qa.config.md` in your project repo — it tells the engine everything project-specific: app URL, auth recipe, source of truth, tracker mapping, report-vs-fix mode, what's intentionally unfinished. Copy `templates/qa.config.md` and fill it in, **or just run `/appqa` and let the skill interview you and write it.**

Also copy `templates/BUG_PATTERNS.md` to your repo — that's the learning file (more below).

**Figma projects — register your sections:** in Figma **Dev Mode**, select a **section** (e.g. "Checkout", "Settings") on the canvas, copy the **MCP link** from the right-hand panel, paste it to Claude and say what it is — it saves to the config's section map. Sections only: ❌ full-page links time out on the Figma MCP; ❌ individual elements are too granular (component sets aren't gospel — page designs are). Repeat per app section.

### 4. First round — see what it can do
How the skill authenticates as you: log into your app in Chrome → DevTools → **Application → Cookies** → copy the session cookie named in your auth recipe → paste it when the skill asks. Used for that session only, never stored.

Then try:
```
/appqa — automatically check all parts of the checkout section
```
Other good first prompts:
- `/appqa full round` — the whole app, every screen, every journey
- `/appqa re-test the QA column` — verify tickets your devs marked as fixed
- `/appqa fix mode: the settings screen` — find AND fix, one commit per bug

The skill suggests one of these itself the moment your config is scaffolded — take it up on it.

---

## It learns your app

This is the compounding part. Each project keeps a `BUG_PATTERNS.md` — a living catalogue of bug types and team rulings:

- **Every bug your team files manually** gets read at the start of each round; new bug *types* are added to the catalogue, so automated checks start hunting for the things your team actually cares about.
- **Every rejected ticket teaches it what NOT to file.** House rule: reject with a comment saying why — never delete. The skill reads rejections before every round and records the reason ("that's intentional", "that's covered by the Q3 epic", "component sets aren't our source of truth") so the same false positive never comes back.
- **Every workflow quirk it discovers** (auth gotchas, click-immune components, screens that crash headless browsers) gets appended to the config so future rounds don't re-learn it.

Ten rounds in, it's not a generic QA bot anymore — it's *your* QA bot.

## Triggering rounds automatically (Notion boards)

Native Notion automations can't invoke Claude and can't express "when all tasks in an epic are done" (rollup changes don't fire triggers). The working pattern is a **Claude Code scheduled task** that polls the board and reacts. Two recipes:

**Recipe A — epic completed → QA handoff.** Ask Claude Code:
> Create a scheduled task that runs weekday mornings: query our Epics database for epics not marked Done; for any epic where every related task is Done, set the epic to Done and add a comment tagging <QA operator> asking them to run `/appqa` scoped to the screens that epic touched, linking this repo's README.

**Recipe B — fixed tickets → auto re-test.** Ask Claude Code:
> Create a scheduled task that runs daily: if 5 or more tickets on our bug board are in "QA" status, run /appqa in re-test mode against them — verify each fix live in the app, move passes to Done and failures back to In Progress with a comment explaining what still breaks.

Both run from the operator's machine while Claude Code is open (they catch up on next launch if it was closed). Tip: click "Run now" once after creating a scheduled task to pre-approve its tool permissions so future runs never stall.

## What a round produces

- **Report mode:** tickets on your board that read like a teammate wrote them — plain-English issue → expected behaviour → a self-contained **fix prompt** for the assigned dev's AI (it opens with "read this ticket and follow its links") → acceptance bullets → links (annotated screenshot, design/spec, related epic, one-line repro path). Deduped against your existing tickets AND your roadmap — it won't file what a planned epic already owns.
- **Fix mode:** root-caused fixes committed atomically per bug, each verified live in the app before committing; product-decision questions get asked, not guessed; out-of-scope finds get filed instead.
- **Evidence:** annotated full-page screenshots (green box = expected, red box = issue) that pass a mandatory render-and-verify loop before publishing — no mislabeled arrows, ever.

## House rules baked into the engine

- Page designs are gospel; Figma component sets are not. In Notion mode, the spec pages are gospel.
- Re-test "missing" claims live before filing — teams ship between rounds.
- Never file what the roadmap already owns; banner with "defer to epic" when in doubt.
- Reject-with-comment, never delete — rejections train the next round.
- Gate visibility server-side: client-hidden data still leaks via the network tab.
- No real-money / destructive actions unless the project config explicitly allows them.

## Make it yours

The whole engine is markdown and a small Python script — built to be extended. See **[EXTENDING.md](EXTENDING.md)** for where to add team rules, new connectors, new evidence styles, and new triggers, and what belongs in the engine vs your project config.

## Repo map

| Path | What |
|---|---|
| `skills/appqa/SKILL.md` | The engine — what Claude actually executes |
| `templates/qa.config.md` | Per-project config template |
| `templates/BUG_PATTERNS.md` | Per-project learning-file template |
| `tools/gen_evidence.py` | Annotated-evidence page generator |
| `EXTENDING.md` | How to build on top |

MIT licensed — fork it, ship it, PR improvements back.
