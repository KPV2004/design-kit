<p align="center">
  <img src=".claude-plugin/icon.png" width="96" alt="">
</p>

<h1 align="center">Design Kit — a skill</h1>

<p align="center">
  Describe an app. Get a complete, reviewable design project: wireframes of every screen, a clickable mockup,
  a design system, dev diagrams and a UX spec — all kept in sync whenever you ask for a change.
</p>

<p align="center">
  <a href="https://kpv2004.github.io/design-kit/">Docs (EN/TH)</a> ·
  <a href="README.th.md">ภาษาไทย</a> ·
  <a href="#install">Install</a> ·
  <a href="#update-the-skill">Update</a> ·
  <a href="#other-ai-agents">Other agents</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#what-you-get">What you get</a> ·
  <a href="#review-workflow">Review workflow</a>
</p>

![Wireframe with desktop, tablet and mobile side by side, and a pinned review comment](docs/images/wireframe-devices.png)

## Why

Asking an AI to "design a screen" usually gives you one pretty page that doesn't match the next one, emoji for icons, no empty or error states, and nothing a developer can build from. This skill makes the AI work like a designer handing off to a dev team:

- **Every screen**, not just the happy path — including login, 403/404, empty states, session expired.
- **One source of truth** (`design.md`) for colors, typography and icons, checked for WCAG AA contrast — light **and dark** when the app ships dark mode.
- **A spec devs implement from** (`ux-spec.md`) — state matrix per screen, exact error text, interactions, copy deck, API payloads — so nobody has to reopen app code.
- **Low-fi wireframes first**, then a hi-fi mockup, so structure is agreed before colors.
- **Dev diagrams** — ER, state, sequence, API contract — that match the screens.
- **Changes propagate**: "add a phone field" updates the wireframe, mockup, spec, ER diagram and API table together.
- **Verified**: a script checks that every file agrees before anything is handed over.

Works for internal ERP/back-office tools, customer-facing web apps and mobile apps. Deliverables default to English; localized apps (e.g. Thai) keep their real UI language, with every locale's exact strings recorded in the spec's copy deck — Thai typography rules, THB and dd/MM/yyyy formats included.

## Install

### Claude Code — plugin marketplace (recommended)

Inside a Claude Code session:

```
/plugin marketplace add KPV2004/design-kit
/plugin install design-kit@design-kit
```

Or from your shell:

```bash
claude plugin marketplace add KPV2004/design-kit
claude plugin install design-kit@design-kit
```

Update later with:

```bash
claude plugin marketplace update design-kit
claude plugin update design-kit@design-kit
```

Remove with `claude plugin uninstall design-kit@design-kit`.

### Claude Code — manual copy

```bash
git clone https://github.com/KPV2004/design-kit.git
cp -r design-kit/skills/design-kit ~/.claude/skills/design-kit
```

Use `<your-project>/.claude/skills/` instead of `~/.claude/skills/` to install it for one repository only.

### Claude.ai (web, desktop, mobile)

