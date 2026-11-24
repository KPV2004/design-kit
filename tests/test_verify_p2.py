"""Unit tests for the Phase 2 checks in verify.py (docs/p2-schema.md): R8 users & jobs, R9 design-qa.md,
R10 notifications, R11 assets, R12 analytics events, R13 charts. Every section is optional. No browser needed.

Run: python -m unittest discover -s tests -p 'test_verify_p2.py'
"""
import contextlib
import importlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'skills' / 'design-kit' / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
verify = importlib.import_module('verify')
p1 = importlib.import_module('test_verify_p1')

IDS = {'login', 'po-list', 'po-detail', 'po-form', 'not-found'}
ROLES = {'guest', 'requester', 'approver'}

USERS = """## Users & jobs
### Personas
| Persona | Role | Context | Goals | Pain points |
|---|---|---|---|---|
| busy-approver | approver | department head, on a phone | clear the queue | opens each PO |
| new-requester | requester, guest | first week | raise a PO | unknown cost centers |

### Jobs to be done
| ID | Persona | When | I want to | So I can | Screen |
|---|---|---|---|---|---|
| JTBD-01 | busy-approver | a PO waits | decide from my phone | keep buying | po-detail |
| JTBD-02 | new-requester | I need goods | raise a PO | get them | po-form, po-list |

### Journey
| Stage | Persona | Action | Screen | Pain point | Opportunity |
|---|---|---|---|---|---|
| Notice | busy-approver | gets a push | — | no amount | amount in push |
| Decide | busy-approver | approves | po-detail | — | |

### Journey map
Mermaid is optional and not read for screen IDs.

## User flow
"""

DESIGN_QA = """# Procura — Design QA
> Version 1.0 — matches design.md 1.0

## Pre-handoff checklist
| ID | Check | Heuristic | Result | Notes |
|---|---|---|---|---|
| HC-01 | Every screen shows where the user is | Visibility of system status | pass | |
| HC-02 | Errors say how to fix them | Help users recover | n/a | |

## Tolerances
| Property | Tolerance | How to check |
|---|---|---|
| spacing | ±2px | DevTools |

## Build review
| ID | Screen | Device | Theme | State | Property | Expected | Actual | Severity | Status |
|---|---|---|---|---|---|---|---|---|---|
| DQ-01 | po-list | mobile | Default | default | layout | cards below md | table scrolls | major | open |
| DQ-02 | po-form | desktop | Teal | error | copy | exact error text | paraphrased | minor | fixed |
"""

DESIGN = """# Procura — Design System
> Version: 1.0 · Device model: Responsive web

### 2.6 Chart palette
| Token | Hex | Usage |
|---|---|---|
| chart-1 | #2563eb | first series |
| chart-2 | #16a34a | second series |

### 2.9 Theme variants (mock theme picker)
| Theme | Token | Value |
|---|---|---|
| Teal | brand-600 | #0d9488 |

## 9. Assets
| Asset | Platform | Size | Format | Screen | Source | Status | Notes |
|---|---|---|---|---|---|---|---|
| logo | all | vector | svg | — | brand/logo.svg | approved | |
| favicon | web | 32x32, 16x16 | ico | — | TBD | needed | |
| favicon | web | vector | svg | — | TBD | needed | same name, other format |
| web-manifest | web | — | webmanifest | — | public/site.webmanifest | draft | |
| empty-orders | web | 240x160 | svg | po-list | TBD | draft | |
"""

ANALYTICS = """## Analytics events
### Common properties
| Property | Type | Notes |
|---|---|---|
| user_id | string | internal ID |
| platform | enum(web/ios/android) | |

### Events
| Event | Trigger | Screen | Source | Properties | Req ID |
|---|---|---|---|---|---|
| screen_viewed | the screen rendered | * | client | screen_id: string | — |
| po_submitted | Submit returns 2xx | po-form | server | po_id: string, amount: number, currency: string, line_count: integer | R3 |
| po_list_filtered | a chip changes | po-list | client | status: enum(all/pending/approved), result_count: integer, has_query?: boolean | R2 |

## Dev diagrams
"""

