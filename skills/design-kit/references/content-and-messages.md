# Content, Messages & Analytics

Voice & tone (design.md §8), messages sent outside the screens (ux-spec.md `## Notifications`) and tracked events (ux-spec.md `## Analytics events`). Column names and values are exact — `verify.py` checks them.

## Contents
1. Voice & tone
2. Notifications: structure
3. Notifications: rules that make them sendable
4. Length limits
5. Analytics events

## 1. Voice & tone
- 3–5 principles, each with a real Do / Don't pair taken from this product's screens.
- A "Use / Avoid" word list for terms users and the team disagree on (e.g. "order" vs "PO request"); the copy deck must follow it.
- Thai: choose one register (polite, no ครับ/ค่ะ in UI labels; allowed in longer messages if the brand speaks that way) and keep it everywhere.

## 2. Notifications: structure
- `Locales:` line first (`en, th`) — every ID × channel needs a copy row per locale.
- **Triggers** — one row per event that sends something: `NT-01`…, `Trigger` = the Analytics event name (`po_submitted`) so one name means one thing, `Recipient` = declared role(s) or `actor`, `Channels`, `Category`, `Screen` (what the link opens), `Variables` as `name: type`.
- **Copy** — one row per ID × channel × locale: `Subject / Title` (email subject, push / in-app title; `—` for sms) and `Body` (plain text; for email, the summary paragraph).
- Variables: `{{snake_case}}`, declared on the trigger with a type: `string` · `number` · `money` · `date` · `datetime` · `url`. Every locale uses the same variables. Backend formats `money` / `date` / `datetime` per Formats & locale in the recipient's language — never pre-formatted in the template.
- No logic in templates (`{{#if}}`, `{%`, loops). Need a variant? Make a second trigger. Plurals follow the Formats & locale `plural` row.
- Links: name the screen; backend builds the URL or deep link (`action_url`). Never paste real URLs into copy.

## 3. Notifications: rules that make them sendable
- `marketing` needs prior consent (PDPA in Thailand, GDPR in the EU) and an unsubscribe link in every email; `transactional` (receipts, approvals, security) doesn't.
- Push appears on the lock screen: no personal or sensitive data (salaries, ID numbers, health, OTP codes not meant to be seen). "PO-1042 needs approval" — not the supplier's bank details.
- Email always ships a plain-text version; don't rely on images (many clients block them); don't use SVG in email (Gmail and Outlook don't show it).
- Put the point first — mobile mail clients cut subjects at about 40 characters.
- Measure them with `notification_sent` (server) and `notification_opened` (client), properties `notification_id: string, channel: enum(email/push/in-app/sms)`.

## 4. Length limits
- `### Channel limits` holds recommended maxima (warnings, not provider limits). Defaults: email subject 60 · push title 40 / body 120 · in-app title 60 / body 200 · sms body 70 (Thai, UCS-2 — one segment) / 160 (English). Rows can be per locale; a locale row beats `all`.
- `verify.py` counts characters excluding Thai tone marks and above/below vowels (Unicode category Mn), and counts each variable as a typical length for its type (string 12, number 6, money 12, date 11, datetime 17, url 0).
- Thai has no spaces, so truncation can cut mid-word — write shorter than the limit.

## 5. Analytics events
- Names: `object_action` in the past tense, snake_case, ≤ 40 characters, unique; never start with `ga_`, `firebase_`, `google_` (reserved). Screens: one `screen_viewed` event with `screen_id`, never one event per screen.
- `Source`: `server` for results that must be exact (saved, approved, paid — after the commit); `client` for UI behavior (filters, opens). Client events get lost to ad blockers and closed tabs.
- `Trigger`: an observable moment — "Submit returns 2xx", not "user submits".
- Properties: `name: type`, `name?` for optional (Events only — common properties are always sent), ≤ 25 per event including common ones (GA4's limit). Types: `string` · `integer` · `number` · `boolean` · `datetime` (ISO 8601 UTC) · `enum(a/b/c)` · `string[]` — GA4 doesn't accept arrays; send them as a comma-separated string there.
- No personal data in properties: names, emails, phone numbers, national IDs, addresses, free text. Use internal IDs. Money = `amount: number` + `currency: string` (ISO 4217), never a formatted string.
- `Req ID` links an event to the requirement it measures — the success metric in the spec Summary should have at least one event behind it.
