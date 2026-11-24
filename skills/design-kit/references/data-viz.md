# Data Visualization

How to choose and specify charts. The chart list for a screen goes in ux-spec.md `## Charts` (optional — only apps with charts); colors come from design.md §2.6 chart palette. Column names and values are exact — `verify.py` checks them.

## Contents
1. Pick the chart from the question
2. The `## Charts` table
3. Accessibility
4. Palette
5. States and formats

## 1. Pick the chart from the question
| Question | Type | Notes |
|---|---|---|
| How much is each item? (compare categories) | `bar` | sort by value; `orient: horizontal` for long labels or > 7 items |
| How do several series compare per category? | `grouped-bar` | ≤ 3 series |
| What makes up each total? | `stacked-bar` | ≤ 5 parts; put the most important part at the base |
| How did it change over time? | `line` | ≤ 4 lines; `area` only for one series or cumulative totals |
| Two measures with different units over time | `combo` | bar + line on two axes; label both axes |
| Share of a whole (≤ 5 parts) | `donut` | never pie with many slices; a bar chart is usually clearer |
| One number that matters | `kpi` | value + comparison ("+12% vs last month") |
| Progress against a target | `progress` | bullet or gauge with the target marked |
| A trend inside a table row | `sparkline` | no axes; the value sits next to it |
| Relationship between two measures | `scatter` | for analysts, rarely for operational screens |
| Exact values matter more than shape | `table` | the honest default for operational tools |

Enterprise tools: a sorted table often beats a chart. Add a chart only when the shape answers the question faster.

## 2. The `## Charts` table
`| Chart | Screen | Question | Type | Data | Palette | Table fallback |`
- `Chart`: kebab-case, unique. `Screen`: where it appears (inventory IDs).
- `Question`: the one question it answers, in the user's words.
- `Data`: `x: <field> · y: <field> (agg, unit)` using the field names in the API contract response, e.g. `x: status · y: count (count, orders)`; add `orient: horizontal` when needed.
- `Palette`: chart tokens from §2.6 (`chart-1, chart-2`), `—` for kpi/table.
- `Table fallback`: `yes` (a data table is available) or `no` (warned).

## 3. Accessibility
- Never color alone: direct labels on lines and bars, patterns or markers for series, legend order = visual order.
- Chart marks ≥ 3:1 against the background and adjacent marks; text ≥ 4.5:1.
- Every chart has a text alternative: a one-sentence summary ("Pending orders rose from 12 to 30 this week") and a data table (visible or behind a "Show as table" toggle).
- Tooltips are not the only way to read a value — keyboard users must reach the same values (the table).
- Don't animate on load under reduced motion.

## 4. Palette
- §2.6 lists `chart-1` … `chart-8` as a hex table (`| chart-1 | #… |`) so `verify.py` can match Palette cells. Order matters: use them in order, `chart-1` for the main series.
- Status charts (approved / rejected) use the status colors from §2.5, not chart colors — one meaning per color.
- Check every chart color in the dark theme too.

## 5. States and formats
- Empty, loading and error states of a chart go in the States matrix of its screen (empty: "No orders this month", not an empty axis).
- Axis labels and tooltips follow Formats & locale (thousands separators, currency, Thai era for dates).
- Zero-based axes for bars; say so when a line chart's axis doesn't start at zero.