NOTIF = """## Notifications
Locales: th, en

### Notification triggers
| ID | Trigger | Recipient | Channels | Category | Screen | Variables |
|---|---|---|---|---|---|---|
| NT-01 | po_submitted | approver | push, email | transactional | po-detail | po_number: string, amount: money, action_url: url |

### Notification copy
| ID | Channel | Locale | Subject / Title | Body |
|---|---|---|---|---|
| NT-01 | push | th | มี PO รออนุมัติ | {{po_number}} ยอด {{amount}} |
| NT-01 | push | en | PO waiting for approval | {{po_number}} for {{amount}} |
| NT-01 | email | th | {{po_number}} รออนุมัติ | ยอด {{amount}} |
| NT-01 | email | en | {{po_number}} needs approval | Amount {{amount}} |

### Channel limits
| Channel | Field | Locale | Max chars |
|---|---|---|---|
| email | Subject / Title | all | 60 |
| push | Subject / Title | all | 40 |
| push | Body | all | 120 |

## Analytics events
"""

CHARTS = """## Charts
| Chart | Screen | Question | Type | Data | Palette | Table fallback |
|---|---|---|---|---|---|---|
| orders-by-status | po-list | How many orders wait at each status? | bar | x: status · y: count | chart-1 | yes |
| spend-trend | po-list, po-detail | Is spend rising? | combo | x: month · y: amount | chart-1, chart-2 | yes |
"""

INV = {s: {'req': r, 'module': 'Purchasing'} for s, r in
       (('login', 'R1'), ('po-list', 'R2, R4'), ('po-detail', 'R2, R4'), ('po-form', 'R3'), ('not-found', '—'))}


def run(fn, *args):
    verify.errors.clear(); verify.warns.clear()
    fn(*args)
    return list(verify.errors), list(verify.warns)


def has(msgs, *parts):
    return any(all(p in m for p in parts) for m in msgs)


class OptionalSections(unittest.TestCase):
    """Absent sections / file are not checked — no new breaking change on top of Phase 1."""
    def test_nothing_present_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run(verify.p2_checks, Path(d), INV, '# D\n', '# S\n'), ([], []))

    def test_section_without_table_errors(self):
        for fn, args in ((verify.users_checks, ('## Users & jobs\ntext\n', IDS, ROLES)),
                         (verify.assets_checks, ('## 9. Assets\nlater\n', IDS)),
                         (verify.charts_checks, ('## Charts\nnone yet\n', '', IDS))):
            with self.subTest(fn=fn.__name__):
                errs, _ = run(fn, *args)
                self.assertTrue(errs, fn.__name__)

    def test_heading_must_match_whole_line(self):
        self.assertEqual(run(verify.charts_checks, '## Charts and graphs\nprose\n', '', IDS), ([], []))

    def test_near_miss_headings_warn(self):
        # QA Q-P2-01: a misspelt optional heading would otherwise be skipped silently
        spec = '## Users and jobs\n## Notification\n## Analytics\n## Chart\n## User flow\n## Assumptions & open questions\n'
        design = '## 9 Assets\n## Voice and tone\n## 8. Voice & tone\n'
        with tempfile.TemporaryDirectory() as d:
            errs, warns = run(verify.p2_checks, Path(d), INV, design, spec)
        self.assertEqual(errs, [])
        for h in ('## Users and jobs', '## Notification', '## Analytics', '## Chart', '## 9 Assets', '## Voice and tone'):
            self.assertTrue(has(warns, f'"{h}"'), h)
        self.assertFalse(has(warns, 'User flow') or has(warns, 'Assumptions') or has(warns, 'heading "## 8. Voice & tone"'))


