#!/usr/bin/env python3
"""
PyTekt - Model Evaluation and Metrics
==========================================

Evaluation utilities for ML outputs: classification metrics (accuracy,
precision, recall, F1, confusion matrix, ROC-AUC), regression metrics (MSE,
RMSE, MAE, R²), and text-similarity evaluation. evaluate_predictions
auto-detects task type. Supports JSON and CSV inputs for predictions and
ground truth.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import json
import csv
from typing import List, Dict, Any, Union, Tuple, Optional
import numpy as np


def evaluate_predictions(preds_file: str, answers_file: str) -> Dict[str, float]:
    """
    Load predictions and ground truth from files, detect task type (classification
    vs regression from data types), and return the corresponding metrics dict.
    Supports JSON (list) and CSV (single column). Returns an empty dict on error.
    """
    print(f"Evaluating predictions: {preds_file}")
    print(f"Against answers: {answers_file}")
    try:
        predictions = _load_data(preds_file)
        answers = _load_data(answers_file)
        if isinstance(predictions[0], (int, float)) and isinstance(answers[0], (int, float)):
            return calculate_regression_metrics(predictions, answers)
        else:
            return calculate_classification_metrics(predictions, answers)
    except Exception as e:
        print(f"Error evaluating predictions: {e}")
        return {}


def _load_data(filepath: str) -> List[Any]:
    """Load a list of values from JSON, CSV (single column), or plain text (one value per line)."""
    if filepath.endswith(".json"):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else [data]
    elif filepath.endswith(".csv"):
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            return [row[0] for row in reader]
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]


def calculate_classification_metrics(y_pred: List[Any], y_true: List[Any]) -> Dict[str, float]:
    """
    Return accuracy and, for binary labels, precision, recall, and F1.
    For multiclass, returns accuracy and num_classes.
    """
    if len(y_pred) != len(y_true):
        raise ValueError("Predictions and answers must have the same length")
    y_pred = np.array(y_pred)
    y_true = np.array(y_true)
    accuracy = np.mean(y_pred == y_true)
    unique_labels = np.unique(np.concatenate([y_pred, y_true]))
    if len(unique_labels) == 2:
        tp = np.sum((y_pred == unique_labels[1]) & (y_true == unique_labels[1]))
        fp = np.sum((y_pred == unique_labels[1]) & (y_true == unique_labels[0]))
        fn = np.sum((y_pred == unique_labels[0]) & (y_true == unique_labels[1]))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1_score)
        }
    else:
        return {
            'accuracy': float(accuracy),
            'num_classes': len(unique_labels)
        }


def calculate_regression_metrics(y_pred: List[float], y_true: List[float]) -> Dict[str, float]:
    """Return MSE, RMSE, MAE, and R-squared for predicted vs true numerical values."""
    if len(y_pred) != len(y_true):
        raise ValueError("Predictions and answers must have the same length")
    y_pred = np.array(y_pred, dtype=float)
    y_true = np.array(y_true, dtype=float)
    mse = np.mean((y_pred - y_true) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_pred - y_true))
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    return {
        'mse': float(mse),
        'rmse': float(rmse),
        'mae': float(mae),
        'r2': float(r2)
    }


def confusion_matrix(y_pred: List[Any], y_true: List[Any]) -> np.ndarray:
    """Return the confusion matrix (rows=true, cols=pred) as a numpy array."""
    unique_labels = sorted(list(set(y_pred + y_true)))
    n_labels = len(unique_labels)
    label_to_idx = {label: i for i, label in enumerate(unique_labels)}
    cm = np.zeros((n_labels, n_labels), dtype=int)
    for pred, true in zip(y_pred, y_true):
        cm[label_to_idx[true], label_to_idx[pred]] += 1
    
    return cm


def calculate_auc_roc(y_scores: List[float], y_true: List[int]) -> float:
    """Return AUC-ROC for binary classification (y_true in {0, 1}). Uses trapezoidal rule."""
    sorted_indices = np.argsort(y_scores)[::-1]
    y_scores_sorted = np.array(y_scores)[sorted_indices]
    y_true_sorted = np.array(y_true)[sorted_indices]
    n_pos = np.sum(y_true)
    n_neg = len(y_true) - n_pos
    
    if n_pos == 0 or n_neg == 0:
        return 0.5
    tpr_values = []
    fpr_values = []
    
    tp = 0
    fp = 0
    
    for i in range(len(y_true_sorted)):
        if y_true_sorted[i] == 1:
            tp += 1
        else:
            fp += 1
        
        tpr = tp / n_pos
        fpr = fp / n_neg
        
        tpr_values.append(tpr)
        fpr_values.append(fpr)
    auc = 0.0
    for i in range(1, len(fpr_values)):
        auc += (fpr_values[i] - fpr_values[i-1]) * (tpr_values[i] + tpr_values[i-1]) / 2
    
    return auc


def evaluate_text_similarity(pred_texts: List[str], true_texts: List[str]) -> Dict[str, float]:
    """Return exact_match_ratio and avg_word_overlap (pred vs true text pairs)."""
    if len(pred_texts) != len(true_texts):
        raise ValueError("Predictions and ground truth must have the same length")
    exact_matches = sum(1 for p, t in zip(pred_texts, true_texts) if p.strip() == t.strip())
    exact_match_ratio = exact_matches / len(pred_texts)
    word_overlaps = []
    for pred, true in zip(pred_texts, true_texts):
        pred_words = set(pred.lower().split())
        true_words = set(true.lower().split())
        
        if len(true_words) == 0:
            overlap = 1.0 if len(pred_words) == 0 else 0.0
        else:
            overlap = len(pred_words.intersection(true_words)) / len(true_words)
        word_overlaps.append(overlap)
    
    avg_word_overlap = np.mean(word_overlaps)
    
    return {
        'exact_match_ratio': float(exact_match_ratio),
        'avg_word_overlap': float(avg_word_overlap)
    }