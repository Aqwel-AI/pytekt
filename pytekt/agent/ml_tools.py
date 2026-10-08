"""
Machine Learning & Research Tools for PyTekt Agent.
Integrates PyTekt Core ML (models, preprocessing, metrics) for autonomous dataset exploration.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
import numpy as np


def profile_dataset(filepath: str) -> Dict[str, Any]:
    """
    Profile a tabular CSV dataset: dimensions, columns, missing values, summary stats.
    """
    if not os.path.isfile(filepath):
        return {"error": f"File not found: {filepath}"}

    try:
        from ..data.loaders import load_csv
        records = load_csv(filepath)
    except Exception as e:
        return {"error": f"Failed to load dataset: {e}"}

    if not records:
        return {"error": "Dataset is empty."}

    columns = list(records[0].keys())
    row_count = len(records)
    
    col_stats: Dict[str, Any] = {}
    for col in columns:
        vals = [r.get(col) for r in records]
        null_count = sum(1 for v in vals if v is None or v == "" or str(v).lower() in ("nan", "null"))
        
        # Check numeric
        numeric_vals = []
        for v in vals:
            if v is not None and v != "":
                try:
                    numeric_vals.append(float(v))
                except (ValueError, TypeError):
                    pass
        
        is_numeric = len(numeric_vals) > 0.8 * (row_count - null_count) and len(numeric_vals) > 0
        if is_numeric:
            arr = np.array(numeric_vals, dtype=float)
            col_stats[col] = {
                "type": "numeric",
                "missing": null_count,
                "missing_pct": round(null_count / row_count * 100, 2),
                "mean": round(float(np.mean(arr)), 4),
                "std": round(float(np.std(arr)), 4),
                "min": round(float(np.min(arr)), 4),
                "max": round(float(np.max(arr)), 4),
                "median": round(float(np.median(arr)), 4),
            }
        else:
            # Categorical value counts
            unique_vals = set(vals)
            col_stats[col] = {
                "type": "categorical",
                "missing": null_count,
                "missing_pct": round(null_count / row_count * 100, 2),
                "unique_count": len(unique_vals),
            }

    return {
        "filepath": filepath,
        "rows": row_count,
        "columns_count": len(columns),
        "columns": col_stats,
    }


def fit_baseline_classifier(
    filepath: str,
    target_column: str,
    model_type: str = "gaussian_nb",
    test_size: float = 0.2,
) -> Dict[str, Any]:
    """
    Train a baseline classifier using PyTekt native Core ML stack and compute metrics.
    Supported model types: 'gaussian_nb', 'logistic_regression', 'decision_tree'.
    """
    if not os.path.isfile(filepath):
        return {"error": f"File not found: {filepath}"}

    try:
        from ..data.loaders import load_csv
        from ..data.splitting import train_test_split
        from ..preprocessing.scalers import StandardScaler
        from ..metrics.classification import accuracy_score, precision_score, recall_score, f1_score

        records = load_csv(filepath)
        if not records:
            return {"error": "Dataset is empty"}

        if target_column not in records[0]:
            return {"error": f"Target column '{target_column}' not found in dataset."}

        # Extract features and targets
        feature_cols = [c for c in records[0].keys() if c != target_column]
        
        # Build numeric matrix
        X_rows = []
        y_vals = []
        for r in records:
            try:
                row_vals = [float(r[c]) for c in feature_cols]
                t_val = r[target_column]
                X_rows.append(row_vals)
                y_vals.append(t_val)
            except (ValueError, TypeError):
                continue

        X = np.array(X_rows, dtype=float)
        # Encode target if strings
        unique_targets = sorted(list(set(y_vals)))
        target_map = {t: idx for idx, t in enumerate(unique_targets)}
        y = np.array([target_map[t] for t in y_vals], dtype=int)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Select model from pytekt.models
        m_lower = model_type.lower()
        if "logistic" in m_lower:
            from ..models.linear import LogisticRegression
            clf = LogisticRegression()
        elif "tree" in m_lower:
            from ..models.trees import DecisionTreeClassifier
            clf = DecisionTreeClassifier(max_depth=5)
        else:
            from ..models.naive_bayes import GaussianNB
            clf = GaussianNB()

        clf.fit(X_train_scaled, y_train)
        preds = clf.predict(X_test_scaled)

        acc = float(accuracy_score(y_test, preds))
        f1 = float(f1_score(y_test, preds, average="macro"))

        return {
            "status": "success",
            "model": model_type,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features_used": feature_cols,
            "classes": unique_targets,
            "metrics": {
                "accuracy": round(acc, 4),
                "f1_macro": round(f1, 4),
            },
        }
    except Exception as e:
        return {"error": f"Model training failed: {e}"}
