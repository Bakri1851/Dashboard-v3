# ui/

**Path:** `code/learning_dashboard/ui/`
**Parent:** [[learning_dashboard]]

> The presentation layer. Every Streamlit widget and Plotly chart the instructor sees is rendered from this subpackage. The lab assistant app reuses the mobile CSS from here but has its own inline rendering.

## Contents

| File | Summary |
|------|---------|
| [[components]] | Reusable Streamlit/Plotly building blocks — header, cards, leaderboards, charts, comparison panels. |
| [[views]] | Page-level layouts — In Class, Student Detail, Question Detail, Data Analysis, Settings, Comparison, Previous Sessions. |
| [[theme]] | CSS generators (desktop sci-fi + mobile) and Plotly layout defaults. |

## Purpose

The split keeps widget-level concerns (one card, one chart) in [[components]] while page-level composition stays in [[views]]. [[theme]] owns everything visual — CSS, colours, fonts, Plotly defaults — so restyling never means editing logic.

## Related notes

- [[UI System]] (thematic)
- [[Architecture]]
