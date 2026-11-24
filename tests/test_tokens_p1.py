"""Phase 1 (R5) tests: motion / breakpoint / z-index tokens in design.md §4 → tokens/.

Run: python3 -m unittest discover -s tests -p 'test_tokens_p1.py'
"""
import contextlib
import importlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / 'skills' / 'design-kit'
sys.path.insert(0, str(SKILL / 'scripts'))
export_tokens = importlib.import_module('export_tokens')

COLORS = """# T — Design System
### 2.2 Neutral scale
| Token | Hex | Usage |
|---|---|---|
| neutral-50 | #f8fafc | Page |
| neutral-900 | #0f172a | Ink |

### 2.4 Usage tokens
| Token | Light | Where |
|---|---|---|
| bg-page | neutral-50 | App background |
"""

SECTION4 = """
## 4. Spacing, radius, elevation, motion, layers
- Spacing scale (px): 4, 8, 12

### 4.1 Motion tokens
| Token | Value | Usage |
|---|---|---|
| duration-fast | 120ms | Hover |
| duration-slow | 0.3s | Dialogs |
| ease-standard | cubic-bezier(0.2,0,0,1) | Moves |
| ease-linear | linear | Progress |

### 4.2 Breakpoints
| Token | Min width | Usage |
|---|---|---|
| sm | 640px | Phones |
| md | 768 | Tablet |
| lg | 1024px | Laptop |

### 4.3 Z-index (layers)
| Token | Value | Usage |
|---|---|---|
| base | 0 | Page |
| z-modal | 400 | Dialogs |
| toast | 500 | Toasts |

## 5. Components
| Token | Value | Usage |
|---|---|---|
| not-a-layer | 999 | must not leak from §5 |
"""


