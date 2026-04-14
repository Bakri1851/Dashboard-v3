---
tags: [library, explainability, placeholder, unused]
status: 🔲 Not yet used
---

# SHAP

> ⚠️ Not currently used. Candidate for model explainability.

## What it is

SHapley Additive exPlanations — assigns each feature a Shapley value representing
its contribution to a given prediction. Model-agnostic, widely cited in ML literature.

## Potential use in this project

After training a model or optimising weights, use SHAP to explain which components
(n̂, t̂, î, r̂, A_raw, d̂, rep̂) contribute most to a student's struggle score.
Provides a principled, literature-grounded alternative to the rejected tornado plot —
SHAP values come from model behaviour, not from weights you manually set,
so they avoid the circular reasoning problem Dr. Batmaz flagged.

```python
# Sketch — not implemented
import shap
explainer = shap.Explainer(model, X_train)
shap_values = explainer(X_test)
shap.plots.waterfall(shap_values[0])
```

## Relevant to report

Ch3/Ch5: Feature importance and explainability without circular reasoning.
Directly addresses Dr. Batmaz's objection to the tornado plot.
