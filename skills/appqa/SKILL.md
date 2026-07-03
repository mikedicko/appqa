---
name: appqa
description: Generic AI QA round for any web app — drive the live app, compare against the project's source of truth (Figma or Notion specs), file annotated bugs to the project's tracker, or fix them in-session. Use when the user says /appqa or asks for a QA round on a project that has a qa.config.md.
---

# App QA round (/appqa)

You are running a QA round on a web app. The engine below is generic; **everything project-specific comes from the project's `qa.config.md`** — never assume another project's conventions.

## 0. Load the project config
1. Look for `qa.config.md` at the project root (then `.claude/qa.config.md`, then `docs/qa.config.md`). It defines: app URL + auth recipe, source of truth (figma / notion / both), tracker (system, database/board id, property mapping, developer defaults), mode (`report` or `fix`), evidence hosting, hidden/intentional features, known quirks, and the patterns-file location.
2. **If no config exists:** offer to scaffold one — interview the user briefly (app URL, how to authenticate, where designs/specs live, where bugs go, report vs fix mode, anything intentionally unfinished) and write `qa.config.md` from the template in this kit. Don't start a round without a config.
3. Read the project's **patterns file** (path from config; create it if missing from the template). This is the learning file: bug types this team cares about + past rejection reasons. Also **calibrate**: query the tracker for bugs filed manually since the last round and for rejected-with-comment tickets; fold new bug types and rejection lessons into the patterns file.
4. Ask for scope if not given: full round, one screen/flow, or re-test of the fixed/QA-status column.
5. **Figma projects — section map:** the config's Figma section map lists MCP links per app section (registered via Dev Mode → select a SECTION → copy the MCP link from the right-hand panel). If a screen you're testing has no registered section, ask the operator to send its section MCP link (explicitly: a section — full-page links time out on the Figma MCP, and individual element links are too granular since component sets aren't gospel). Save new links into the config's section map for future rounds.

## 1. Access & driving the app
- Use the auth recipe from the config verbatim (cookie injection, env-gated QA login, test account, etc.). Never invent an auth path; never use real-money/production-destructive accounts unless the config explicitly says so.
- Browser: gstack browse if installed (`~/.claude/skills/gstack/browse/dist/browse`); else Claude-in-Chrome if the site allows it; else the **reverse workflow** (precise shot lists the operator fulfils; their pasted screenshots are recoverable from the session transcript JSONL as base64 — never ask them to re-send).
- Headless survival kit (battle-tested): one bash call per interaction sequence if the browser dies between calls; custom components that ignore synthetic clicks need the full pointer sequence (`pointerdown,mousedown,pointerup,mouseup,click` as PointerEvent/MouseEvent on the element or `document.elementFromPoint`); scroll the inner container (`scrollHeight>clientHeight`), not window; some client-side transitions can crash the renderer — don't grind, add the screen to the operator shot list and record the crasher in the config's known-quirks section.

## 2. The checks (per screen — slow is smooth)
1. **Coverage** — every element/flow in the source of truth exists in-app. Figma mode: page designs are gospel, component sets are NOT. Notion mode: the spec/PRD pages define expected behaviour. Re-test any "missing" claim live before filing — teams ship between rounds.
2. **Functionality** — click everything; run **journeys end-to-end** (sign-up, core loop, settings flows, destructive-action confirmations), not just screenshots. Open every sub-flow behind every sheet/menu — verifying the menu exists is not QA.
3. **Fidelity** — Figma mode: pixel-perfect fonts/spacing/colors via `get_variable_defs`/`get_metadata` + DOM `getComputedStyle` as proof. Notion mode: behaviour matches the written spec, copy matches specified strings.
4. **State/visibility logic** — roles, plans/tiers, subscribed vs not, owner vs viewer, mode toggles (e.g. demo vs live). Gate checks belong server-side — client-hidden data still leaks via the network tab.
5. **Common-sense bugs** — wrong images in slots, zero/placeholder data that should move, stale mock/stub data (hardcoded emails, test strings), raw third-party errors in themed UI, dead controls.
6. **Detail sweep** — number formatting (currency decimals, thousands separators, compact large numbers), copy nits (plurals, double punctuation, entities like `&apos;`, typos), broken navigation (dead back buttons, traps).
7. **UX suggestions** — flag as suggestion, not bug.

## 3. Before filing — the two gates
1. **Dedupe** against the tracker (title + semantic search).
2. **Pending-work check** — search the project's epics/backlog; if planned work covers the finding, don't file (or file with an explicit "defer to <epic>" banner). Never hand devs a ticket their roadmap already owns.

## 4. Output — report mode
File to the tracker defined in the config, using its property mapping. **Body template (must read like a short story, not a wall of bold labels):**

```markdown
[⚠️ defer-to-epic / ✅ recommend-close banners above everything, when applicable]

## The issue
2-4 plain-English sentences: what the user sees, where, why (briefly). No code in the first sentence. Include exact observed values.

## Expected
Per the source of truth. 1-3 sentences.

## Fix prompt (Claude Code)
```(fenced)
Context: read this bug's tracker page <its own URL> first and follow every
link in it for full context before changing anything.
<the prompt: file:line refs, the change, the design/spec node to match, what to verify.>
```

## Done when
- 2-4 scannable acceptance bullets

## Links
- 📸 [Annotated screenshot](evidence URL)
- 🎨/📄 [Design or spec — full clickable URL, never bare node ids]
- 🔗 Related epic/task: [link] — always find the work item the feature belongs to
- Code: `path/file.ts:line`
- 🧭 In-app path: one-line repro route
```

## 4b. Output — fix mode
When the config sets `mode: fix` (or the user asks): for each bug, **root-cause before touching anything**, fix in the project source, verify the fix live in the app (re-drive the flow), and commit atomically per fix with a clear message. Still keep a running list: fixed (with commit sha), needs-decision (product call required — ask, don't guess), and out-of-scope (file to tracker instead). Never mix multiple bug fixes in one commit. Skip anything the pending-work gate says the roadmap owns.

## 5. Evidence (every visual finding)
Pipeline (generator ships in this kit: `tools/gen_evidence.py`):
1. Capture live PNG (+ design/spec image for comparison findings).
2. Coordinates from real data ONLY — DOM `getBoundingClientRect` / Figma `get_metadata`. Never guess.
3. JSON config → annotated HTML (green box = expected/target, red box + label = issue; `labelBelow` to dodge collisions; pad short image strips so labels don't clip).
4. **Mandatory QA render:** serve via `python3 -m http.server`, load headless, screenshot, LOOK at it, verify every box lands; fix and re-render until right.
5. Full-page PNG (viewport = scrollHeight) → save to the evidence location from the config (repo folder committed + linked by URL is the zero-friction default; private artifacts need per-item sharing) → link from the ticket as `📸`.

## 6. Learning loop (every round)
- New bug type → one line in the project's patterns file.
- Rejected ticket → record WHY in its "process rules learned" section (teams should reject-with-comment, never delete).
- New workflow trick / crasher / auth quirk → update the project's `qa.config.md` known-quirks section.
- Commit + push patterns/evidence changes if they live in a repo.

## 7. Wrap-up
Report: filed (links) / fixed (commits) / re-tested → passed/failed / recommend-close / blocked + operator shot list / patterns added. Plain English, lead with the biggest finding.
