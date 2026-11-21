# Customer-facing Web App Patterns

Users are often first-time or occasional. Optimize for clarity, trust, and getting to value fast.

## Navigation & layout
- Top nav for ≤ 6 sections; sidebar for more or for app-like products.
- Content width max ~1200px; reading text max ~70 characters per line.
- Show desktop (1280px) and mobile (390px) versions of key screens.

## Onboarding & sign-up
- Ask only what's needed now; defer the rest.
- Social/SSO above email if supported. Show password rules before the user fails them.
- After sign-up, land on a screen with one clear next step, not an empty dashboard.

## Forms
- Single column. Inline validation on blur, not on every keystroke.
- Multi-step forms: progress indicator with step names, back without data loss, review step before submit.
- Error summary at top with links to fields on submit failure.

## Trust & feedback
- Confirm success specifically ("ส่งคำสั่งซื้อ #10234 แล้ว — ยืนยันทางอีเมล").
- Show pricing, fees, and what happens next before commitment.
- Toasts for minor confirmations; inline banners for things that need reading.

## Search & browse
- Search with suggestions; results page with filters (sidebar on desktop, sheet on mobile) and sort.
- Cards for visual items, list rows for comparable items.

## Pitfalls
- Hero sections that push the actual task below the fold.
- Modals for long content or multi-step tasks — use a page.
- Disabled submit buttons with no explanation.
