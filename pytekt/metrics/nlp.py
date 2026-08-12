"""NLP evaluation metrics (lightweight implementations)."""

from __future__ import annotations

from typing import List, Sequence


def _tokenize(text: str) -> List[str]:
    return text.lower().split()


def bleu_score(
    reference: str,
    hypothesis: str,
    *,
    max_n: int = 4,
) -> float:
    """Corpus BLEU approximation for a single sentence pair (0–1)."""
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)
    if not hyp_tokens:
        return 0.0
    precisions = []
    for n in range(1, max_n + 1):
        ref_ngrams = [tuple(ref_tokens[i : i + n]) for i in range(len(ref_tokens) - n + 1)]
        hyp_ngrams = [tuple(hyp_tokens[i : i + n]) for i in range(len(hyp_tokens) - n + 1)]
        if not hyp_ngrams:
            precisions.append(0.0)
            continue
        ref_counts = {}
        for ng in ref_ngrams:
            ref_counts[ng] = ref_counts.get(ng, 0) + 1
        match = 0
        for ng in hyp_ngrams:
            if ref_counts.get(ng, 0) > 0:
                match += 1
                ref_counts[ng] -= 1
        precisions.append(match / len(hyp_ngrams))
    import math
    if any(p == 0 for p in precisions):
        return 0.0
    log_avg = sum(math.log(p) for p in precisions) / len(precisions)
    bp = 1.0 if len(hyp_tokens) >= len(ref_tokens) else math.exp(1 - len(ref_tokens) / len(hyp_tokens))
    return float(bp * math.exp(log_avg))


def rouge_l_score(reference: str, hypothesis: str) -> float:
    """ROUGE-L F1 based on longest common subsequence length."""
    ref = _tokenize(reference)
    hyp = _tokenize(hypothesis)
    m, n = len(ref), len(hyp)
    if m == 0 or n == 0:
        return 0.0
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[m][n]
    prec = lcs / n
    rec = lcs / m
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def perplexity(log_probs: Sequence[float]) -> float:
    """Perplexity from log-probabilities (natural log)."""
    import math
    n = len(log_probs)
    if n == 0:
        return float("inf")
    return float(math.exp(-sum(log_probs) / n))