class UsersAndJobs(unittest.TestCase):
    """R8."""
    def test_valid_is_clean(self):
        self.assertEqual(run(verify.users_checks, USERS, IDS, ROLES), ([], []))

    def test_persona_rules(self):
        errs, _ = run(verify.users_checks, USERS.replace('| new-requester | requester, guest |', '| Busy | buyer |'), IDS, ROLES)
        self.assertTrue(has(errs, 'kebab-case'))
        self.assertTrue(has(errs, 'role "buyer" is not declared'))
        errs, _ = run(verify.users_checks, USERS.replace('new-requester | requester', 'busy-approver | requester'), IDS, ROLES)
        self.assertTrue(has(errs, 'declared twice'))

    def test_jtbd_rules(self):
        spec = USERS.replace('| JTBD-02 | new-requester |', '| JTBD-1 | ghost |').replace('| get them | po-form, po-list |', '| get them | — |')
        errs, _ = run(verify.users_checks, spec, IDS, ROLES)
        self.assertTrue(has(errs, 'must look like JTBD-01'))
        self.assertTrue(has(errs, 'persona "ghost"'))
        self.assertTrue(has(errs, 'Screen cannot be —'))
        errs, _ = run(verify.users_checks, USERS.replace('| po-detail |\n| JTBD-02', '| nowhere |\n| JTBD-02'), IDS, ROLES)
        self.assertTrue(has(errs, 'screen "nowhere"'))

    def test_journey_rules(self):
        errs, _ = run(verify.users_checks, USERS.replace('| Decide | busy-approver | approves | po-detail |', '| Decide | ghost |  | po-gone |'), IDS, ROLES)
        self.assertTrue(has(errs, 'persona "ghost"'))
        self.assertTrue(has(errs, '"action" is empty'))
        self.assertTrue(has(errs, 'screen "po-gone"'))

    def test_missing_sub_table(self):
        errs, _ = run(verify.users_checks, USERS.replace('### Journey\n', '### Path\n'), IDS, ROLES)
        self.assertTrue(has(errs, 'missing "### Journey"'))


class DesignQA(unittest.TestCase):
    """R9: design-qa.md is optional."""
    def run_qa(self, text, design=DESIGN):
        with tempfile.TemporaryDirectory() as d:
            if text is not None:
                (Path(d) / 'design-qa.md').write_text(text)
            return run(verify.design_qa_checks, Path(d), design, IDS)

    def test_missing_file_is_clean(self):
        self.assertEqual(self.run_qa(None), ([], []))

    def test_valid_is_clean(self):
        text = DESIGN_QA.replace('| major | open |', '| major | verified |')
        self.assertEqual(self.run_qa(text), ([], []))

    def test_open_blocker_or_major_warns(self):
        _, warns = self.run_qa(DESIGN_QA)  # DQ-01 major / open
        self.assertTrue(has(warns, 'DQ-01', 'does not pass'))
        _, warns = self.run_qa(DESIGN_QA.replace('| major | open |', '| blocker | fixed |'))
        self.assertTrue(has(warns, 'DQ-01', 'does not pass'))
        _, warns = self.run_qa(DESIGN_QA.replace('| major | open |', '| minor | open |'))
        self.assertFalse(has(warns, 'does not pass'))

    def test_round_line_and_evidence_column_are_ignored(self):
        text = DESIGN_QA.replace('## Build review\n', '## Build review\nRound 1 — 2026-11-24 — build abc — design 1.0 — QA\n\n') \
            .replace('| Severity | Status |', '| Severity | Status | Evidence |').replace('|---|---|---|---|---|---|---|---|---|---|', '|---|---|---|---|---|---|---|---|---|---|---|') \
            .replace('| major | open |', '| major | verified | shot.png |').replace('| minor | fixed |', '| minor | fixed | |')
        self.assertEqual(self.run_qa(text), ([], []))

    def test_build_review_may_be_empty(self):
        text = DESIGN_QA.split('| DQ-01')[0]
        self.assertEqual(self.run_qa(text), ([], []))

    def test_checklist_rules(self):
        errs, warns = self.run_qa(DESIGN_QA.replace('| pass |', '| todo |').replace('| HC-02 |', '| HC-01 |').replace('| n/a |', '| ok |'))
        self.assertTrue(has(errs, 'used twice'))
        self.assertTrue(has(errs, 'Result "ok"'))
        self.assertTrue(has(warns, 'HC-01', 'fail/todo'))

    def test_build_review_values(self):
        text = DESIGN_QA.replace('| DQ-01 | po-list | mobile | Default | default | layout |', '| DQ-01 | * | watch | Neon | idle | vibes |') \
                        .replace('| major | open |', '| huge | done |').replace('| exact error text | paraphrased |', '|  |  |')
        errs, warns = self.run_qa(text)
        for part in ('Screen cannot be *', 'Device "watch"', 'State "idle"', 'Property "vibes"', 'Severity "huge"',
                     'Status "done"', '"expected" is empty', '"actual" is empty'):
            self.assertTrue(has(errs, part), part)
        self.assertTrue(has(warns, 'theme "Neon"'))

    def test_one_screen_per_row(self):
        errs, _ = self.run_qa(DESIGN_QA.replace('| DQ-01 | po-list |', '| DQ-01 | po-list, po-form |'))
        self.assertTrue(has(errs, 'one screen ID per row'))

    def test_version_mismatch_warns(self):
        _, warns = self.run_qa(DESIGN_QA.replace('Version 1.0', 'Version 0.9'))
        self.assertTrue(has(warns, 'design-qa.md 0.9'))


