#!/usr/bin/env python3
"""Browser tests for the review engines, run against the template and examples/procura-design.

Run: python tests/test_browser.py          (needs: pip install playwright && playwright install chromium)

Checks, each on a real Chromium page:
  - no JS errors in wireframes.html / mock.html (shell and frame mode)
  - the wireframe Components page renders every wf-* block
  - the mock State dropdown shows exactly the chosen data-state variant (Default / Empty / Loading / Error)
  - every visible text element on every mock screen and the component gallery is >= 4.5:1
    in every theme, at desktop and mobile widths
Color swatches on the design-system page are skipped: they show each color with its own ratio.
Exit code 1 on any failure.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = {
    'template': ROOT / 'skills/design-kit/assets/project',
    'example': ROOT / 'examples/procura-design',
}
failures = []

# Contrast of each element's own text vs the first opaque background behind it.
CONTRAST_JS = """(sel) => {
  const ch = s => s.match(/[\\d.]+/g).map(Number);
  const lum = ([r, g, b]) => [r, g, b].map(c => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; })
                                      .reduce((a, c, i) => a + c * [0.2126, 0.7152, 0.0722][i], 0);
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const v = ch(getComputedStyle(e).backgroundColor);
                       if (v.length < 4 || v[3] > 0.5) return v; } return [255, 255, 255]; };
  const out = [];
  document.querySelectorAll(sel + ' *').forEach(el => {
    if (!el.offsetParent || el.closest('[disabled], .anno, [data-state]:not(.show), pre, .hidden, #swatches')) return;
    if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
    const [a, b] = [lum(ch(getComputedStyle(el).color)), lum(bgOf(el))].sort((x, y) => y - x);
    const r = (a + 0.05) / (b + 0.05);
    if (r < 4.5) out.push(`${el.tagName.toLowerCase()}.${(el.className || '').toString().split(' ').slice(0, 3).join('.')} "${el.textContent.trim().slice(0, 24)}" ${r.toFixed(2)}:1`);
  });
  return [...new Set(out)];
}"""


def fail(msg):
    failures.append(msg)
    print('FAIL', msg)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        def page(width=1440, height=900, theme=None):
            pg = browser.new_page(viewport={'width': width, 'height': height})
            pg.on('pageerror', lambda e, pg=pg: fail(f'JS error on {pg.url}: {e}'))
            if theme:
                pg.add_init_script(f"localStorage.setItem('mk-theme', {theme!r})")
            return pg

        for name, root in PROJECTS.items():
            uri = root.resolve().as_uri()

            # Wireframes: loads, Components page lists the kit
            pg = page()
            pg.goto(f'{uri}/wireframes.html#components')
            pg.wait_for_timeout(2000)
            n = pg.evaluate("document.querySelectorAll('#components .cp-item').length")
            if n < 30:
                fail(f'{name}: wireframe Components page shows {n} blocks (expected ≥ 30)')
            pg.close()

            # Mock shell: state switcher shows exactly one variant per state
            pg = page()
            pg.goto(f'{uri}/mock.html')
            pg.wait_for_timeout(2500)
            frame = pg.frame_locator('#frame')
            screens = pg.evaluate("[...document.querySelectorAll('#screens > .screen')].map(s => s.id)")
            themes = pg.evaluate("[...document.querySelectorAll('#theme-select option')].map(o => o.value)")
            for sid in screens:
                has_states = pg.evaluate(f"document.querySelectorAll('[id=\"{sid}\"] [data-state]').length")
                if not has_states:
                    continue
                pg.select_option('#screen-select', sid)
                pg.wait_for_timeout(300)
                for opt in pg.evaluate("[...document.querySelectorAll('#state-select option')].map(o => o.value)"):
                    pg.select_option('#state-select', opt)
                    pg.wait_for_timeout(200)
                    shown = frame.locator(f'[id="{sid}"] [data-state]').evaluate_all(
                        'els => els.filter(e => e.offsetParent !== null).map(e => e.dataset.state)')
                    available = frame.locator(f'[id="{sid}"] [data-state]').evaluate_all('els => els.map(e => e.dataset.state)')
                    expect = [opt.lower()] if opt.lower() in available else ['default']
                    if shown != expect:
                        fail(f'{name} {sid}: State "{opt}" shows {shown}, expected {expect}')
                pg.select_option('#state-select', 'default')
            pg.close()

            # Contrast: every mock screen, every theme, desktop + mobile
            for theme in themes:
                for width, label in ((1440, 'desktop'), (390, 'mobile')):
                    pg = page(width, 844, theme)
                    pg.goto(f'{uri}/mock.html?frame=1')
                    pg.wait_for_timeout(1500)
                    for sid in screens:
                        pg.evaluate(f"showScreen('{sid}')")
                        pg.wait_for_timeout(150)
                        for item in pg.evaluate(CONTRAST_JS, f'[id="{sid}"]'):
                            fail(f'{name} {sid} [{theme}, {label}]: contrast {item}')
                    pg.close()
            print(f'ok  {name}: {len(screens)} mock screens × {len(themes)} themes × 2 widths')
        browser.close()

    print(f'\n{len(failures)} failure(s)')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
