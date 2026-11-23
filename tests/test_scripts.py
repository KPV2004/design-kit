"""Unit tests for the skill's Python scripts (no browser needed).

Run: python -m unittest discover -s tests -p 'test_scripts.py'
"""
import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'skills' / 'design-kit' / 'scripts'))
verify = importlib.import_module('verify')
export_tokens = importlib.import_module('export_tokens')

DESIGN = """# T — Design System
> Version: 1.0 · Dark mode: yes — light + dark

### 2.2 Neutral scale
| Token | Hex | Usage |
|---|---|---|
| neutral-50 | #f8fafc | Page |
| neutral-900 | #0f172a | Ink |

### 2.3 Semantic colors
| Token | 50 (bg) | 600 (main) | 700 (text) | Usage |
|---|---|---|---|---|
| danger | #fef2f2 | #dc2626 | #b91c1c | Errors |

### 2.4 Usage tokens
| Token | Light | Dark | Where |
|---|---|---|---|
| bg-page | neutral-50 | #020617 | App background |

### 2.9 Theme variants (mock theme picker)
| Theme | Token | Value |
|---|---|---|
| Teal | neutral-50 | #000000 |
"""


class TokenParsing(unittest.TestCase):
    # Regression (1.2.1): "| bg-page | neutral-50 | #020617 |" was read as neutral-50 = #020617
    def test_verify_ignores_value_columns(self):
        t = verify.design_tokens(DESIGN)
        self.assertEqual(t['neutral-50'], '#f8fafc')
        self.assertEqual(t['danger-700'], '#b91c1c')

    def test_export_ignores_value_columns(self):
        scales = export_tokens.parse(DESIGN)[0]
        self.assertEqual(scales['neutral'][50], '#f8fafc')
        self.assertEqual(scales['danger'][600], '#dc2626')

    def test_theme_rows_do_not_override_scales(self):
        self.assertEqual(verify.design_tokens(DESIGN)['neutral-50'], '#f8fafc')

    def test_usage_tokens_resolve(self):
        du = verify.design_usage(DESIGN)
        self.assertEqual(verify.resolve_ref(du['bg-page'], verify.design_tokens(DESIGN)), '#f8fafc')


class EngineVersion(unittest.TestCase):
    def run_check(self, stamp):
        verify.errors.clear(); verify.warns.clear()
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / '_engine').mkdir()
            if stamp is not None:
                (Path(d) / '_engine' / 'VERSION').write_text(stamp)
            verify.engine_version_check(Path(d))
        return list(verify.warns)

    def test_current_engine_is_quiet(self):
        self.assertEqual(self.run_check(verify.KIT_VERSION), [])

    def test_missing_stamp_warns(self):
        self.assertTrue(any('no VERSION stamp' in w for w in self.run_check(None)))

    def test_old_engine_warns(self):
        self.assertTrue(any('update_engine.py' in w for w in self.run_check('1.0.0')))

    def test_version_compare_is_numeric(self):
        self.assertLess(verify.vtuple('1.9.0'), verify.vtuple('1.10.0'))


class UsabilityPlan(unittest.TestCase):
    TASK = "### T{n} Task {n}\n- **Scenario:** \"Do it\"\n- **Screens:** [{sid}]\n- **Success:** done\n\n"

    def run_check(self, body):
        verify.errors.clear(); verify.warns.clear()
        with tempfile.TemporaryDirectory() as d:
            if body is not None:
                (Path(d) / 'usability-test.md').write_text('# Plan\n\n## Tasks\n' + body + '## Measures\n')
            verify.usability_checks(Path(d), {'login', 'po-list'})
        return list(verify.errors), list(verify.warns)

    def test_five_valid_tasks_pass(self):
        body = ''.join(self.TASK.format(n=n, sid='po-list') for n in range(1, 6))
        self.assertEqual(self.run_check(body), ([], []))

    def test_too_few_tasks(self):
        errs, _ = self.run_check(''.join(self.TASK.format(n=n, sid='login') for n in range(1, 4)))
        self.assertTrue(any('3 task(s)' in e for e in errs))

    def test_unknown_screen_and_missing_success(self):
        body = ''.join(self.TASK.format(n=n, sid='login') for n in range(1, 5))
        body += "### T5 Broken\n- **Screens:** [ghost-screen]\n\n"
        errs, _ = self.run_check(body)
        self.assertTrue(any('ghost-screen' in e for e in errs))
        self.assertTrue(any('no **Success:**' in e for e in errs))

    def test_missing_file_warns(self):
        _, warns = self.run_check(None)
        self.assertTrue(any('usability-test.md' in w for w in warns))


class VersionsInSync(unittest.TestCase):
    """plugin.json is the source of truth; tools/release.sh writes the other two."""
    def test_all_versions_match(self):
        plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text())['version']
        engine = (ROOT / 'skills/design-kit/assets/project/_engine/VERSION').read_text().strip()
        self.assertEqual(engine, plugin, '_engine/VERSION ≠ plugin.json')
        self.assertEqual(verify.KIT_VERSION, plugin, 'verify.KIT_VERSION ≠ plugin.json')


if __name__ == '__main__':
    unittest.main()
