"""Unit tests for the Phase 1 UX-gap checks in verify.py (docs/p1-schema.md): R1 roles, R2 Req ID + AC,
R3 Priority/Status, R6 accessibility table. No browser needed.

Run: python -m unittest discover -s tests -p 'test_verify_p1.py'
"""
import contextlib
import importlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'skills' / 'design-kit' / 'scripts'))
verify = importlib.import_module('verify')

INVENTORY = """## 7. Screen inventory
| ID | Screen | Module | Wireframe | Mockup | Req ID | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| login | Sign in | Auth | ✅ | ✅ | R1 | MVP | approved | |
| po-list | Purchase orders | Purchasing | ✅ | ✅ | R3, FR-01 | MVP | review | |
| not-found | Page not found | System | ✅ | — | — | Later | draft | |

## 8. Next
"""

ROLES = """## Roles & permissions
### Roles
| Role | Description |
|---|---|
| guest | not signed in |
| buyer | creates POs |

### Permission matrix
| Role | Screen | View | Create | Edit | Approve | Delete |
|---|---|---|---|---|---|---|
| * | not-found | ✅ | — | — | — | — |
| guest | login | ✅ | — | — | — | — |
| buyer | po-list | ✅ (own only) | ✅ | — | — | — |

## Screens
"""

AC = """## Acceptance criteria
| ID | Screen | Req ID | Given | When | Then |
|---|---|---|---|---|---|
| AC-01 | login | R1 | a user | they sign in | the list shows |
| AC-02 | po-list, not-found | R3 | a buyer | they open it | rows show |

## States
"""

A11Y = """## Accessibility
| Screen | Announce (aria-live) | Focus on open | Focus return | Tab order |
|---|---|---|---|---|
| login | assertive: sign-in error | email field | n/a | email → password → Sign in |
| po-list | polite: "12 results" · assertive: load error | h1 | menu → its button | search → rows |
| not-found | n/a | h1 | n/a | Go home |

### Global
- Target size ≥ 24×24
"""


def run(fn, *args):
    verify.errors.clear(); verify.warns.clear()
    fn(*args)
    return list(verify.errors), list(verify.warns)


def has(msgs, *parts):
    return any(all(p in m for p in parts) for m in msgs)


class Inventory(unittest.TestCase):
    """R2 Req ID + R3 Priority/Status; columns read by header name."""
    def inv(self, text=INVENTORY):
        verify.errors.clear(); verify.warns.clear()
        return verify.parse_inventory(text)

    def test_valid_inventory_is_clean(self):
        self.assertEqual(run(verify.inventory_checks, self.inv()), ([], []))

    def test_columns_read_by_header_not_position(self):
        # Regression (TC R2-06): new columns placed before Wireframe/Mockup must not shift them
        text = INVENTORY.replace('| ID | Screen | Module | Wireframe | Mockup | Req ID | Priority | Status |',
                                 '| ID | Screen | Module | Req ID | Priority | Status | Wireframe | Mockup |')
        text = text.replace('| ✅ | — | — | Later | draft |', '| — | Later | draft | ✅ | — |')
        inv = self.inv(text)
        self.assertTrue(inv['not-found']['wireframe'])
        self.assertFalse(inv['not-found']['mockup'])
        self.assertEqual(inv['not-found']['priority'], 'Later')

    def test_old_five_column_inventory_parses_and_errors(self):
        old = "## 7. Screen inventory\n| ID | Screen | Module | Wireframe | Mockup | Notes |\n|---|---|---|---|---|---|\n" \
              "| login | Sign in | Auth | ✅ | — | |\n"
        inv = self.inv(old)
        self.assertEqual(inv['login']['wireframe'], True)
        self.assertEqual(inv['login']['mockup'], False)
        errs, _ = run(verify.inventory_checks, inv)
        self.assertTrue(has(errs, '"Req ID" column') and has(errs, '"Priority" column') and has(errs, '"Status" column'))

    def test_bad_priority_status_are_case_sensitive(self):
        inv = self.inv(INVENTORY.replace('| MVP | approved |', '| mvp | Approved |'))
        errs, _ = run(verify.inventory_checks, inv)
        self.assertTrue(has(errs, 'login', 'Priority "mvp"'))
        self.assertTrue(has(errs, 'login', 'Status "Approved"'))

    def test_empty_priority_status_req_are_errors(self):
        inv = self.inv(INVENTORY.replace('| R1 | MVP | approved |', '|  |  |  |'))
        errs, _ = run(verify.inventory_checks, inv)
        self.assertTrue(has(errs, 'login', 'Req ID is empty'))
        self.assertTrue(has(errs, 'login', 'Priority ""'))
        self.assertTrue(has(errs, 'login', 'Status ""'))

    def test_bad_req_id_format(self):
        inv = self.inv(INVENTORY.replace('| R3, FR-01 |', '| r3, FR_01 |'))
        errs, _ = run(verify.inventory_checks, inv)
        self.assertTrue(has(errs, 'Req ID "r3"'))
        self.assertTrue(has(errs, 'Req ID "FR_01"'))

    def test_dash_req_id_warns_outside_system(self):
        inv = self.inv(INVENTORY.replace('| R1 | MVP |', '| — | MVP |'))
        errs, warns = run(verify.inventory_checks, inv)
        self.assertEqual(errs, [])
        self.assertTrue(has(warns, 'login', 'Module is "Auth"'))
        self.assertFalse(has(warns, 'not-found'))


