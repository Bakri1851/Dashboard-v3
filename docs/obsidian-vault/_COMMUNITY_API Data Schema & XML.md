---
type: community
cohesion: 0.19
members: 13
---

# API Data Schema & XML

**Cohesion:** 0.19 - loosely connected
**Members:** 13 nodes

## Members
- [[AI Check Triggers Submission]] - image - Report/figures/design-and-architecture/data-entry.png
- [[API Record Structure]] - image - Report/figures/design-and-architecture/data-entry.png
- [[Feedback XML Element (AI Response)]] - image - Report/figures/design-and-architecture/data-entry.png
- [[Module Code Field]] - image - Report/figures/design-and-architecture/data-entry.png
- [[Question Field]] - image - Report/figures/design-and-architecture/data-entry.png
- [[Session ID Field (Time of First Submission)]] - image - Report/figures/design-and-architecture/data-entry.png
- [[Step XML Element (Student Answer)]] - image - Report/figures/design-and-architecture/data-entry.png
- [[Submission XML Element]] - image - Report/figures/design-and-architecture/data-entry.png
- [[Timestamp Field (Most Recent Submission)]] - image - Report/figures/design-and-architecture/data-entry.png
- [[User Field]] - image - Report/figures/design-and-architecture/data-entry.png
- [[XML Field (Embedded XML Payload)]] - image - Report/figures/design-and-architecture/data-entry.png
- [[XML Payload Structure]] - image - Report/figures/design-and-architecture/data-entry.png
- [[data_loader.py — API Fetch and XML Parsing]] - code - code/learning_dashboard/data_loader.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/API_Data_Schema_&_XML
SORT file.name ASC
```
