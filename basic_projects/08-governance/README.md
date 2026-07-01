# 08 - Governance: Bias Audit Script

## Overview

Build a Python script that loads a trained classification model and a labeled test dataset (with a protected attribute column), then computes standard fairness metrics — demographic parity, equal opportunity, and disparate impact — for each demographic group. The script prints a pass/fail status per metric based on configurable thresholds.

## Tech Stack

- **Fairness toolkit** — Aequitas or Fairlearn (open-source, purpose-built)
- **Model** — any classifier with a `predict` method (scikit-learn, XGBoost, PyTorch)
- **Data** — CSV with columns: `label` (ground truth), `prediction` (model output), and one or more protected attributes (`gender`, `race`, `age_group`)
- **Reporting** — console output + optional HTML report (Aequitas can generate one)

## Architecture & Design

```
test_data.csv ──► load ──► DataFrame
                          │
                    ┌─────┴─────┐
                    │  columns:  │
                    │  label     │
                    │  prediction│
                    │  gender    │
                    │  race      │
                    └─────┬─────┘
                          │
              ┌───────────▼───────────┐
              │  Fairness Evaluation   │
              ├───────────────────────┤
              │  demographic parity    │
              │  equal opportunity     │
              │  disparate impact      │
              │  false positive rate   │
              │  false negative rate   │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │  Threshold Check       │
              │  (e.g., parity < 0.1) │
              ├───────────────────────┤
              │  Group A: PASS         │
              │  Group B: FAIL (0.15) │
              └───────────┬───────────┘
                          │
                    ┌─────▼─────┐
                    │  Report    │
                    │  (console  │
                    │   + JSON)  │
                    └───────────┘
```

**Design decisions:**

- **Aequitas** over building metrics from scratch because it handles the group-by logic, confidence intervals, and edge cases (empty groups, zero division). The goal is to learn the *process* of fairness auditing, not reimplement statistics.
- **Three metrics** cover the most common regulatory and ethical fairness definitions:
  - **Demographic parity** — Is the selection rate equal across groups?
  - **Equal opportunity** — Is the true positive rate equal across groups?
  - **Disparate impact** — Is the ratio of favorable outcomes between groups above 0.8 (the "four-fifths rule" used by US EEOC)?
- **Thresholds are configurable** because fairness is context-dependent. A hiring model might require disparate impact > 0.9; a recommendation system might tolerate 0.7.

## Setup & Run

1. Install dependencies:
   ```bash
   pip install pandas aequitas fairlearn
   ```
2. Prepare your data as CSV with at least these columns:
   ```
   label,prediction,gender,race
   1,1,Female,White
   0,0,Male,Black
   1,0,Female,Asian
   ...
   ```
3. Run the audit:
   ```python
   # audit.py
   import pandas as pd
   from aequitas import Group, Preprocessing, Bias

   df = pd.read_csv("test_predictions.csv")
   # Must have columns: score (probability 0-1), label_value (0/1), and protected attribute columns

   # Aequitas expects specific column names
   df["score"] = df["prediction"]  # ensure score is float probability
   df["label_value"] = df["label"]

   # Preprocess
   g = Group()
   xtab, _ = g.get_crosstabs(df)
   b = Bias()
   results = b.get_disparities(xtab, xtab["group_size"])

   # Evaluate against thresholds
   parity_threshold = 0.1       # max acceptable deviation
   disparate_impact_threshold = 0.8  # four-fifths rule

   print(f"{'Group':<15} {'Parity':<10} {'DI':<10} {'Status'}")
   print("-" * 50)
   for _, row in results.iterrows():
       di = row.get("disparate_impact", 1)
       parity = abs(row.get("statistical_parity", 0))
       status = "PASS" if di >= disparate_impact_threshold and parity <= parity_threshold else "FAIL"
       print(f"{row['attribute_name']:<15} {parity:<10.3f} {di:<10.3f} {status}")
   ```
   ```bash
   python audit.py
   ```
4. Expected output example:
   ```
   Group           Parity     DI         Status
   ------------------------------------------------
   Female          0.023      0.952      PASS
   Male            0.018      0.973      PASS
   Non-binary      0.145      0.650      FAIL
   ```

## What You Learn

- The difference between group fairness definitions: demographic parity vs. equal opportunity vs. disparate impact
- How to operationalize the "four-fifths rule" from US employment law
- That fairness is a socio-technical problem — the metrics tell you *what* is happening, not *why* or *what to do about it*
- How to structure a fairness audit as a repeatable CI/CD step (this script can run in a GitHub Action)
- The importance of intersectional analysis — single-attribute checks can hide bias at intersections (e.g., women of color may be disadvantaged even if "women" and "people of color" separately pass)
- That there is no single "fair" metric — you must choose which definition matches the ethical and legal context of your specific use case