IDS = {'login', 'po-list', 'not-found'}


class Roles(unittest.TestCase):
    """R1 role × screen × action matrix."""
    def test_valid_matrix_is_clean(self):
        self.assertEqual(run(verify.roles_checks, ROLES, IDS), ([], []))

    def test_missing_section_errors(self):
        errs, _ = run(verify.roles_checks, '## Screens\n', IDS)
        self.assertTrue(has(errs, 'Roles & permissions'))

    def test_undeclared_role_and_unknown_screen(self):
        spec = ROLES.replace('| buyer | po-list |', '| approver | ghost-screen |')
        errs, _ = run(verify.roles_checks, spec, IDS)
        self.assertTrue(has(errs, 'role "approver" is not declared'))
        self.assertTrue(has(errs, 'screen "ghost-screen"'))

    def test_role_case_matters(self):
        errs, _ = run(verify.roles_checks, ROLES.replace('| buyer | creates', '| Buyer | creates'), IDS)
        self.assertTrue(has(errs, 'role "Buyer" must be kebab-case'))
        self.assertTrue(has(errs, 'role "buyer" is not declared'))

    def test_duplicate_role_declaration(self):
        errs, _ = run(verify.roles_checks, ROLES.replace('| buyer | creates POs |', '| buyer | creates POs |\n| buyer | again |'), IDS)
        self.assertTrue(has(errs, 'declared twice'))

    def test_bad_cells(self):
        for bad in ('yes', '✅(own)', '-', ''):
            with self.subTest(cell=bad):
                errs, _ = run(verify.roles_checks, ROLES.replace('| ✅ (own only) |', f'| {bad} |'), IDS)
                self.assertTrue(has(errs, 'View', 'use ✅'), errs)

    def test_wildcards_and_lists(self):
        spec = ROLES.replace('| * | not-found |', '| * | * |').replace('| guest | login |', '| guest, buyer | login, not-found |')
        errs, warns = run(verify.roles_checks, spec, IDS)
        self.assertEqual(errs, [])
        self.assertFalse(has(warns, 'more than one row'))  # wildcard rows are defaults, not duplicates

    def test_duplicate_pair_and_uncovered_warn(self):
        spec = ROLES.replace('| * | not-found | ✅ | — | — | — | — |\n', '') + ''
        spec = spec.replace('| buyer | po-list | ✅ (own only) | ✅ | — | — | — |',
                            '| buyer | po-list | ✅ | — | — | — | — |\n| buyer | po-list | ✅ | ✅ | — | — | — |')
        errs, warns = run(verify.roles_checks, spec, IDS)
        self.assertEqual(errs, [])
        self.assertTrue(has(warns, '"buyer" × screen "po-list"'))
        self.assertTrue(has(warns, 'screen "not-found" is not covered'))

    def test_role_without_rows_warns(self):
        spec = ROLES.replace('| guest | login | ✅ | — | — | — | — |\n', '')
        _, warns = run(verify.roles_checks, spec, IDS)
        self.assertFalse(has(warns, 'role "guest" has no row'))  # the `*` row covers every role
        spec = spec.replace('| * | not-found |', '| buyer | not-found |')
        _, warns = run(verify.roles_checks, spec, IDS)
        self.assertTrue(has(warns, 'role "guest" has no row'))

    def test_empty_tables_error(self):
        spec = "## Roles & permissions\n### Roles\n| Role | Description |\n|---|---|\n\n### Permission matrix\n" \
               "| Role | Screen | View | Create | Edit | Approve | Delete |\n|---|---|---|---|---|---|---|\n"
        errs, _ = run(verify.roles_checks, spec, IDS)
        self.assertTrue(has(errs, '### Roles'))
        self.assertTrue(has(errs, '### Permission matrix'))

    def test_empty_role_cell_errors(self):
        # BUG-P1-01: a row with an empty Role was skipped silently
        errs, _ = run(verify.roles_checks, ROLES.replace('| guest | login |', '|  | login |'), IDS)
        self.assertTrue(has(errs, 'screen "login" has no Role'))

    def test_missing_action_column(self):
        errs, _ = run(verify.roles_checks, ROLES.replace(' Approve |', '').replace('| — | — | — | — |', '| — | — | — |'), IDS)
        self.assertTrue(has(errs, 'lacks column', 'approve'))


