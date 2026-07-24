"""
Comprehensive ML metrics for classification, regression, clustering, NLP, and ranking.

Examples
--------
>>> from aion.metrics import accuracy_score, f1_score, r2_score, bleu_score
>>> accuracy_score([0, 1, 1], [0, 1, 0])
0.6666666666666666
"""

from .classification import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    matthews_corrcoef,
    roc_auc_score,
    classification_report,
)
from .regression import (
    mean_squared_error,
    root_mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
    r2_score,
    adjusted_r2_score,
    explained_variance_score,
)
from .clustering import silhouette_score, adjusted_rand_score
from .nlp import bleu_score, rouge_l_score, perplexity
from .ranking import ndcg_score, mrr_score
from .stats import bootstrap_ci, mcnemar_test, compare_models

__all__ = [
    "accuracy_score",
    "confusion_matrix",
    "precision_score",
    "recall_score",
    "f1_score",
    "matthews_corrcoef",
    "roc_auc_score",
    "classification_report",
    "mean_squared_error",
    "root_mean_squared_error",
    "mean_absolute_error",
    "mean_absolute_percentage_error",
    "r2_score",
    "adjusted_r2_score",
    "explained_variance_score",
    "silhouette_score",
    "adjusted_rand_score",
    "bleu_score",
    "rouge_l_score",
    "perplexity",
    "ndcg_score",
    "mrr_score",
    "bootstrap_ci",
    "mcnemar_test",
    "compare_models",
]