class Notifications(unittest.TestCase):
    """R10."""
    EVENTS = {'po_submitted'}

    def check(self, spec, events=EVENTS):
        return run(verify.notifications_checks, spec, IDS, ROLES, events)

    def test_valid_is_clean(self):
        self.assertEqual(self.check(NOTIF), ([], []))

    def test_thai_length_ignores_non_spacing_marks(self):
        # Backend T14: combining() is 0 for Thai upper vowels — category Mn is the right test
        self.assertEqual(verify.msg_len('มี PO รออนุมัติ', {}), 11)
        self.assertEqual(verify.msg_len('{{po_number}} ยอด {{amount}}', {'po_number': 'string', 'amount': 'money'}), 12 + 5 + 12)

    def test_locales_line(self):
        errs, _ = self.check(NOTIF.replace('Locales: th, en\n', ''))
        self.assertTrue(has(errs, 'Locales'))
        errs, _ = self.check(NOTIF.replace('Locales: th, en\n', 'Some intro.\nLocales: th, en\n'))
        self.assertTrue(has(errs, 'Locales'))  # must be the first non-empty line

    def test_trigger_rules(self):
        spec = NOTIF.replace('| NT-01 | po_submitted | approver | push, email | transactional | po-detail |',
                             '| NT-1 | po_submitted | boss | push, fax | promo | * |')
        errs, _ = self.check(spec)
        for part in ('must look like NT-01', 'recipient "boss"', 'channel "fax"', 'Category "promo"', 'Screen cannot be *'):
            self.assertTrue(has(errs, part), part)

    def test_actor_recipient_and_dash_screen(self):
        spec = NOTIF.replace('| approver | push, email | transactional | po-detail |', '| actor, approver | push, email | transactional | — |')
        self.assertEqual(self.check(spec), ([], []))

    def test_trigger_vs_events(self):
        _, warns = self.check(NOTIF, {'po_approved'})
        self.assertTrue(has(warns, 'not an event'))
        self.assertEqual(self.check(NOTIF, None), ([], []))  # no analytics section → no comparison
        _, warns = self.check(NOTIF.replace('| po_submitted |', '| PO Submitted |'), None)
        self.assertTrue(has(warns, 'should be an event name'))

    def test_variables(self):
        errs, _ = self.check(NOTIF.replace('amount: money', 'amount: cash, po_number: string'))
        self.assertTrue(has(errs, 'type "cash"'))
        self.assertTrue(has(errs, '"po_number" is listed twice'))
        errs, _ = self.check(NOTIF.replace('ยอด {{amount}} |', 'ยอด {{total}} |'))
        self.assertTrue(has(errs, 'variable "total" is not declared'))

    def test_logic_in_template(self):
        for bad in ('{{#if amount}}x{{/if}}', '{% if amount %}', '{{ PO }}'):
            with self.subTest(bad=bad):
                errs, _ = self.check(NOTIF.replace('{{po_number}} for {{amount}}', bad))
                self.assertTrue(has(errs, 'logic in template'), errs)

    def test_unused_variable_warns_per_locale_but_not_url(self):
        _, warns = self.check(NOTIF.replace('{{po_number}} for {{amount}}', 'PO for you').replace('| {{po_number}} needs approval | Amount {{amount}} |', '| Needs approval | Amount {{amount}} |'))
        self.assertTrue(has(warns, 'po_number', 'en copy'))
        self.assertFalse(has(warns, 'action_url'))

    def test_copy_rules(self):
        spec = NOTIF.replace('| NT-01 | email | en |', '| NT-02 | email | en |').replace('| NT-01 | push | en | PO waiting for approval |', '| NT-01 | sms | de |  |')
        errs, _ = self.check(spec)
        for part in ('ID "NT-02"', 'channel "sms"', 'locale "de"', 'NT-01 email has no copy for locale(s) en',
                     'NT-01 push has no copy for locale(s) en'):
            self.assertTrue(has(errs, part), part)
        errs, _ = self.check(NOTIF.replace('| NT-01 | email | en | {{po_number}} needs approval |', '| NT-01 | email | th | {{po_number}} needs approval |'))
        self.assertTrue(has(errs, 'more than one row'))

    def test_empty_body_and_subject_error(self):
        errs, _ = self.check(NOTIF.replace('| Amount {{amount}} |', '|  |').replace('| PO waiting for approval |', '| — |'))
        self.assertTrue(has(errs, 'email/en', 'Body is empty'))
        self.assertTrue(has(errs, 'push/en', 'Subject / Title is empty'))

    def test_sms_may_have_no_subject(self):
        spec = NOTIF.replace('| push, email |', '| push, email, sms |') + ''
        spec = spec.replace('### Channel limits', '| NT-01 | sms | th | — | {{po_number}} ยอด {{amount}} |\n| NT-01 | sms | en | — | {{po_number}} {{amount}} |\n\n### Channel limits')
        spec = spec.replace('| Amount {{amount}} |\n\n| NT-01 | sms', '| Amount {{amount}} |\n| NT-01 | sms')
        self.assertEqual(self.check(spec), ([], []))

    def test_limits(self):
        _, warns = self.check(NOTIF.replace('| push | Subject / Title | all | 40 |', '| push | Subject / Title | all | 10 |'))
        self.assertTrue(has(warns, 'push limit is 10'))
        # locale-specific limit wins over all
        spec = NOTIF.replace('| push | Body | all | 120 |', '| push | Body | all | 120 |\n| push | Body | th | 20 |')
        _, warns = self.check(spec)
        self.assertTrue(has(warns, 'push/th', 'limit is 20'))
        self.assertFalse(has(warns, 'push/en', 'limit is 20'))
        errs, _ = self.check(NOTIF.replace('| push | Body | all | 120 |', '| push | Body | all | 120 |\n| push | Body | all | 90 |\n| fax | Text | xx | many |'))
        for part in ('more than one row for this channel', 'Channel "fax"', 'Field "Text"', 'locale "xx"', 'Max chars "many"'):
            self.assertTrue(has(errs, part), part)

    def test_no_limit_row_means_no_length_check(self):
        _, warns = self.check(NOTIF.replace('| email | Subject / Title | all | 60 |\n', '').replace('{{po_number}} needs approval', 'x' * 200))
        self.assertFalse(has(warns, 'limit'))


