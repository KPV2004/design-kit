# Assets

How to fill design.md `## 9. Assets`: every image file the build needs, with sizes and formats per platform. Column names and values are exact — `verify.py` checks them. Sizes below are checked against platform docs (Nov 2026); re-check when targeting a new OS version.

## Contents
1. Rules
2. Web
3. iOS
4. Android
5. Email and sharing
6. Illustrations

## 1. Rules
- One row per file: the key is Asset + Platform + Format (the favicon has an `ico` and an `svg` row).
- `Size`: the largest export in px (`WxH`, several comma-separated) or `vector`; `—` for the web manifest. Native apps export @1x/@2x/@3x (iOS) and mdpi–xxxhdpi (Android) from one vector source — list the largest.
- `Status`: `needed` → `draft` → `review` → `approved` (ready to ship). `Source`: the path in the repo or design files, `TBD` until it exists.
- Colors inside icons and backgrounds come from design.md tokens (e.g. splash background = `brand-600`).

## 2. Web
| Asset | Size | Format | Notes |
|---|---|---|---|
| favicon | 32x32 (contains 16x16) | ico | legacy browsers |
| favicon | vector | svg | modern browsers; may switch color with `prefers-color-scheme` |
| apple-touch-icon | 180x180 | png | no transparency |
| manifest-icon | 192x192, 512x512 | png | purpose `any` |
| maskable-icon | 512x512 | png | purpose `maskable`; content inside the central 80% |
| web-manifest | — | webmanifest | `name`, `short_name`, `theme_color` / `background_color` (tokens), `icons[]` — PWAs build their splash from it |

## 3. iOS
| Asset | Size | Format | Notes |
|---|---|---|---|
| app-icon | 1024x1024 | png | no alpha, no rounded corners (the system masks it) |
| splash | — | — | a launch screen (storyboard / Info.plist) with the logo and a token background — not an image size |

## 4. Android
| Asset | Size | Format | Notes |
|---|---|---|---|
| adaptive-icon-foreground | 432x432 | png or xml | 108dp layer at xxxhdpi; keep content inside the central 66dp safe zone (72dp is visible through the mask) |
| adaptive-icon-background | 432x432 | png or xml | 108dp; a color token works too |
| adaptive-icon-monochrome | 432x432 | xml | themed icons (Android 13+), single color |
| play-store-icon | 512x512 | png | |
| splash-icon | 1152x1152 | png or xml | Android 12+ SplashScreen: 288dp without an icon background (content inside a 192dp circle), or 240dp with one (160dp circle); background = color token |

## 5. Email and sharing
| Asset | Platform | Size | Format | Notes |
|---|---|---|---|---|
| email-header | email | 1200 wide | png or jpg | displayed at 600 wide (@2x); never svg — Gmail and Outlook don't show it; meaning must survive images being blocked |
| og-image | web | 1200x630 | png or jpg | link previews in chat apps and social sites |

## 6. Illustrations
- Empty-state and onboarding illustrations: one row each, `Screen` = where it appears, `svg` for web, vector drawable (`xml`) or pdf/svg for native.
- Use the icon set's style (stroke width, corner radius) or a single illustration style throughout; decorative images get empty `alt`.
