# Users & Journeys

How to fill ux-spec.md `## Users & jobs`: short personas, jobs to be done and a journey table, each tied to roles and screen IDs. Column names are exact — `verify.py` reads them by name.

## Contents
1. Personas
2. Jobs to be done
3. Journey
4. Where the facts come from

## 1. Personas
- One persona per distinct way of using the product, not per job title — two roles that work the same way can share one; one role used in two very different contexts (desk vs phone) gets two.
- 2–4 personas is usual. Key = kebab-case describing the behavior (`busy-approver`, `new-requester`), not a fake name — fake names and stock photos add nothing a developer can use.
- `Role` = role keys from Roles & permissions (one or several, comma-separated).
- `Context`: frequency, device, environment, skill ("approves 20 POs a day between meetings, on a phone"). `Goals`: what success means to them. `Pain points`: what goes wrong today — each should lead to a design decision you can point to.

## 2. Jobs to be done
- Format: **When** (situation) · **I want to** (motivation) · **So I can** (outcome). Keep the solution out: "When a PO waits for me, I want to decide from my phone, so I can keep purchasing moving" — not "I want an Approve button".
- `ID` `JTBD-01`… unique. `Screen` = the screens that serve the job (`*` only for app-wide jobs like "find anything").
- Every MVP screen should serve at least one job; a screen that serves none is a candidate to cut.

## 3. Journey
- One row per stage, in order: trigger → find → do → confirm → follow-up. Include steps outside the app (`Screen` = `—`): the email that starts it, the phone call after it.
- `Pain point` / `Opportunity` may be `—`. An opportunity must become something in the design: a screen, a field default, a notification, a row in the spec.
- A Mermaid `journey` diagram under `### Journey map` is optional (for presentations); the table is the source of truth, and the diagram is synced to the wireframe Diagrams page like the others.

## 4. Where the facts come from
- Requirements doc and the PM first; interviews, support tickets or analytics when they exist. Mark anything not confirmed as an assumption in design.md §0 and turn the riskiest into a usability-test goal.
- Don't invent research. "Assumed" is fine; "users told us" without a source is not.
