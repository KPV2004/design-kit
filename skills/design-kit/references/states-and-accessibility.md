# States & Accessibility Checklist

Run through this before delivering. Mockups usually show only the happy path; real products spend much of their life elsewhere.

## States every data screen needs
- **Empty (first use):** explain what goes here + primary action to create the first item.
- **Empty (no results):** say why and how to fix (clear filters).
- **Loading:** skeleton matching final layout (avoid layout jump); for > 3s show progress text.
- **Error:** what happened in plain words + what to do ("โหลดข้อมูลไม่สำเร็จ ลองใหม่อีกครั้ง" + ปุ่มลองใหม่). Never show raw exception text.
- **Partial:** some data loaded, some failed.
- **Success:** confirmation after an action.
- **Permission denied / read-only:** if roles exist.
- **Edge data:** very long text, zero, negative, huge numbers, missing optional fields.

## Action states
Buttons: default, hover, focus, disabled (with reason), loading (spinner + label, prevents double click).

## Accessibility (WCAG AA baseline)
- Text contrast ≥ 4.5:1 (≥ 3:1 for large text and UI components). Don't use color alone for status — add icon or text.
- Visible focus ring on every interactive element (template uses `focus-visible:ring-2`).
- Every input has a visible label; placeholders are not labels.
- Error messages are next to the field and describe the fix.
- Logical heading order; buttons are `<button>`, links are `<a>`.
- Keyboard: everything reachable and operable; modals trap focus and close on Esc.

## Beyond contrast — what the spec's Accessibility table must answer
Every inventory screen gets a row in ux-spec.md `## Accessibility` (`Screen | Announce (aria-live) | Focus on open | Focus return | Tab order`); no empty cells, `n/a` where nothing applies.

- **Announcements (aria-live).** Anything that changes without moving focus must be announced: result counts after filtering, "Saved", toasts, inline async errors. `polite` for status, `assertive` only for errors that block the task. Write the exact text (from the copy deck). Never announce on every keystroke — debounce search counts.
- **Focus on open.** New page → the `h1` (or the first field on a form whose only job is input, e.g. sign-in). Dialog / bottom sheet → the first field, or the least destructive button in a confirm dialog — never the destructive one.
- **Focus return.** Closing a dialog, sheet or menu returns focus to the control that opened it. After Save that navigates, focus lands on the new page's `h1` or the highlighted new row; after Save that stays, on the success message or the first field in error. After deleting a row, the next row (or the list heading when empty).
- **Tab order.** Follows the visual reading order (top → bottom, start → end). List the landmarks, not every link: `search → filters → table rows → pagination`. Sticky action bars come last in DOM order on mobile only if they are also visually last.
- **Target size (WCAG 2.2 SC 2.5.8).** ≥ 24×24 CSS px with spacing, as the legal minimum; the kit uses 40px (44px on touch). Inline text links are exempt.
- **Zoom & reflow (SC 1.4.4 / 1.4.10).** Usable at 200% zoom; at 320px width no horizontal scrolling except for data tables and code. No `maximum-scale=1` in the viewport.
- **Dynamic type (mobile).** Layouts hold at the OS's largest text size: no fixed heights on text containers, labels wrap rather than truncate, icons don't scale past their touch target. Test the mock at 200% browser zoom as a proxy.
- **Focus not obscured (SC 2.4.11).** Sticky headers/footers and toasts never cover the focused element — add scroll padding equal to their height.
- **Reduced motion.** Under `prefers-reduced-motion: reduce` the motion tokens export as 0ms; no information may live only in an animation.
- **Errors (SC 3.3.1 / 3.3.3).** Field error linked with `aria-describedby`, field has `aria-invalid`; on submit failure with several errors, show an error summary that receives focus and links to each field.

## Thai-specific
- Thai text needs more line-height (`leading-relaxed`) — tone marks get clipped with tight leading.
- Thai has no spaces between words, so truncation/wrapping can break mid-word; allow 2 lines or use `break-words` and test with long real names.
- Specify date era (พ.ศ./ค.ศ.) and number formatting in the spec.
