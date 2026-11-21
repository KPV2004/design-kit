# [App] — UX Spec
> Version 1.0 — matches design.md 1.0

## Summary

## Assumptions & open questions

## User flow
```mermaid
flowchart LR
  login[เข้าสู่ระบบ] --> list[รายการ]
```

## Screens
### [screen-id] Screen name
- **Purpose:**
- **Layout:**
- **Key components:**
- **Annotations:** (1) … (2) … — match `.anno` markers in wireframe and mockup

## States
| Screen | Empty | Loading | Error | Success | Permission |
|---|---|---|---|---|---|

## Fields & validation
| Field | Type | Required | Rule | Error message (exact wording) |
|---|---|---|---|---|

## Interactions & behavior

## Dev diagrams
### Data model (ER)
```mermaid
erDiagram
  USER ||--o{ DOCUMENT : creates
```

### Document status (state)
```mermaid
stateDiagram-v2
  [*] --> draft
```

### Save document (sequence)
```mermaid
sequenceDiagram
  actor U as ผู้ใช้
  participant API
  U->>API: POST /documents
```

## API contract
| Method | Path | Used by (screen ID) | Request | Success | Errors (status → message shown) |
|---|---|---|---|---|---|

## Accessibility notes

## Risks for implementation