1. Download `design-kit.zip` from the [latest release](https://github.com/KPV2004/design-kit/releases/latest)
   (or build it yourself: `./tools/build-skill.sh` → `dist/design-kit.zip`).
2. Make sure **Code execution and file creation** is enabled in Settings → Capabilities.
3. Go to **Customize → Skills**, click **+** → **Create skill** → **Upload a skill**, and choose the zip.

Skills you enable on claude.ai also sync to Claude Code when you sign in with the same account. See Anthropic's guide: [Use skills in Claude](https://support.claude.com/en/articles/12512180).

### Other AI agents

The skill follows the open [Agent Skills](https://agentskills.io) format (a folder with a `SKILL.md`), so any agent that supports skills can use it.

**Easiest: the `skills` CLI.** It detects which agents you have installed and copies the skill to the right folder for each:

```bash
npx skills add KPV2004/design-kit
```

Pick agents explicitly with `-a`, for example `npx skills add KPV2004/design-kit -a codex -a cursor`.

**Manual copy.** Clone once, then copy `skills/design-kit` into your agent's skills folder:

```bash
git clone https://github.com/KPV2004/design-kit.git
cp -r design-kit/skills/design-kit ~/.agents/skills/design-kit
```

| Agent | Global (all projects) | One project only |
|---|---|---|
| OpenAI Codex CLI | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| GitHub Copilot (VS Code / CLI) | `~/.copilot/skills/` | `.github/skills/` |
| Other agents | see the agent's docs | `.agents/skills/` works for many |

Folder names change between agent versions, so check your agent's docs if the skill doesn't show up. Restart the agent after copying.

**Chat apps without skill support** (ChatGPT, Gemini web, etc.): download `design-kit.zip` from the [latest release](https://github.com/KPV2004/design-kit/releases/latest), upload it to the chat (or a project/custom GPT), and say *"Follow SKILL.md in this zip to design …"*. The wireframes and mockup need a tool that can create files, and `verify.py` needs one that can run Python — without them you get the design text only.

The instructions were written and tested with Claude. Other models can follow them, but results vary — always open the generated `wireframes.html` and `mock.html` to check.

### Requirements

- Python 3.9+ (for the helper scripts the skill runs).
- Optional: `pip install playwright && playwright install chromium` — enables browser checks in `verify.py` (JS errors, icon names, Mermaid syntax, annotation visibility). Already available on claude.ai.
- An internet connection when opening the HTML files (Tailwind, fonts, icons and Mermaid load from CDNs).

## Update the skill

Pick the update path that matches how the skill was installed.

### Claude Code — plugin marketplace

Updates come from this GitHub repo, so push your changes first, then refresh in a session:

```bash
claude plugin marketplace update design-kit
claude plugin update design-kit@design-kit
```

### Claude.ai (uploaded skill)

Rebuild the zip, then replace the upload:

```bash
./tools/build-skill.sh          # → dist/design-kit.zip
```

On claude.ai: **Customize → Skills → design-kit → Delete**, then **Create skill → Upload a skill** with the new zip.

### Manual copy (Claude Code, Codex, Cursor, other agents)

Re-copy the folder with `rsync`, so files that were removed or renamed in the repo are also removed locally — then restart the agent, since skills load at startup:

```bash
rsync -a --delete --exclude '__pycache__' skills/design-kit/ ~/.claude/skills/design-kit/   # Claude Code manual install
rsync -a --delete --exclude '__pycache__' skills/design-kit/ ~/.agents/skills/design-kit/   # Codex CLI and most agents
```

Plain `cp -r skills/design-kit <dest>` works too, but leaves stale files behind when the skill removes or renames one. Point the destination wherever your agent reads skills from (see the install table above; e.g. `~/.zcode/skills/` for ZCode, `~/.cursor/skills/` for Cursor).

### The `skills` CLI

```bash
npx skills add KPV2004/design-kit
```

Re-running it refreshes the copies it installed.

### Existing design projects

A design project carries its own copy of the review engine (`_engine/`) and tools (`_tools/`) — it does not update itself. `verify.py` warns when the engine is older than the tools. From the project folder:

```bash
python _tools/update_engine.py ~/.claude/skills/design-kit   # or the path where you installed the skill
python _tools/verify.py .
```

It copies the skill's `_engine/` and `scripts/` over the project's copies; your design files are never touched. Without a path it searches the usual install locations. Projects made before 1.2.1 don't have `update_engine.py` yet — copy it once from `skills/design-kit/scripts/`.

### Releasing a new version

```bash
./tools/release.sh prepare 1.3.0   # writes the version everywhere, dates the CHANGELOG entry, opens a release PR
./tools/release.sh tag 1.3.0       # after merging: pushes tag v1.3.0 → the workflow publishes the zip
```

Details in [Contributing](#contributing).

## Usage

The skill triggers on its own when you ask for design work. Examples:

```
Design a purchase-order approval system for a factory: list, detail, approve/reject, dashboard.
Users are office staff who use Dynamics AX all day.
```

```
ออกแบบแอปจดรายรับรายจ่ายบนมือถือ มีหน้าบันทึก สรุปรายเดือน และตั้งงบประมาณ
```

```
Wireframe a customer self-service portal: sign up, login, view invoices, raise a ticket.
```

For apps with more than ~8 screens, Claude first sends you the screen inventory, user flow, palette and icon set to confirm — so it doesn't build 20 screens on a wrong assumption. Then it builds everything and runs the checks.

To change something, just say it: *"เปลี่ยนสีหลักเป็นเขียว"*, *"add a Tablet layout to the list screen"*, *"remove the dashboard"*. Claude edits every affected file and bumps the version.

In Claude Code you can also invoke it explicitly: `/design-kit:design-kit` when installed as a plugin, `/design-kit` when copied manually.

## What you get

Each design is a self-contained folder:

```
<app>-design/
├── AGENTS.md          AI entry point — file roles, editing rules, commands (CLAUDE.md imports it)
├── design.md          colors (light + dark), typography, icons, components, screen inventory, changelog
├── ux-spec.md         behavior, state matrix, validation + exact error text, copy deck, diagrams (Mermaid), API contract, risks
├── usability-test.md  test plan: goals, participants, 5 tasks with screens + success criteria, measures, results
├── wireframes.html    every screen, low-fi — open in a browser
├── mock.html          hi-fi clickable mock with a theme picker — open in a browser
├── _engine/           shared viewer code (toolbar, zoom, comments, device frames)
├── _tools/            verify.py · sync_diagrams.py · export_tokens.py
├── tokens/            tokens.css (incl. dark) · tailwind.config.js · tokens.json (incl. platform mapping, e.g. Flutter constants)
└── feedback/          exported review comments
```

Open `wireframes.html` or `mock.html` from inside the folder — they need `_engine/` next to them.

### Wireframes

- Overview of all screens grouped by module, or one screen at a time.
- **Desktop / Tablet / Mobile / All** filter (key `D`), frames side by side.
- **Zoom** — `−` `+`, fit, 100%, Ctrl/⌘ + scroll or pinch; **Space + drag** to pan.
- **Diagrams page** — user flow (boxes link to screens), ER, state and sequence diagrams.
- **Components page** — the grayscale `wf-*` kit (~35 blocks: top bar, sidebar, table, badges, form controls, tabs, stepper, pagination, modal, bottom sheet, toast, skeleton, empty state…) with a live example and **Copy** button for each. Screens are composed from it, so every wireframe uses the same vocabulary.

![Overview of all screens](docs/images/wireframe-overview.png)

![Diagrams page showing a sequence diagram](docs/images/diagrams.png)

### Mockup

- Review shell with **Desktop / Tablet / Mobile** preview — the real Tailwind breakpoints respond.
- **Theme picker** — Default / Dark / palette presets (from design.md §2.9) applied live, remembered per browser.
- State switcher (normal / empty / loading / error), notes sidebar explaining each numbered marker.
- **Component kit** — themeable `mk-*` components (buttons, fields, table, badges, tabs, pagination, dialog, alerts, toast, skeleton, empty…) driven by the design tokens. Hover / focus / disabled / loading / error states, 40px targets (44px on touch), reduced-motion support, and AA-safe text in dark themes are built in.
- **Keyboard-testable** — mark widgets with ARIA roles and the engine adds the standard keyboard behavior: arrow keys in tabs and menus, `openDialog()` moves focus in, traps Tab and closes on Esc, then returns focus. `verify.py` checks text contrast ≥ 4.5:1 on every screen in every theme.
- **Design system page** — every color with its contrast ratio, type scale, the icon set, and a **component gallery** with copyable markup that restyles live with the theme picker.

| Mobile preview | Design system |
|---|---|
| ![Mockup in mobile frame](docs/images/mockup-mobile.png) | ![Design system page](docs/images/mockup-design-system.png) |

### Design choices that keep it from looking AI-generated

- No emoji as icons; one icon set chosen for the users (Fluent for Office/Dynamics users, Phosphor or Tabler elsewhere — not Lucide by default).
- Icons support labels instead of decorating every heading; no sparkles, no pastel icon-card grids.
- Realistic content in the user's language instead of lorem ipsum.

## Review workflow

1. Open `wireframes.html`, press **💬** (or `C`) and click any spot to pin a comment — choose *Fix / Add / Remove / Question*.
2. Press **Export** → copy or download the markdown.
3. Paste it to Claude (or drop it in `feedback/` and ask Claude Code to apply it).

Claude locates each pinned element, applies the change to every affected file, answers the questions, and reports item by item. Comments are stored in your browser per file — export before moving or renaming the folder.

## Repository layout

```
.claude-plugin/
  plugin.json            plugin manifest
  marketplace.json       makes this repo installable with /plugin marketplace add
  icon.png
skills/design-kit/   the skill (this is what gets installed)
  SKILL.md               workflow instructions for Claude
  references/            color, icons, enterprise/web/mobile patterns, dev diagrams, accessibility
  assets/project/        the project template (content files + _engine/)
  scripts/               verify.py, sync_diagrams.py, export_tokens.py
examples/procura-design/ a full design project made with the skill — test fixture and the docs site's live demo
tests/                   unit tests (scripts) and browser tests (engines, contrast in every theme)
tools/
  check.sh               everything CI runs
  release.sh             prepare / tag a release
  build-skill.sh         builds dist/design-kit.zip for claude.ai
docs-site/               the GitHub Pages site (kpv2004.github.io/design-kit)
.github/workflows/       ci (every PR) · release (tag vX.Y.Z → zip) · docs (Pages)
```

## Contributing

Issues and pull requests are welcome. Publishing your own fork? Run `./tools/set-owner.sh <github-user> "<Your Name>"` once to fill in the install links and manifests.

Before opening a PR, run what CI runs:

```bash
pip install playwright && playwright install chromium   # once
./tools/check.sh                                        # or --fast to skip browser tests
claude plugin validate .                                # manifest + marketplace
```

`check.sh` runs the unit tests, `verify.py` on `examples/procura-design`, browser tests on the template and the example (no JS errors; the State switcher shows exactly one variant; every text ≥ 4.5:1 in every theme at desktop and mobile widths) and builds the zip. If you change `_engine/` or `scripts/`, refresh the example with `cd examples/procura-design && python3 _tools/update_engine.py ../../skills/design-kit` — CI fails while its copies differ. Add a line under `## Unreleased` in `CHANGELOG.md`.

**Releasing** takes two commands, matching the PR workflow:

```bash
./tools/release.sh prepare 1.3.0   # on an up-to-date main
# merge the release PR on GitHub, then:
git switch main && git pull
./tools/release.sh tag 1.3.0
```

`prepare` refuses a version that isn't `X.Y.Z` or isn't higher than the current one, writes it to `plugin.json`, `_engine/VERSION`, `verify.py` and the docs site, dates the `## Unreleased` entry, runs the checks and opens the PR. `tag` only tags when `main` already carries that version. The Release workflow only reacts to `vX.Y.Z` tags.

## License

[MIT](LICENSE)