class AcceptanceCriteria(unittest.TestCase):
    """R2 Given/When/Then table + coverage of every inventory screen."""
    def inv(self):
        verify.errors.clear(); verify.warns.clear()
        return verify.parse_inventory(INVENTORY)

    def test_valid_ac_is_clean(self):
        self.assertEqual(run(verify.ac_checks, AC, self.inv()), ([], []))

    def test_missing_section_errors(self):
        errs, _ = run(verify.ac_checks, '## States\n', self.inv())
        self.assertTrue(has(errs, 'Acceptance criteria'))

    def test_screen_without_ac_is_error(self):
        errs, _ = run(verify.ac_checks, AC.replace('po-list, not-found', 'po-list'), self.inv())
        self.assertTrue(has(errs, 'no acceptance criterion', '"not-found"'))

    def test_shared_heading_does_not_count_as_ac(self):
        spec = '### [login] [po-list] Shared\n' + AC.replace('| AC-01 | login |', '| AC-01 | po-list |')
        errs, _ = run(verify.ac_checks, spec, self.inv())
        self.assertTrue(has(errs, 'no acceptance criterion', '"login"'))

    def test_bad_and_duplicate_ids(self):
        errs, _ = run(verify.ac_checks, AC.replace('AC-02', 'AC-01').replace('| AC-01 | login', '| AC-1 | login'), self.inv())
        self.assertTrue(has(errs, '"AC-1"', 'AC-01'))
        errs, _ = run(verify.ac_checks, AC.replace('AC-02', 'AC-01'), self.inv())
        self.assertTrue(has(errs, 'used twice'))

    def test_unknown_screen_and_empty_gwt(self):
        errs, _ = run(verify.ac_checks, AC.replace('| login | R1 | a user | they sign in |', '| ghost | R1 |  |  |'), self.inv())
        self.assertTrue(has(errs, 'screen "ghost"'))
        self.assertTrue(has(errs, 'Given is empty') and has(errs, 'When is empty'))

    def test_req_id_not_in_inventory_warns(self):
        errs, warns = run(verify.ac_checks, AC.replace('| login | R1 |', '| login | R9 |'), self.inv())
        self.assertEqual(errs, [])
        self.assertTrue(has(warns, 'AC-01', 'R9'))

    def test_bad_req_id_format_errors(self):
        errs, _ = run(verify.ac_checks, AC.replace('| login | R1 |', '| login | r1 |'), self.inv())
        self.assertTrue(has(errs, 'Req ID "r1"'))

    def test_empty_req_id_errors(self):
        # BUG-P1-02: empty Req ID must be — like the inventory, not blank
        errs, _ = run(verify.ac_checks, AC.replace('| login | R1 |', '| login |  |'), self.inv())
        self.assertTrue(has(errs, 'AC-01', 'Req ID is empty'))
        errs, _ = run(verify.ac_checks, AC.replace('| login | R1 |', '| login | — |'), self.inv())
        self.assertEqual(errs, [])

    def test_empty_screen_gives_no_req_warning(self):
        # SUG-P1-04: no "not listed for  in the inventory" noise next to the error
        errs, warns = run(verify.ac_checks, AC.replace('| AC-01 | login | R1 |', '| AC-01 |  | R1 |'), self.inv())
        self.assertTrue(has(errs, 'AC-01', 'has no Screen'))
        self.assertFalse(has(warns, 'AC-01'))

    def test_empty_then_errors(self):
        errs, _ = run(verify.ac_checks, AC.replace('| the list shows |', '|  |'), self.inv())
        self.assertTrue(has(errs, 'AC-01', 'Then is empty'))

    def test_missing_column_and_header_case(self):
        errs, _ = run(verify.ac_checks, AC.replace(' Given |', '').replace('| a user |', '|').replace('| a buyer |', '|'), self.inv())
        self.assertTrue(has(errs, 'lacks column', 'given'))
        self.assertEqual(run(verify.ac_checks, AC.replace('| Req ID |', '| req id |'), self.inv()), ([], []))

    def test_empty_table_errors(self):
        errs, _ = run(verify.ac_checks, '## Acceptance criteria\n| ID | Screen | Req ID | Given | When | Then |\n|---|---|---|---|---|---|\n', self.inv())
        self.assertTrue(has(errs, 'no rows'))


