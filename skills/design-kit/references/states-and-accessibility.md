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

## Thai-specific
- Thai text needs more line-height (`leading-relaxed`) — tone marks get clipped with tight leading.
- Thai has no spaces between words, so truncation/wrapping can break mid-word; allow 2 lines or use `break-words` and test with long real names.
- Specify date era (พ.ศ./ค.ศ.) and number formatting in the spec.
