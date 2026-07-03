# QA config — <project name>

Project-specific settings for `/appqa` rounds. Everything the generic engine needs to know about THIS app lives here. Keep it updated — the skill reads it at the start of every round and appends discovered quirks.

## App
- **URL:** https://<app-url> (staging preferred over prod)
- **Viewport:** 393x852 mobile-first | 1280x800 desktop  ← pick one
- **Auth recipe:** <exactly how the QA session authenticates — e.g. "inject cookie `session=<value>` from DevTools → Application → Cookies (operator supplies value)" or "env-gated QA login: append ?qa_token=... on staging" or "test account creds in 1Password vault X">
- **Test account:** <account to use; state clearly if real-money/destructive actions are EVER allowed (default: never)>

## Source of truth
- **Mode:** figma | notion | both
- **Figma:** file `<fileKey>`, page "<page name>" — page designs are gospel, component sets are not.
- **Figma section map** (register via Dev Mode → select a SECTION → copy the MCP link from the right-hand panel → paste to Claude. NOT full-page links — they time out; NOT individual elements — too granular):
  - <Section name>: <MCP link / node-id>
  - <Section name>: <MCP link / node-id>
- **Notion specs:** <links to the PRD/spec pages that define expected behaviour>

## Tracker
- **System:** Notion | Linear | GitHub Issues
- **Location:** <database/board id or repo>
- **Property mapping:** Title=<prop>, Description=<prop>, Type=<prop/value>, Priority=<prop>, Developer default=<user id>, Submitter=<user id>, Round tag=<prop, e.g. "QA Ref: QA-<date>">
- **Statuses:** <e.g. Not Started → In Progress → QA → Done; Rejected requires a comment>

## Mode
- **report** (findings only — never edit the app code) | **fix** (root-cause, fix, verify live, atomic commit per fix; file out-of-scope items instead)

## Evidence
- **Hosting:** <repo folder committed + linked (recommended: `<qa-repo>/evidence/QA-<date>/`) | tracker attachments | private artifacts (needs per-item sharing)>
- **Patterns file:** <path — the living catalogue of bug types + rejection lessons for THIS project>

## Pending-work sources (the don't-file-what's-planned gate)
- <where epics/backlog live — the skill checks these before filing anything>

## Intentionally unfinished / hidden (never file)
- <features hidden on purpose, stubs awaiting integrations, etc.>

## Known quirks (append as discovered)
- <headless crashers, click-immune components, auth gotchas, scroll containers, parser fragilities…>
