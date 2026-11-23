# Procura — Usability test plan
> Version 1.0 — matches design.md 1.0 · Prototype: mock.html
> Run before development starts. Five participants find most of the problems a design has; fix, then test again.

## Goals
Checks the success metric in ux-spec.md: approvers decide on a PO quickly, and approval on a phone works without help (≥ 95% completion).
- Can an approver find a pending PO and approve it on a phone without help?
- Do requesters understand why a rejected PO came back and how to resubmit it? (open question in ux-spec.md)
- Is the reject reason requirement clear before the error appears?

## Participants
| | |
|---|---|
| Number | 5 approvers + 5 requesters |
| Who | Approvers: department heads who approve ≥ 5 POs a week, mostly on a phone. Requesters: office staff who raise ≥ 2 POs a month on desktop |
| Screener | "How many purchase orders did you approve / raise last month?" · "On which device?" |
| Not | Procurement system admins; anyone who saw earlier versions of this design |

## Setup
- Approver sessions: phone viewport 390 (mock.html → Mobile). Requester sessions: desktop 1440.
- Prototype: `mock.html`, Theme Default, State Default, starting screen `login`
- Session: 30 min, moderated, think-aloud, recorded with consent
- Moderator never points at the screen; answers questions with "What would you do if I weren't here?"

## Tasks

### T1 Sign in and find what is waiting for you
- **Scenario:** "You've just come out of a meeting. Check whether anything is waiting for your approval."
- **Screens:** [login] → [po-list]
- **Success:** signs in and states how many orders are pending, without changing filters
- **Watch for:** whether the Pending chip being pre-selected is noticed

### T2 Approve a routine order
- **Scenario:** "Siam Steel's order for the Rayong plant is expected. Approve it."
- **Screens:** [po-list] → [po-detail]
- **Success:** PO-2611-0042 approved; returns to the list
- **Watch for:** checks amount and supplier before approving; reaches the sticky Approve button on the phone

### T3 Reject an order with a reason
- **Scenario:** "The order from Thai Logistics Partners is a duplicate. Send it back to the requester."
- **Screens:** [po-list] → [po-detail]
- **Success:** rejects with a reason of 5+ characters; understands the requester will see it
- **Watch for:** first attempt with a too-short reason — does "Tell the requester why (at least 5 characters)." lead to recovery?

### T4 Raise a new order and recover from an error
- **Scenario (requester):** "Order 120 steel sheets from Siam Steel for the Plant cost center, needed by 5 December."
- **Screens:** [po-list] → [po-form] → [po-detail]
- **Success:** submits for approval after fixing the amount error ("Enter an amount above 0.")
- **Watch for:** amount entry and the dd/MM/yyyy date; Save draft vs Submit confusion

### T5 Follow a broken link
- **Scenario:** "A colleague sent you a link to an old order. Open it and get back to your orders."
- **Screens:** [not-found] → [po-list]
- **Success:** returns to the order list in one step
- **Watch for:** whether "We can't find that page" is understood as the order being gone

## Measures
| Measure | How | Target |
|---|---|---|
| Task success | completed without help (pass / pass with help / fail) | ≥ 4 of 5 per task; T2 5 of 5 |
| Time on task | from reading the scenario to the success state | T2 under 60 s on a phone |
| Errors | wrong path or wrong value before recovering | note each |
| Ease (SEQ) | 1 very difficult – 7 very easy, after each task | ≥ 5.5 |
| SUS | 10-item System Usability Scale at the end | ≥ 68 |

## After the sessions
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
| T2 | | | | | |
| T3 | | | | | |
| T4 | | | | | |
| T5 | | | | | |