class Assets(unittest.TestCase):
    """R11."""
    def test_valid_is_clean(self):
        self.assertEqual(run(verify.assets_checks, DESIGN, IDS), ([], []))

    def test_values(self):
        d = DESIGN.replace('| empty-orders | web | 240x160 | svg | po-list | TBD | draft |', '| Empty_Orders | tv | big | gif | ghost |  | done |')
        errs, _ = run(verify.assets_checks, d, IDS)
        for part in ('kebab-case', 'Platform "tv"', 'Size "big"', 'Format "gif"', 'screen "ghost"', '"source" is empty', 'Status "done"'):
            self.assertTrue(has(errs, part), part)

    def test_duplicate_key_includes_format(self):
        errs, _ = run(verify.assets_checks, DESIGN.replace('| favicon | web | vector | svg |', '| favicon | web | vector | ico |'), IDS)
        self.assertTrue(has(errs, 'listed twice'))

    def test_dash_size_only_for_webmanifest(self):
        errs, _ = run(verify.assets_checks, DESIGN.replace('| logo | all | vector | svg |', '| logo | all | — | svg |'), IDS)
        self.assertTrue(has(errs, 'Size "—"'))

    def test_star_screen_errors_and_email_svg_warns(self):
        errs, warns = run(verify.assets_checks, DESIGN.replace('| logo | all | vector | svg | — |', '| logo | email | vector | svg | * |'), IDS)
        self.assertTrue(has(errs, 'Screen cannot be *'))
        self.assertTrue(has(warns, 'Gmail'))


