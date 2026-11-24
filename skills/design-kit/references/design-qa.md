# Design QA

Two checks in `design-qa.md`: the **pre-handoff checklist** (designer, before screens become `approved`) and the **build review** (designer + QA, comparing the built app with mock.html). Column names and values are exact — `verify.py` checks them.

## Contents
1. Pre-handoff checklist
2. Tolerances
3. Build review round
4. Reporting

## 1. Pre-handoff checklist
- Run it before setting screens to `approved` in design.md §7. `Result`: `pass` · `fail` · `n/a` · `todo`; `verify.py` warns while anything is `fail` or `todo`.
- The template rows follow Nielsen's 10 heuristics plus accessibility and robustness. Add project-specific rows (e.g. "every amount shows THB with 2 decimals"); keep IDs `HC-01`… unique.
- `n/a` needs a reason in Notes.

## 2. Tolerances
- The template values are the defaults: exact tokens for color and type, ±2px spacing on a token, exact copy, same icon names, layout changes only at the §4.2 breakpoints.
- Tighten or loosen per project and say why (e.g. a native app may differ in system controls — date pickers, share sheets — by design).

## 3. Build review round
The procedure QA runs (from the team's QA test plan):
1. Header line above the table: `Round 1 — 2026-12-01 — build 3f2a1c — design 1.1 — reviewers: Designer, QA` (build = commit or URL; design = design.md version).
2. Scope: every screen with Status `approved` × every state in the ux-spec States matrix × devices `mobile` 375px, `tablet` at `md`, `desktop` at `lg` (§4.2) × Default theme plus Dark if shipped.
3. Reference: `mock.html?frame=1#<screen-id>:mock` beside the build. Theme via the toolbar (localStorage `mk-theme`), state via the state switcher (`data-state`). Pixel diffs only show where to look; the Tolerances table decides.
4. Default tolerances: color and typography exact tokens · spacing ±2px on the spacing scale · motion ±20ms · copy exact to the character.
5. Log each difference: `ID` `DQ-01`…, `Screen`, `Device`, `Theme`, `State`, `Property`, `Expected` (quote the token, string or rule from mock/spec), `Actual`, `Severity`, `Status` `open`, optional `Evidence` (screenshot path).
6. Status cycle: `open` → `fixed` (developer) → `verified` (**QA only**) · `wontfix` needs a reason and the name of who decided (in Evidence); if the design changes instead, add a changelog row in design.md.

Severity: `blocker` — a state or flow is missing, or copy / error text is wrong · `major` — wrong token, layout or accessibility · `minor` — spacing, icon · `cosmetic` — barely noticeable.

## 4. Reporting
- A round passes when no `blocker` or `major` row is `open` or `fixed` (unverified); `verify.py` warns while one is.
- QA attaches the build review table to the test report; recurring causes (e.g. raw hex instead of tokens) go to the team's lessons learned.
