# Mobile App Patterns

Users are one-handed, interrupted, often on poor connections. Optimize for thumbs, glanceability, and resilience.

## Frame
- Design at 390×844 inside the template's phone frame. Respect safe areas (status bar, home indicator).
- Touch targets ≥ 44×44px; spacing between targets ≥ 8px.

## Navigation
- Bottom tab bar for 3–5 top-level destinations. Primary action reachable by thumb (bottom area or FAB).
- Back always available on pushed screens; don't rely on swipe-only gestures.

## Input
- Use the right keyboard (numeric for amounts, tel, email). Avoid typing where a picker, toggle, or scan works.
- Amount entry: large numeric display, quick presets when helpful.
- Bottom sheets for short choices; full screen for long forms.

## Lists & content
- One primary line, one secondary line, trailing value/status. Swipe actions only as shortcuts — also offer them in a menu.
- Pull to refresh; show last-updated time.

## Offline & connectivity
- Show offline banner; queue actions and show pending sync state per item. Spec what happens on conflict.

## Feedback
- Skeletons for loading; optimistic updates with rollback on failure.
- Haptic/visual confirmation for completed actions; snackbars with Undo for reversible deletes.

## Pitfalls
- Desktop tables squeezed onto mobile — convert to cards or key-value rows.
- Important actions in the top corners (hard to reach).
- Tiny text: body ≥ 16px; Thai text needs extra line-height (leading-relaxed).