class Analytics(unittest.TestCase):
    """R12."""
    def test_valid_is_clean_and_returns_events(self):
        verify.errors.clear(); verify.warns.clear()
        names = verify.analytics_checks(ANALYTICS, INV)
        self.assertEqual((verify.errors, verify.warns), ([], []))
        self.assertEqual(names, {'screen_viewed', 'po_submitted', 'po_list_filtered'})

    def test_absent_returns_none(self):
        self.assertIsNone(verify.analytics_checks('## Other\n', INV))

    def test_event_names(self):
        for bad, part in (('submitted', 'object_action'), ('PoSubmitted', 'object_action'), ('ga_po_submitted', 'reserved'),
                          ('a_' + 'b' * 40, 'object_action'), ('screen_viewed', 'listed twice')):
            with self.subTest(bad=bad):
                errs, _ = run(verify.analytics_checks, ANALYTICS.replace('| po_submitted |', f'| {bad} |'), INV)
                self.assertTrue(has(errs, part), errs)

    def test_row_values(self):
        spec = ANALYTICS.replace('| po_submitted | Submit returns 2xx | po-form | server |', '| po_submitted |  | — | backend |')
        errs, _ = run(verify.analytics_checks, spec, INV)
        for part in ('"trigger" is empty', 'Screen cannot be —', 'Source "backend"'):
            self.assertTrue(has(errs, part), part)

    def test_properties(self):
        cases = (('po_id: uuid', 'type "uuid"'), ('po_id string', 'must be name: type'), ('user_id: string', 'repeats a common'),
                 ('s: enum()', 'enum values'), ('s: enum(a/a)', 'repeats a value'), ('s: enum(A/b)', 'enum values'),
                 ('po_id: string, po_id: number', 'listed twice'))
        for props, part in cases:
            with self.subTest(props=props):
                spec = ANALYTICS.replace('po_id: string, amount: number, currency: string, line_count: integer', props)
                errs, _ = run(verify.analytics_checks, spec, INV)
                self.assertTrue(has(errs, part), errs)

    def test_optional_marker_only_in_events(self):
        errs, _ = run(verify.analytics_checks, ANALYTICS.replace('| user_id | string |', '| user_id? | string |'), INV)
        self.assertTrue(has(errs, 'snake_case'))

    def test_property_limit(self):
        props = ', '.join(f'p{i}: string' for i in range(24))
        errs, _ = run(verify.analytics_checks, ANALYTICS.replace('screen_id: string', props), INV)
        self.assertTrue(has(errs, '26 properties', 'limit is 25'))

    def test_req_id(self):
        _, warns = run(verify.analytics_checks, ANALYTICS.replace('| R3 |', '| R9 |'), INV)
        self.assertTrue(has(warns, 'R9', 'po-form'))
        _, warns = run(verify.analytics_checks, ANALYTICS.replace('| screen_id: string | — |', '| screen_id: string | R9 |'), INV)
        self.assertFalse(has(warns, 'R9'))  # Screen * skips the inventory comparison
        errs, _ = run(verify.analytics_checks, ANALYTICS.replace('| R3 |', '|  |'), INV)
        self.assertTrue(has(errs, 'Req ID is empty'))


