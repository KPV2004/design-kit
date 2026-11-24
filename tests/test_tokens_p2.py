"""Phase 2 (R14) tests: export_tokens finds the §4.x token tables by exact heading, not substring.

Run: python3 -m unittest discover -s tests -p 'test_tokens_p2.py'
"""
import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'skills' / 'design-kit' / 'scripts'))
export_tokens = importlib.import_module('export_tokens')

TABLE = """| Token | Value | Usage |
|---|---|---|
{rows}
"""


def table(*rows):
    return TABLE.format(rows='\n'.join(f'| {t} | {v} | x |' for t, v in rows))


def layout(design):
    return export_tokens.layout_tokens(design)


class ExactHeadings(unittest.TestCase):
    def test_parent_section_table_is_not_read_as_motion(self):
        # Code review P1 #2: "## 4. … motion, layers" contains "motion"; a table there was read as motion
        design = ('## 4. Spacing, radius, elevation, motion, layers\n'
                  + table(('duration-oops', '999ms'), ('space-4', '16px'))
                  + '\n### 4.1 Motion tokens\n' + table(('duration-fast', '120ms')))
        tokens, skipped = layout(design)
        self.assertEqual(tokens['motion']['duration'], {'fast': 120})
        self.assertEqual(skipped, [])

    def test_similar_headings_are_not_read_but_warn(self):
        # QA ISSUE-R14-01: a near-miss heading with a Token table must not vanish silently
        design = ('### Motion notes\n' + table(('duration-x', '50ms'))
                  + '\n### Breakpoints and grids\n' + table(('wide', '2000px'))
                  + '\n### Z-index exceptions\n' + table(('popup', '9999')))
        tokens, skipped = layout(design)
        self.assertEqual(tokens, {'motion': {}, 'breakpoints': {}, 'zIndex': {}})
        self.assertEqual(len(skipped), 3)
        self.assertIn("rename it '### 4.1 Motion tokens'", skipped[0])
        self.assertIn("rename it '### 4.2 Breakpoints'", skipped[1])
        self.assertIn("rename it '### 4.3 Z-index (layers)'", skipped[2])

    def test_near_miss_heading_variants_warn(self):
        # QA ISSUE-R14-01 reproductions + singular/other wording
        for head, canonical in (('### 4.1 Motion & easing', '4.1 Motion tokens'),
                                ('### 4.1 Motion tokens (web)', '4.1 Motion tokens'),
                                ('### Breakpoint tokens', '4.2 Breakpoints'),
                                ('### Layers & stacking', '4.3 Z-index (layers)')):
            with self.subTest(head=head):
                tokens, skipped = layout(head + '\n' + table(('duration-fast', '120ms')))
                self.assertEqual(tokens['motion'], {})
                self.assertEqual(len(skipped), 1)
                self.assertIn(head, skipped[0])
                self.assertIn(canonical, skipped[0])

    def test_prose_only_similar_heading_is_quiet(self):
        self.assertEqual(layout('### Motion notes\nKeep animations subtle.\n')[1], [])

    def test_other_heading_levels_are_ignored(self):
        design = '## Motion\n' + table(('duration-a', '10ms')) + '\n#### Breakpoints\n' + table(('sm', '640px'))
        tokens, _ = layout(design)
        self.assertEqual(tokens['motion'], {})
        self.assertEqual(tokens['breakpoints'], {})

    def test_accepted_heading_forms(self):
        for motion, bps, z in (('### 4.1 Motion tokens', '### 4.2 Breakpoints', '### 4.3 Z-index (layers)'),
                               ('### Motion', '### breakpoints', '### Z-INDEX'),
                               ('### 4.1. Motion tokens ###', '###\t4.2\tBreakpoints', '### 4.3 Layers')):
            with self.subTest(motion=motion):
                design = (f'{motion}\n' + table(('duration-fast', '120ms'))
                          + f'\n{bps}\n' + table(('md', '768px'))
                          + f'\n{z}\n' + table(('modal', '400')))
                tokens, skipped = layout(design)
                self.assertEqual(tokens['motion']['duration'], {'fast': 120})
                self.assertEqual(tokens['breakpoints'], {'md': 768})
                self.assertEqual(tokens['zIndex'], {'modal': 400})
                self.assertEqual(skipped, [])


class TableSelection(unittest.TestCase):
    def test_only_first_token_table_under_heading(self):
        design = ('### 4.3 Z-index (layers)\n' + table(('modal', '400'))
                  + '\nLegacy values kept for reference:\n\n' + table(('old-modal', '50')))
        self.assertEqual(layout(design)[0]['zIndex'], {'modal': 400})

    def test_token_table_after_another_table_is_read(self):
        # QA ISSUE-R14-01 case 3: a note table before the Token table no longer hides it
        design = ('### 4.2 Breakpoints\n| Device | Width |\n|---|---|\n| iPhone | 390 |\n\n'
                  + table(('md', '768px')))
        tokens, skipped = layout(design)
        self.assertEqual(tokens['breakpoints'], {'md': 768})
        self.assertEqual(skipped, [])

    def test_exact_heading_without_token_table_warns(self):
        # QA ISSUE-R14-01 case 4: first column "Name" instead of "Token"
        design = '### 4.1 Motion tokens\n' + table(('duration-fast', '120ms')).replace('| Token |', '| Name |')
        tokens, skipped = layout(design)
        self.assertEqual(tokens['motion'], {})
        self.assertEqual(len(skipped), 1)
        self.assertIn('has no | Token | Value | table', skipped[0])

    def test_exact_heading_with_empty_token_table_warns(self):
        design = '### 4.3 Z-index (layers)\n| Token | Value | Usage |\n|---|---|---|\n'
        self.assertIn('empty Token table', layout(design)[1][0])

    def test_warnings_reach_stderr(self):
        import contextlib, io, tempfile
        colors = '### 2.2 Neutral scale\n| Token | Hex |\n|---|---|\n| neutral-50 | #f8fafc |\n'
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'design.md').write_text(colors + '\n### 4.1 Motion & easing\n'
                                               + table(('duration-fast', '120ms')), encoding='utf-8')
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                export_tokens.main(str(Path(d) / 'design.md'), str(Path(d) / 'out'))
        self.assertIn("WARN '### 4.1 Motion & easing' looks like a §4 token table", err.getvalue())

    def test_table_ends_at_next_heading(self):
        design = '### 4.1 Motion tokens\n' + table(('duration-fast', '120ms')) + '\n## 5. Components\n' \
                 + table(('duration-leak', '1ms'))
        self.assertEqual(layout(design)[0]['motion']['duration'], {'fast': 120})


class Unchanged(unittest.TestCase):
    def test_example_and_template_still_parse(self):
        for path in ('examples/procura-design/design.md', 'skills/design-kit/assets/project/design.md'):
            with self.subTest(path=path):
                tokens, skipped = layout((ROOT / path).read_text(encoding='utf-8'))
                self.assertEqual(skipped, [])
                self.assertEqual(list(tokens['breakpoints']), ['sm', 'md', 'lg', 'xl'])
                self.assertEqual(set(tokens['motion']['duration']), {'fast', 'base', 'slow'})
                self.assertIn('modal', tokens['zIndex'])


if __name__ == '__main__':
    unittest.main()