class Accessibility(unittest.TestCase):
    """R6 per-screen accessibility table."""
    def test_valid_table_is_clean(self):
        self.assertEqual(run(verify.a11y_checks, A11Y, IDS), ([], []))

    def test_old_heading_errors_with_rename_hint(self):
        errs, _ = run(verify.a11y_checks, '## Accessibility notes\nsome text\n', IDS)
        self.assertTrue(has(errs, 'Accessibility notes', 'rename'))

    def test_missing_section_errors(self):
        errs, _ = run(verify.a11y_checks, '## Risks\n', IDS)
        self.assertTrue(has(errs, '"## Accessibility"'))

    def test_empty_table_errors(self):
        spec = '## Accessibility\n| Screen | Announce (aria-live) | Focus on open | Focus return | Tab order |\n|---|---|---|---|---|\n'
        errs, _ = run(verify.a11y_checks, spec, IDS)
        self.assertTrue(has(errs, 'no rows'))

    def test_missing_screen_row_errors(self):
        errs, _ = run(verify.a11y_checks, A11Y.replace('| not-found | n/a | h1 | n/a | Go home |\n', ''), IDS)
        self.assertTrue(has(errs, 'no row for screen "not-found"'))

    def test_unknown_screen_and_empty_cell(self):
        errs, _ = run(verify.a11y_checks, A11Y.replace('| not-found | n/a | h1 | n/a |', '| ghost | n/a | h1 |  |'), IDS)
        self.assertTrue(has(errs, 'screen "ghost"'))
        self.assertTrue(has(errs, '"focus return" is empty'))

    def test_announce_without_prefix_warns(self):
        errs, warns = run(verify.a11y_checks, A11Y.replace('assertive: sign-in error', 'sign-in error'), IDS)
        self.assertEqual(errs, [])
        self.assertTrue(has(warns, 'login', 'polite: or assertive:'))

    def test_duplicate_screen_row_warns(self):
        # SUG-P1-03
        spec = A11Y.replace('| not-found | n/a | h1 | n/a | Go home |\n', '| not-found | n/a | h1 | n/a | Go home |\n| login | n/a | h1 | n/a | x |\n')
        errs, warns = run(verify.a11y_checks, spec, IDS)
        self.assertEqual(errs, [])
        self.assertTrue(has(warns, 'screen "login" has more than one row'))

    def test_several_ids_in_one_row_error(self):
        errs, _ = run(verify.a11y_checks, A11Y.replace('| not-found | n/a |', '| not-found, login | n/a |'), IDS)
        self.assertTrue(has(errs, 'one screen ID per row'))

    def test_missing_column_errors(self):
        spec = A11Y.replace(' Tab order |', '').replace('|---|---|---|---|---|', '|---|---|---|---|')
        errs, _ = run(verify.a11y_checks, spec, IDS)
        self.assertTrue(has(errs, 'lacks column', 'tab order'))

    def test_global_bullets_are_ignored(self):
        spec = A11Y + '| stray | table | under | global | x |\n'
        self.assertEqual(run(verify.a11y_checks, spec, IDS), ([], []))


class EndToEnd(unittest.TestCase):
    """main() on a full project folder: a v2.0.0-format project (no Phase 1 sections) fails with the R1/R2/R3/R6
    errors (breaking change, user decision 2026-11-24), and passes once the sections are added."""
    SPEC_V2 = """# T — UX Spec
## User flow
```mermaid
flowchart LR
  a --> b
```
## Screens
### [login] Sign in
### [po-list] Purchase orders
### [not-found] Page not found
## Accessibility notes
"""
    DESIGN_V2 = INVENTORY.replace(' Req ID | Priority | Status |', '').replace('|---|---|---|---|---|---|---|---|---|', '|---|---|---|---|---|---|') \
        .replace('| R1 | MVP | approved |', '').replace('| R3, FR-01 | MVP | review |', '').replace('| — | Later | draft |', '')

    def run_main(self, design, spec):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'design.md').write_text(design)
            (d / 'ux-spec.md').write_text(spec)
            for name in ('wireframes.html', 'mock.html'):
                (d / name).write_text('')
            verify.errors.clear(); verify.warns.clear()
            orig = verify.browser_checks
            verify.browser_checks = lambda *a, **k: None
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    verify.main(d)
            finally:
                verify.browser_checks = orig
            return list(verify.errors)

    def test_v2_project_fails_with_p1_errors(self):
        errs = self.run_main(self.DESIGN_V2, self.SPEC_V2)
        for part in ('"Req ID" column', '"Priority" column', '"Status" column',
                     'Roles & permissions', 'Acceptance criteria', 'Accessibility notes'):
            self.assertTrue(has(errs, part), part)

    def test_p1_project_has_no_p1_errors(self):
        spec = self.SPEC_V2.replace('## Screens', ROLES.split('## Screens')[0] + '## Screens').replace('## Accessibility notes\n', AC + A11Y)
        errs = self.run_main(INVENTORY, spec)
        p1 = [e for e in errs if any(k in e for k in ('Req ID', 'Priority', 'Status', 'Role', 'Permission', 'AC', 'acceptance', 'Accessibility'))]
        self.assertEqual(p1, [])


if __name__ == '__main__':
    unittest.main()
