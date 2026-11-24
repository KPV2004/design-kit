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

    def test_similar_headings_are_ignored(self):
        design = ('### Motion notes\n' + table(('duration-x', '50ms'))
                  + '\n### Breakpoints and grids\n' + table(('wide', '2000px'))
                  + '\n### Z-index exceptions\n' + table(('popup', '9999')))
        tokens, skipped = layout(design)
        self.assertEqual(tokens, {'motion': {}, 'breakpoints': {}, 'zIndex': {}})
        self.assertEqual(skipped, [])

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

    def test_non_token_table_under_heading_is_not_read(self):
        design = ('### 4.2 Breakpoints\n| Device | Width |\n|---|---|\n| iPhone | 390 |\n\n'
                  + table(('md', '768px')))
        tokens, skipped = layout(design)
        self.assertEqual(tokens['breakpoints'], {})
        self.assertEqual(skipped, [])

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
