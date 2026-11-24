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

# playwright is imported in main(), so `unittest discover` can import this file on machines without it

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = {
    'template': ROOT / 'skills/design-kit/assets/project',
    'example': ROOT / 'examples/procura-design',
}
failures = []

# Same contrast check verify.py runs, so the tests and the tool can't drift apart.
sys.path.insert(0, str(ROOT / 'skills/design-kit/scripts'))
from verify import CONTRAST_JS  # noqa: E402


def fail(msg):
    failures.append(msg)
    print('FAIL', msg)


def keyboard_checks(pg, name):
    def check(cond, what):
        if not cond:
            fail(f'{name} keyboard: {what}')
    active = lambda: pg.evaluate("document.activeElement.id || document.activeElement.textContent.trim()")
    # Tabs: arrow keys move selection and show the matching panel
    pg.focus('#g-tab-1'); pg.keyboard.press('ArrowRight')
    check(active() == 'g-tab-2', 'ArrowRight on a tab does not move focus to the next tab')
    check(pg.get_attribute('#g-tab-2', 'aria-selected') == 'true', 'focused tab is not selected')
    check(pg.is_visible('#g-panel-2') and not pg.is_visible('#g-panel-1'), 'tab panels do not follow the selected tab')
    pg.keyboard.press('End'); check(active() == 'g-tab-3', 'End does not jump to the last tab')
    # Menu: Enter opens and focuses the first item, arrows move, Esc closes and returns focus
    btn = '[aria-controls="g-menu"]'
    check(not pg.is_visible('#g-menu'), 'menu is open before it is triggered')
    pg.focus(btn); pg.keyboard.press('Enter')
    check(pg.is_visible('#g-menu') and pg.get_attribute(btn, 'aria-expanded') == 'true', 'Enter does not open the menu')
    check('Edit' in active(), 'opening the menu does not focus the first item')
    pg.keyboard.press('ArrowDown'); check('Delete' in active(), 'ArrowDown does not move to the next menu item')
    pg.keyboard.press('Escape')
    check(not pg.is_visible('#g-menu') and pg.evaluate(f"document.activeElement.matches('{btn}')"), 'Esc does not close the menu and return focus')
    # Dialog: openDialog moves focus in, Tab is trapped, Esc closes and returns focus to the opener
    opener = 'button:has-text("Delete order") >> nth=0'
    pg.click(opener)
    check(pg.evaluate("!!document.activeElement.closest('#g-dlg-wrap')"), 'openDialog does not move focus into the dialog')
    for _ in range(4):
        pg.keyboard.press('Tab')
    check(pg.evaluate("!!document.activeElement.closest('#g-dlg-wrap')"), 'Tab escapes the open dialog')
    pg.keyboard.press('Escape')
    check(not pg.is_visible('#g-dlg-wrap'), 'Esc does not close the dialog')
    check(pg.evaluate("document.activeElement.textContent.includes('Delete order')"), 'closing the dialog does not return focus to its opener')
    # Switch and single-select chips
    sw = '#component-gallery [role="switch"]'
    before = pg.get_attribute(sw, 'aria-checked'); pg.click(sw)
    check(pg.get_attribute(sw, 'aria-checked') != before, 'clicking a switch does not toggle aria-checked')
    pg.click('#component-gallery .mk-chip:has-text("Approved")')
    check(pg.evaluate("[...document.querySelectorAll('#component-gallery [data-select=single] .mk-chip[aria-pressed=true]')].map(c => c.textContent)") == ['Approved'],
          'single-select chips allow more than one pressed chip')


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('playwright is not installed — pip install playwright && playwright install chromium '
              '(or run ./tools/check.sh --fast to skip the browser tests)')
        return 1
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

            # Keyboard: WAI-ARIA patterns wired by the engine (component gallery on the design-system page)
            pg = page()
            pg.goto(f'{uri}/mock.html?frame=1#design-system:mock')
            pg.wait_for_timeout(2000)
            keyboard_checks(pg, name)
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