def export(design):
    """Run export_tokens.main on a design string → (css, tailwind js, json dict, stderr)."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'design.md'
        p.write_text(design, encoding='utf-8')
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            export_tokens.main(str(p), str(Path(d) / 'out'))
        out = Path(d) / 'out'
        return ((out / 'tokens.css').read_text(), (out / 'tailwind.config.js').read_text(),
                json.loads((out / 'tokens.json').read_text()), err.getvalue())


class LayoutParsing(unittest.TestCase):
    def setUp(self):
        self.tokens, self.skipped = export_tokens.layout_tokens(COLORS + SECTION4)

    def test_durations_in_ms(self):
        self.assertEqual(self.tokens['motion']['duration'], {'fast': 120, 'slow': 300})

    def test_easings_normalized(self):
        self.assertEqual(self.tokens['motion']['easing'],
                         {'standard': 'cubic-bezier(0.2, 0, 0, 1)', 'linear': 'linear'})

    def test_breakpoints_px_with_or_without_unit(self):
        self.assertEqual(self.tokens['breakpoints'], {'sm': 640, 'md': 768, 'lg': 1024})

    def test_zindex_prefix_stripped_and_other_sections_ignored(self):
        self.assertEqual(self.tokens['zIndex'], {'base': 0, 'modal': 400, 'toast': 500})

    def test_parent_heading_mentioning_motion_does_not_hide_table(self):
        # Regression: "## 4. … motion, layers" matched first and returned no rows
        self.assertTrue(self.tokens['motion']['duration'])
        self.assertEqual(self.skipped, [])

    def test_invalid_rows_are_skipped_with_message(self):
        bad = SECTION4.replace('| 120ms |', '| fast |').replace('| 400 |', '| high |')
        tokens, skipped = export_tokens.layout_tokens(COLORS + bad)
        self.assertNotIn('fast', tokens['motion']['duration'])
        self.assertNotIn('modal', tokens['zIndex'])
        self.assertEqual(len(skipped), 2)

    def test_descending_breakpoints_flagged_and_sorted(self):
        bad = SECTION4.replace('| sm | 640px |', '| sm | 900px |')
        tokens, skipped = export_tokens.layout_tokens(COLORS + bad)
        self.assertTrue(any('ascending' in s for s in skipped))
        self.assertEqual(list(tokens['breakpoints']), ['md', 'sm', 'lg'])


class Outputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css, cls.tw, cls.json, cls.err = export(COLORS + SECTION4)

    def test_css_custom_properties(self):
        for line in ('--duration-fast: 120ms;', '--duration-slow: 300ms;',
                     '--ease-standard: cubic-bezier(0.2, 0, 0, 1);',
                     '--breakpoint-md: 768px;', '--z-modal: 400;'):
            self.assertIn(line, self.css)

    def test_css_reduced_motion_zeroes_durations(self):
        block = self.css.split('@media (prefers-reduced-motion: reduce)', 1)[1]
        self.assertIn('--duration-fast: 0ms;', block)
        self.assertIn('--duration-slow: 0ms;', block)

    def test_tailwind_sections(self):
        self.assertRegex(self.tw, r'screens: \{\s*"sm": "640px",\s*"md": "768px",\s*"lg": "1024px"\s*\}')
        self.assertRegex(self.tw, r'transitionDuration: \{\s*"fast": "120ms"')
        self.assertRegex(self.tw, r'transitionTimingFunction: \{\s*"standard": "cubic-bezier\(0.2, 0, 0, 1\)"')
        self.assertRegex(self.tw, r'zIndex: \{\s*"base": "0"')
        # screens sit in theme (replace defaults), the rest in theme.extend
        self.assertLess(self.tw.index('screens:'), self.tw.index('extend:'))
        self.assertGreater(self.tw.index('zIndex:'), self.tw.index('extend:'))

    @unittest.skipUnless(shutil.which('node'), 'node not installed')
    def test_tailwind_config_is_valid_js(self):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
            f.write(self.tw)
        try:
            r = subprocess.run(['node', '-e', f'const c=require({json.dumps(f.name)});'
                                'console.log(JSON.stringify([c.theme.screens, c.theme.extend.zIndex]))'],
                               capture_output=True, text=True, timeout=30)
        finally:
            Path(f.name).unlink()
        self.assertEqual(r.returncode, 0, r.stderr)
        screens, z = json.loads(r.stdout)
        self.assertEqual(screens['lg'], '1024px')
        self.assertEqual(z['modal'], '400')

    def test_json_numbers_for_native_stacks(self):
        self.assertEqual(self.json['motion']['duration']['slow'], 300)
        self.assertEqual(self.json['breakpoints']['md'], 768)
        self.assertEqual(self.json['zIndex']['toast'], 500)
        self.assertEqual(self.json['neutral-50'], '#f8fafc')  # colors unchanged

    def test_no_warnings_for_valid_tables(self):
        self.assertEqual(self.err, '')


class BackwardCompatibility(unittest.TestCase):
    def test_design_without_section4_tables_exports_colors_only(self):
        css, tw, data, err = export(COLORS)
        self.assertNotIn('--duration', css)
        self.assertNotIn('prefers-reduced-motion', css)
        self.assertNotIn('screens', tw)
        self.assertNotIn('zIndex', tw)
        self.assertFalse({'motion', 'breakpoints', 'zIndex'} & set(data))
        self.assertEqual(err, '')

    def test_invalid_row_warns_on_stderr(self):
        err = export(COLORS + SECTION4.replace('| 0 |', '| auto |'))[3]
        self.assertIn("WARN skipped z-index 'base'", err)


class Template(unittest.TestCase):
    """The shipped template's §4 tables must parse cleanly (they are what designers copy)."""

    def test_template_section4_parses_without_skips(self):
        tpl = (SKILL / 'assets' / 'project' / 'design.md').read_text(encoding='utf-8')
        tokens, skipped = export_tokens.layout_tokens(tpl)
        self.assertEqual(skipped, [])
        self.assertTrue({'fast', 'base', 'slow'} <= set(tokens['motion']['duration']))
        self.assertTrue({'standard', 'enter', 'exit'} <= set(tokens['motion']['easing']))
        self.assertEqual(list(tokens['breakpoints']), ['sm', 'md', 'lg', 'xl'])
        z = tokens['zIndex']
        self.assertEqual(list(z.values()), sorted(z.values()))
        self.assertTrue({'dropdown', 'overlay', 'modal', 'toast'} <= set(z))

    def test_template_section4_rows_are_not_read_as_colors(self):
        tpl = (SKILL / 'assets' / 'project' / 'design.md').read_text(encoding='utf-8')
        sec4 = re.search(r'^## 4\..*?(?=^## 5\.)', tpl, re.S | re.M).group(0)
        self.assertEqual(export_tokens.parse(COLORS + sec4)[0], export_tokens.parse(COLORS)[0])


if __name__ == '__main__':
    unittest.main()