class Charts(unittest.TestCase):
    """R13."""
    def test_valid_is_clean(self):
        self.assertEqual(run(verify.charts_checks, CHARTS, DESIGN, IDS), ([], []))

    def test_values(self):
        spec = CHARTS.replace('| orders-by-status | po-list | How many orders wait at each status? | bar | x: status · y: count | chart-1 | yes |',
                              '| Orders | * |  | pie |  | chart-9 | maybe |')
        errs, warns = run(verify.charts_checks, spec, DESIGN, IDS)
        for part in ('kebab-case', 'Screen cannot be *', '"question" is empty', 'Type "pie"', '"data" is empty', 'Table fallback "maybe"'):
            self.assertTrue(has(errs, part), part)
        self.assertTrue(has(warns, 'chart-9'))

    def test_no_fallback_warns_and_duplicate_errors(self):
        errs, warns = run(verify.charts_checks, CHARTS.replace('| chart-1, chart-2 | yes |', '| chart-1, chart-2 | no |').replace('spend-trend', 'orders-by-status'), DESIGN, IDS)
        self.assertTrue(has(warns, 'no table fallback'))
        self.assertTrue(has(errs, 'listed twice'))


class EndToEnd(unittest.TestCase):
    """main(): a v2.0.0 project still fails only with Phase 1 errors; a full P1 + P2 project has no P2 errors."""
    P2_WORDS = ('Users & jobs', 'design-qa.md', 'Notifications', 'Assets', 'Analytics', 'Charts')

    def test_v2_project_gets_no_p2_errors(self):
        errs = p1.EndToEnd('run_main').run_main(p1.EndToEnd.DESIGN_V2, p1.EndToEnd.SPEC_V2)
        self.assertTrue(has(errs, 'Roles & permissions'))
        self.assertFalse([e for e in errs if any(w in e for w in self.P2_WORDS)])

    def test_full_p2_project_has_no_p2_errors(self):
        spec = p1.EndToEnd.SPEC_V2.replace('## Screens', p1.ROLES.split('## Screens')[0] + '## Screens') \
            .replace('## Accessibility notes\n', p1.AC + p1.A11Y)
        spec = spec.replace('## User flow', USERS.split('## User flow')[0].replace('new-requester | requester, guest', 'new-requester | buyer')
                            + '## User flow')
        spec += NOTIF.replace('approver | push', 'buyer | push').split('## Analytics events')[0] + ANALYTICS + CHARTS
        spec = spec.replace('busy-approver | approver |', 'busy-approver | buyer |')
        design = p1.INVENTORY.replace('| not-found |', '| po-detail | Detail | Purchasing | ✅ | ✅ | R2 | MVP | draft | |\n'
                                      '| po-form | Form | Purchasing | ✅ | ✅ | R3 | MVP | draft | |\n| not-found |') \
            .replace('## 8. Next\n', '') + DESIGN.split('# Procura — Design System\n')[1]
        errs = p1.EndToEnd('run_main').run_main(design, spec)
        p2_errs = [e for e in errs if any(w in e for w in self.P2_WORDS)]
        self.assertEqual(p2_errs, [])


if __name__ == '__main__':
    unittest.main()
