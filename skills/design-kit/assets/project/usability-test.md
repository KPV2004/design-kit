# [App] — Usability test plan
> Version 1.0 — matches design.md 1.0 · Prototype: mock.html (wireframes.html for early rounds)
> Run before development starts. Five participants find most of the problems a design has; fix, then test again.

## Goals
What decision this round informs, and the success metric from ux-spec.md Summary it checks.
- Can [primary user] complete [primary task] without help?
- [One question per open assumption in design.md §0]

## Participants
| | |
|---|---|
| Number | 5 (per user group) |
| Who | [role, how often they do the task, device they use] |
| Screener | [2–3 questions that rule people in or out] |
| Not | [people who designed or built it; power users of the old system, unless they are the target] |

## Setup
- Device and viewport: [desktop 1440 / phone 390 — match the device model]
- Prototype: `mock.html`, Theme Default, State Default, starting screen `[screen-id]`
- Session: 30–45 min, moderated, think-aloud, recorded with consent
- Moderator never points at the screen; answers questions with "What would you do if I weren't here?"

## Tasks
Five tasks, ordered from warm-up to hardest. Each lists the screens it touches (IDs from design.md §7) and what counts as success.
Write scenarios as goals in the user's words — never name the button.

### T1 [Warm-up task]
- **Scenario:** "…"
- **Screens:** [screen-id] → [screen-id]
- **Success:** [observable end state, e.g. "reaches po-detail of PO-2611-0042"]
- **Watch for:** [hesitation points, wrong paths]

### T2 [Task]
- **Scenario:** "…"
- **Screens:** [screen-id]
- **Success:** …
- **Watch for:** …

### T3 [Task]
- **Scenario:** "…"
- **Screens:** [screen-id]
- **Success:** …
- **Watch for:** …

### T4 [Task that hits an error or edge case]
- **Scenario:** "…"
- **Screens:** [screen-id]
- **Success:** recovers using the error text from the spec's Fields table
- **Watch for:** …

### T5 [Hardest / least frequent task]
- **Scenario:** "…"
- **Screens:** [screen-id]
- **Success:** …
- **Watch for:** …

## Measures
| Measure | How | Target |
|---|---|---|
| Task success | completed without help (pass / pass with help / fail) | ≥ 4 of 5 per task |
| Time on task | from reading the scenario to the success state | [baseline or estimate] |
| Errors | wrong path or wrong value before recovering | note each |
| Ease (SEQ) | "Overall, this task was…" 1 very difficult – 7 very easy, after each task | ≥ 5.5 |
| SUS | 10-item System Usability Scale at the end | ≥ 68 |

## After the sessions
Rate each problem, then fix the design (and re-run verify) before the next round.

| Severity | Meaning |
|---|---|
| Critical | blocks task completion or causes data loss |
| High | causes errors or major delay for most participants |
| Medium | slows people down or causes confusion, they recover |
| Low | cosmetic or noticed by one participant |

## Results
| Task | Success (n/5) | Median time | SEQ | Problems found (severity) | Design change |
|---|---|---|---|---|---|
| T1 | | | | | |
