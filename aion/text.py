#!/usr/bin/env python3
"""
Aqwel-Aion - Text Processing
============================

Dependency-light text utilities for AI/ML/data-science workflows.

The module focuses on practical tasks that show up repeatedly in research and
engineering pipelines:

- normalization and cleaning for messy corpora
- tokenization, sentence splitting, and chunking
- corpus profiling and lightweight statistics
- duplicate detection and similarity checks
- prompt, dataset, and safety-oriented text inspection
- extraction helpers for semi-structured natural language

The implementations intentionally stay in the Python standard library so the
module is easy to ship inside notebooks, scripts, CI, and lightweight services.
"""

from __future__ import annotations

import hashlib
import html
import re
import string
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


# Compiled patterns are kept at module scope so repeated calls do not spend time
# recompiling the same regular expressions in hot paths.
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")
SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
MARKDOWN_CODE_FENCE_PATTERN = re.compile(r"```(?:[\w+-]+)?\n(.*?)```", re.DOTALL)
URL_PATTERN = re.compile(
    r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.~%!$&'()*+,;=:@-])*(?:\?(?:[\w&=%.~!$'()*+,;:@/-])*)?(?:#(?:[\w.~!$&'()*+,;=:@/-])*)?)?"
)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_PATTERN = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"
)
PHONE_SUB_PATTERN = re.compile(
    r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?){2,4}\d{2,4}\b"
)
NUMBER_PATTERN = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
HASHTAG_PATTERN = re.compile(r"(?<!\w)#([A-Za-z0-9_]+)")
MENTION_PATTERN = re.compile(r"(?<!\w)@([A-Za-z0-9_]+)")
PARENTHETICAL_PATTERN = re.compile(r"\(([^()]+)\)")
QUOTED_STRING_PATTERN = re.compile(r'"([^"\n]+)"|\'([^\'\n]+)\'')

VISUAL_KEYWORDS = {
    "see",
    "look",
    "bright",
    "dark",
    "color",
    "image",
    "view",
    "vision",
    "shape",
    "diagram",
    "photo",
    "chart",
}

DEFAULT_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "in",
    "is",
    "it",
    "its",
    "may",
    "might",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "their",
    "them",
    "these",
    "this",
    "those",
    "to",
    "was",
    "were",
    "will",
    "with",
    "would",
    "you",
    "your",
}

CONTRACTIONS = {
    "aren't": "are not",
    "can't": "cannot",
    "couldn't": "could not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hasn't": "has not",
    "haven't": "have not",
    "he's": "he is",
    "i'd": "i would",
    "i'll": "i will",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it's": "it is",
    "let's": "let us",
    "she's": "she is",
    "shouldn't": "should not",
    "that's": "that is",
    "there's": "there is",
    "they're": "they are",
    "they've": "they have",
    "wasn't": "was not",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what's": "what is",
    "who's": "who is",
    "won't": "will not",
    "wouldn't": "would not",
    "you're": "you are",
    "you've": "you have",
}

SENSITIVE_PATTERNS: Mapping[str, re.Pattern[str]] = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b(?:\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "email": re.compile(r"\b[\w.-]+?@\w+?\.\w+?\b"),
    "password": re.compile(r"(password\s*[:=]\s*.+)", re.IGNORECASE),
    "api_key": re.compile(r"(api[_\-]?key\s*[:=]\s*.+)", re.IGNORECASE),
}

PROMPT_INJECTION_PATTERNS: Mapping[str, re.Pattern[str]] = {
    "ignore_previous_instructions": re.compile(r"\bignore\b.{0,40}\b(previous|prior|above)\b", re.IGNORECASE),
    "reveal_system_prompt": re.compile(r"\b(system prompt|hidden prompt|developer message)\b", re.IGNORECASE),
    "exfiltrate_secrets": re.compile(r"\b(api key|secret|password|token|credentials)\b", re.IGNORECASE),
    "tool_override": re.compile(r"\b(disregard|disable|bypass)\b.{0,40}\b(safety|policy|guardrail)\b", re.IGNORECASE),
    "role_redefinition": re.compile(r"\byou are now\b|\bpretend to be\b", re.IGNORECASE),
}


def _safe_ratio(numerator: int, denominator: int) -> float:
    """Return a defensive ratio for feature calculations."""
    return float(numerator) / denominator if denominator else 0.0


def _iter_ngrams(tokens: Sequence[str], n: int) -> Iterable[Tuple[str, ...]]:
    """Yield token n-grams without materializing intermediate slices unnecessarily."""
    for index in range(len(tokens) - n + 1):
        yield tuple(tokens[index : index + n])


def _normalized_duplicate_key(text: str) -> str:
    """Build a stable normalization key for duplicate detection and corpus deduplication."""
    normalized = normalize_unicode(text, form="NFKC")
    normalized = normalize_whitespace(normalized)
    return normalized.casefold()


def _default_stopwords(custom_stopwords: Optional[Iterable[str]] = None) -> set[str]:
    """Merge caller-provided stopwords with the module defaults."""
    stopwords = set(DEFAULT_STOPWORDS)
    if custom_stopwords is not None:
        stopwords.update(word.casefold() for word in custom_stopwords)
    return stopwords


def count_words(text: str) -> int:
    """Return the number of whitespace-separated words in *text*."""
    return len(text.split())


def count_characters(text: str) -> int:
    """Return the raw character count, including whitespace and punctuation."""
    return len(text)


def count_lines(text: str) -> int:
    """Return the number of logical lines in *text*."""
    return len(text.splitlines())


def reverse_text(text: str) -> str:
    """Return *text* in reverse character order."""
    return text[::-1]


def is_palindrome(text: str) -> bool:
    """Return ``True`` when *text* is a palindrome after basic normalization."""
    cleaned_text = re.sub(r"[^a-zA-Z0-9]", "", text.lower())
    return cleaned_text == cleaned_text[::-1]


def extract_emails(text: str) -> List[str]:
    """Return all email addresses found in *text*."""
    return EMAIL_PATTERN.findall(text)


def extract_phone_numbers(text: str) -> List[Tuple[str, str, str]]:
    """Return matched North-American-style phone number groups from *text*."""
    return PHONE_PATTERN.findall(text)


def extract_urls(text: str) -> List[str]:
    """Return all HTTP/HTTPS URLs found in *text*."""
    return URL_PATTERN.findall(text)


def clean_text(text: str) -> str:
    """Normalize runs of whitespace to a single space and trim outer whitespace."""
    return re.sub(r"\s+", " ", text.strip())


def clean_text_corpus(text: str) -> str:
    """
    Apply aggressive ASCII-oriented corpus cleaning.

    This helper is intentionally narrow: it strips HTML-like tags, removes every
    non-letter character, and leaves only ASCII letters and spaces. That makes it
    useful for very simple Latin-alphabet experiments, but too destructive for
    multilingual corpora or tasks that need digits, punctuation, or casing.
    """
    text = strip_html(text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text.strip()


def detect_language(text: str) -> str:
    """
    Heuristically detect ``en``, ``es``, or ``fr`` from common function words.

    The implementation is intentionally lightweight and should be treated as a
    convenience heuristic rather than a production-grade language identifier.
    """
    tokens = set(tokenize_words(text, lowercase=True))
    english_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    spanish_words = {"el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le"}
    french_words = {"le", "la", "de", "et", "en", "un", "du", "que", "est", "pour", "dans", "sur"}
    english_count = sum(word in tokens for word in english_words)
    spanish_count = sum(word in tokens for word in spanish_words)
    french_count = sum(word in tokens for word in french_words)
    if english_count > spanish_count and english_count > french_count:
        return "en"
    if spanish_count > english_count and spanish_count > french_count:
        return "es"
    if french_count > english_count and french_count > spanish_count:
        return "fr"
    return "unknown"


def generate_hash(text: str, algorithm: str = "md5") -> str:
    """
    Return a hexadecimal digest for *text* using the requested hash algorithm.

    Supported algorithms are ``md5``, ``sha1``, and ``sha256``.
    """
    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
    }
    try:
        hash_object = algorithms[algorithm](text.encode("utf-8"))
    except KeyError as exc:
        raise ValueError(f"Unsupported hash algorithm: {algorithm!r}") from exc
    return hash_object.hexdigest()


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Return the most frequent non-stopword tokens from *text*.

    This is a simple statistical keyword heuristic, not a semantic keyphrase
    extractor. It works best for quick corpus inspection and prompt debugging.
    """
    frequencies = word_frequencies(text, lowercase=True, min_length=3)
    return [word for word, _ in Counter(frequencies).most_common(max_keywords)]


def is_question(text: str) -> bool:
    """Return ``True`` when *text* ends with a question mark after trimming."""
    return text.strip().endswith("?")


def normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace to a single space and strip leading/trailing space."""
    return re.sub(r"\s+", " ", text).strip()


def is_sensitive_text(text: str) -> bool:
    """Return ``True`` when *text* appears to contain obvious sensitive strings."""
    return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS.values())


def text_contains_visual_language(text: str) -> bool:
    """Return ``True`` when *text* contains common visually grounded language."""
    tokens = set(tokenize_words(text, lowercase=True))
    return any(keyword in tokens for keyword in VISUAL_KEYWORDS)


def tokenize_words(
    text: str,
    *,
    lowercase: bool = True,
    include_numbers: bool = True,
    strip_accents_first: bool = False,
) -> List[str]:
    """
    Tokenize *text* into word-like units.

    The tokenizer is deliberately simple and deterministic. It is suitable for
    corpus inspection, feature engineering, and rule-based preprocessing where a
    small dependency footprint matters more than linguistic completeness.
    """
    if strip_accents_first:
        text = strip_accents(text)
    tokens = WORD_PATTERN.findall(text)
    if not include_numbers:
        tokens = [token for token in tokens if not token.isdigit()]
    if lowercase:
        tokens = [token.casefold() for token in tokens]
    return tokens


def tokenize_characters(text: str, *, normalize_newlines: bool = True) -> List[str]:
    """Return a character-level tokenization of *text*."""
    if normalize_newlines:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    return list(text)


def split_sentences(text: str) -> List[str]:
    """
    Split *text* into lightweight sentence units.

    The splitter uses punctuation-based heuristics and keeps implementation
    complexity low. For rigorous linguistic segmentation, a dedicated NLP library
    is still the better tool.
    """
    normalized = normalize_whitespace(text)
    if not normalized:
        return []
    return [sentence.strip() for sentence in SENTENCE_SPLIT_PATTERN.split(normalized) if sentence.strip()]


def split_paragraphs(text: str) -> List[str]:
    """Split *text* on blank lines and return non-empty paragraphs."""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def strip_html(text: str) -> str:
    """
    Remove HTML tags and decode basic HTML entities.

    This helper is intentionally regex-based and is meant for lightweight cleanup
    of scraped text, not for fully faithful HTML parsing.
    """
    return html.unescape(HTML_TAG_PATTERN.sub(" ", text))


def strip_markdown(text: str) -> str:
    """
    Remove common Markdown markers while keeping human-readable content.

    The goal is to preserve the underlying text for indexing and analysis rather
    than to perfectly render every edge case in the Markdown grammar.
    """
    text = MARKDOWN_CODE_FENCE_PATTERN.sub(r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}(#{1,6}|\*|-|\+|>)\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"(\*\*|__|\*|_)(.*?)\1", r"\2", text)
    return text


def strip_urls(text: str) -> str:
    """Remove URLs from *text*."""
    return URL_PATTERN.sub("", text)


def strip_emails(text: str) -> str:
    """Remove email addresses from *text*."""
    return EMAIL_PATTERN.sub("", text)


def strip_phone_numbers(text: str) -> str:
    """Remove phone-number-like strings from *text*."""
    return PHONE_SUB_PATTERN.sub("", text)


def remove_punctuation(text: str, *, keep_apostrophes: bool = False) -> str:
    """Remove punctuation characters from *text*."""
    punctuation = string.punctuation
    if keep_apostrophes:
        punctuation = punctuation.replace("'", "")
    table = str.maketrans("", "", punctuation)
    return text.translate(table)


def normalize_quotes(text: str) -> str:
    """Normalize curly and typographic quotes to straight ASCII quotes."""
    translation = str.maketrans(
        {
            "“": '"',
            "”": '"',
            "„": '"',
            "‟": '"',
            "’": "'",
            "‘": "'",
            "‚": "'",
            "‛": "'",
        }
    )
    return text.translate(translation)


def normalize_dashes(text: str) -> str:
    """Normalize em-dashes, en-dashes, and minus-like characters to ``-``."""
    translation = str.maketrans(
        {
            "–": "-",
            "—": "-",
            "−": "-",
            "‑": "-",
            "‒": "-",
        }
    )
    return text.translate(translation)


def normalize_unicode(text: str, form: str = "NFKC") -> str:
    """
    Normalize Unicode to the requested canonical form.

    ``NFKC`` is a sensible default for research pipelines because it reduces many
    visually equivalent variants into a more stable representation.
    """
    return unicodedata.normalize(form, text)


def strip_accents(text: str) -> str:
    """Remove combining diacritics from *text* while leaving base characters."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def expand_contractions(text: str) -> str:
    """Expand a small curated set of common English contractions."""
    if not CONTRACTIONS:
        return text

    pattern = re.compile(
        r"\b(" + "|".join(re.escape(key) for key in sorted(CONTRACTIONS, key=len, reverse=True)) + r")\b",
        re.IGNORECASE,
    )

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        expanded = CONTRACTIONS[token.casefold()]
        return expanded.capitalize() if token[:1].isupper() else expanded

    return pattern.sub(replace, text)


def remove_stopwords(text: str, custom_stopwords: Optional[Iterable[str]] = None) -> str:
    """Remove stopwords from *text* and return the remaining tokens joined by spaces."""
    stopwords = _default_stopwords(custom_stopwords)
    tokens = [token for token in tokenize_words(text, lowercase=True) if token not in stopwords]
    return " ".join(tokens)


def word_frequencies(
    text: str,
    *,
    lowercase: bool = True,
    min_length: int = 1,
    custom_stopwords: Optional[Iterable[str]] = None,
) -> Dict[str, int]:
    """
    Count token frequencies in *text*.

    The function exposes a reusable primitive for keyword extraction, lexical
    analysis, and simple bag-of-words style feature engineering.
    """
    stopwords = _default_stopwords(custom_stopwords)
    tokens = [
        token
        for token in tokenize_words(text, lowercase=lowercase)
        if len(token) >= min_length and token.casefold() not in stopwords
    ]
    return dict(Counter(tokens))


def ngram_counts(
    text: str,
    n: int = 2,
    *,
    lowercase: bool = True,
    custom_stopwords: Optional[Iterable[str]] = None,
) -> Dict[Tuple[str, ...], int]:
    """Return token n-gram counts for *text*."""
    if n <= 0:
        raise ValueError("n must be a positive integer")
    stopwords = _default_stopwords(custom_stopwords)
    tokens = [
        token
        for token in tokenize_words(text, lowercase=lowercase)
        if token.casefold() not in stopwords
    ]
    return dict(Counter(_iter_ngrams(tokens, n)))


def character_ngrams(text: str, n: int = 3, *, normalize: bool = True) -> Dict[str, int]:
    """Return character n-gram counts for *text*."""
    if n <= 0:
        raise ValueError("n must be a positive integer")
    text = normalize_whitespace(text) if normalize else text
    if len(text) < n:
        return {}
    grams = (text[index : index + n] for index in range(len(text) - n + 1))
    return dict(Counter(grams))


def top_ngrams(
    text: str,
    n: int = 2,
    *,
    top_k: int = 10,
    lowercase: bool = True,
) -> List[Tuple[Tuple[str, ...], int]]:
    """Return the top ``top_k`` token n-grams and their counts."""
    return Counter(ngram_counts(text, n=n, lowercase=lowercase)).most_common(top_k)


def unique_tokens(text: str, *, lowercase: bool = True) -> List[str]:
    """Return unique tokens while preserving first-seen order."""
    seen: set[str] = set()
    ordered_tokens: List[str] = []
    for token in tokenize_words(text, lowercase=lowercase):
        if token not in seen:
            seen.add(token)
            ordered_tokens.append(token)
    return ordered_tokens


def lexical_diversity(text: str) -> float:
    """Return the type-token ratio for *text*."""
    tokens = tokenize_words(text, lowercase=True)
    return _safe_ratio(len(set(tokens)), len(tokens))


def hapax_legomena(text: str) -> List[str]:
    """Return tokens that appear exactly once in *text*."""
    tokens = tokenize_words(text, lowercase=True)
    counts = Counter(tokens)
    return [token for token in tokens if counts[token] == 1]


def average_word_length(text: str) -> float:
    """Return the average token length for *text*."""
    tokens = tokenize_words(text, lowercase=False)
    return _safe_ratio(sum(len(token) for token in tokens), len(tokens))


def average_sentence_length(text: str) -> float:
    """Return the average number of tokens per sentence."""
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    token_total = sum(len(tokenize_words(sentence)) for sentence in sentences)
    return token_total / len(sentences)


def text_statistics(text: str) -> Dict[str, Any]:
    """
    Return a compact descriptive summary for *text*.

    The output is intentionally dictionary-shaped so callers can serialize it
    easily to JSON, log it in experiments, or feed it into dashboards.
    """
    tokens = tokenize_words(text, lowercase=True)
    sentences = split_sentences(text)
    lines = text.splitlines()
    stats = {
        "characters": len(text),
        "characters_no_space": len(re.sub(r"\s+", "", text)),
        "words": len(tokens),
        "unique_words": len(set(tokens)),
        "lines": len(lines),
        "paragraphs": len(split_paragraphs(text)) if text.strip() else 0,
        "sentences": len(sentences),
        "avg_word_length": average_word_length(text),
        "avg_sentence_length": average_sentence_length(text),
        "lexical_diversity": lexical_diversity(text),
        "digit_ratio": digit_ratio(text),
        "uppercase_ratio": uppercase_ratio(text),
        "punctuation_ratio": punctuation_ratio(text),
        "whitespace_ratio": whitespace_ratio(text),
        "non_ascii_ratio": non_ascii_ratio(text),
    }
    return stats


def digit_ratio(text: str) -> float:
    """Return the fraction of characters in *text* that are digits."""
    return _safe_ratio(sum(char.isdigit() for char in text), len(text))


def uppercase_ratio(text: str) -> float:
    """Return the fraction of alphabetic characters that are uppercase."""
    alphabetic = [char for char in text if char.isalpha()]
    return _safe_ratio(sum(char.isupper() for char in alphabetic), len(alphabetic))


def punctuation_ratio(text: str) -> float:
    """Return the fraction of characters in *text* that are punctuation."""
    punctuation = set(string.punctuation)
    return _safe_ratio(sum(char in punctuation for char in text), len(text))


def whitespace_ratio(text: str) -> float:
    """Return the fraction of characters in *text* that are whitespace."""
    return _safe_ratio(sum(char.isspace() for char in text), len(text))


def non_ascii_ratio(text: str) -> float:
    """Return the fraction of characters in *text* that are outside ASCII."""
    return _safe_ratio(sum(ord(char) > 127 for char in text), len(text))


def deduplicate_texts(texts: Sequence[str], *, normalize: bool = True) -> List[str]:
    """
    Deduplicate a sequence of texts while preserving first-seen order.

    When ``normalize`` is enabled, texts are compared using Unicode
    normalization, whitespace collapsing, and case folding.
    """
    seen: set[str] = set()
    deduplicated: List[str] = []
    for text in texts:
        key = _normalized_duplicate_key(text) if normalize else text
        if key not in seen:
            seen.add(key)
            deduplicated.append(text)
    return deduplicated


def find_near_duplicates(
    texts: Sequence[str],
    threshold: float = 0.9,
    *,
    normalize: bool = True,
) -> List[Tuple[int, int, float]]:
    """
    Find near-duplicate document pairs using normalized edit similarity.

    The implementation is intentionally quadratic and therefore best suited for
    moderate-sized batches, benchmark subsets, or dataset audits rather than
    very large corpora.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in the range [0.0, 1.0]")
    prepared = [_normalized_duplicate_key(text) if normalize else text for text in texts]
    duplicates: List[Tuple[int, int, float]] = []
    for left in range(len(prepared)):
        for right in range(left + 1, len(prepared)):
            score = SequenceMatcher(None, prepared[left], prepared[right]).ratio()
            if score >= threshold:
                duplicates.append((left, right, score))
    return duplicates


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split *text* into overlapping character-bounded chunks.

    The chunker prefers whitespace boundaries when possible so the output stays
    readable and suitable for embedding, retrieval, and prompt assembly.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap < 0 or overlap >= max_chars:
        raise ValueError("overlap must be non-negative and smaller than max_chars")

    normalized = normalize_whitespace(text)
    if not normalized:
        return []

    chunks: List[str] = []
    start = 0
    text_length = len(normalized)
    while start < text_length:
        end = min(start + max_chars, text_length)
        if end < text_length:
            sentence_break = max(
                normalized.rfind(". ", start, end),
                normalized.rfind("! ", start, end),
                normalized.rfind("? ", start, end),
            )
            whitespace_break = normalized.rfind(" ", start, end)
            split_at = max(sentence_break + 1, whitespace_break)
            if split_at <= start:
                split_at = end
        else:
            split_at = end

        chunk = normalized[start:split_at].strip()
        if chunk:
            chunks.append(chunk)
        if split_at >= text_length:
            break

        start = max(0, split_at - overlap)
        while start < text_length and normalized[start].isspace():
            start += 1

    return chunks


def sliding_window_chunks(text: str, window_size: int = 200, step: int = 100) -> List[str]:
    """
    Chunk *text* in token space using a fixed sliding window.

    This is often a better fit than character chunking when downstream models
    operate on tokenized language rather than raw character counts.
    """
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    if step <= 0:
        raise ValueError("step must be positive")

    tokens = tokenize_words(text, lowercase=False)
    if not tokens:
        return []

    chunks = [
        " ".join(tokens[index : index + window_size])
        for index in range(0, len(tokens), step)
        if tokens[index : index + window_size]
    ]
    return chunks


def sentence_windows(text: str, window_size: int = 3, step: int = 1) -> List[str]:
    """Return overlapping multi-sentence windows for contextual inspection."""
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    if step <= 0:
        raise ValueError("step must be positive")

    sentences = split_sentences(text)
    if not sentences:
        return []

    windows = [
        " ".join(sentences[index : index + window_size])
        for index in range(0, len(sentences), step)
        if sentences[index : index + window_size]
    ]
    return windows


def truncate_text(text: str, max_chars: int, suffix: str = "...") -> str:
    """Truncate *text* to ``max_chars`` characters while preserving the suffix."""
    if max_chars < 0:
        raise ValueError("max_chars must be non-negative")
    if len(text) <= max_chars:
        return text
    if max_chars <= len(suffix):
        return suffix[:max_chars]
    return text[: max_chars - len(suffix)].rstrip() + suffix


def mask_sensitive_text(text: str) -> str:
    """
    Mask common sensitive substrings so text can be logged or displayed safely.

    This is intentionally conservative and pattern-based. It is meant to reduce
    accidental exposure in logs and diagnostics, not to guarantee perfect PII
    detection across all locales and formats.
    """
    masked = text
    masked = SENSITIVE_PATTERNS["ssn"].sub("[SSN]", masked)
    masked = SENSITIVE_PATTERNS["phone"].sub("[PHONE]", masked)
    masked = SENSITIVE_PATTERNS["email"].sub("[EMAIL]", masked)
    masked = SENSITIVE_PATTERNS["password"].sub("password=[REDACTED]", masked)
    masked = SENSITIVE_PATTERNS["api_key"].sub("api_key=[REDACTED]", masked)
    return masked


def redact_patterns(
    text: str,
    patterns: Sequence[str],
    *,
    replacement: str = "[REDACTED]",
    ignore_case: bool = True,
) -> str:
    """Redact each regex pattern in *patterns* from *text*."""
    flags = re.IGNORECASE if ignore_case else 0
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, replacement, redacted, flags=flags)
    return redacted


def extract_numbers(text: str) -> List[float]:
    """Extract numeric literals from *text* as floats."""
    return [float(match) for match in NUMBER_PATTERN.findall(text)]


def extract_markdown_code_blocks(text: str) -> List[str]:
    """Return fenced Markdown code blocks without their backtick wrappers."""
    return [block.strip("\n") for block in MARKDOWN_CODE_FENCE_PATTERN.findall(text)]


def extract_hashtags(text: str) -> List[str]:
    """Return hashtag tokens without the leading ``#``."""
    return HASHTAG_PATTERN.findall(text)


def extract_mentions(text: str) -> List[str]:
    """Return mention tokens without the leading ``@``."""
    return MENTION_PATTERN.findall(text)


def extract_bullet_points(text: str) -> List[str]:
    """Extract bullet-like list items from Markdown or plain-text lists."""
    bullets: List[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*(?:[-*+]\s+|\d+\.\s+)(.+)$", line)
        if match:
            bullets.append(match.group(1).strip())
    return bullets


def extract_parenthetical_phrases(text: str) -> List[str]:
    """Return phrases enclosed in parentheses."""
    return [phrase.strip() for phrase in PARENTHETICAL_PATTERN.findall(text)]


def extract_quoted_strings(text: str) -> List[str]:
    """Return strings enclosed in single or double quotes."""
    matches = QUOTED_STRING_PATTERN.findall(text)
    return [double or single for double, single in matches]


def parse_key_value_text(text: str) -> Dict[str, str]:
    """
    Parse ``key: value`` or ``key=value`` lines into a dictionary.

    Lines that do not match a supported key/value pattern are ignored, which
    keeps the function useful for mixed-format logs and config snippets.
    """
    parsed: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
        elif "=" in stripped:
            key, value = stripped.split("=", 1)
        else:
            continue
        parsed[key.strip()] = value.strip()
    return parsed


def compute_jaccard_similarity(text1: str, text2: str) -> float:
    """Return token-set Jaccard similarity between two texts."""
    tokens1 = set(tokenize_words(text1, lowercase=True))
    tokens2 = set(tokenize_words(text2, lowercase=True))
    union = tokens1 | tokens2
    if not union:
        return 1.0
    return len(tokens1 & tokens2) / len(union)


def levenshtein_distance(text1: str, text2: str) -> int:
    """
    Compute Levenshtein edit distance between two strings.

    The implementation uses the standard dynamic-programming recurrence while
    storing only two rows, which keeps memory use linear in the shorter input.
    """
    if text1 == text2:
        return 0
    if not text1:
        return len(text2)
    if not text2:
        return len(text1)
    if len(text1) < len(text2):
        text1, text2 = text2, text1

    previous = list(range(len(text2) + 1))
    for i, char1 in enumerate(text1, start=1):
        current = [i]
        for j, char2 in enumerate(text2, start=1):
            insertions = previous[j] + 1
            deletions = current[j - 1] + 1
            substitutions = previous[j - 1] + (char1 != char2)
            current.append(min(insertions, deletions, substitutions))
        previous = current
    return previous[-1]


def contains_code(text: str) -> bool:
    """
    Heuristically detect whether *text* contains code-like structure.

    The function is useful for routing mixed corpora, prompt datasets, or log
    streams where prose and source code are interleaved.
    """
    code_indicators = [
        r"\bdef\s+\w+\(",
        r"\bclass\s+\w+",
        r"\bimport\s+\w+",
        r"\breturn\b",
        r"[{};]{2,}|==|!=|<=|>=",
        r"</?[A-Za-z][^>]*>",
        r"\bSELECT\b|\bFROM\b|\bWHERE\b",
    ]
    matches = sum(bool(re.search(pattern, text, re.IGNORECASE | re.MULTILINE)) for pattern in code_indicators)
    return matches >= 2


def normalize_for_embedding(text: str) -> str:
    """
    Apply a stable normalization pipeline before embedding or retrieval.

    The pipeline intentionally keeps semantics while removing common sources of
    noise such as HTML, typographic variants, repeated whitespace, and casing
    differences.
    """
    text = strip_html(text)
    text = normalize_unicode(text, form="NFKC")
    text = normalize_quotes(text)
    text = normalize_dashes(text)
    text = strip_urls(text)
    text = normalize_whitespace(text)
    return text.casefold()


def label_text_quality(
    text: str,
    *,
    min_chars: int = 20,
    max_chars: int = 10000,
    max_symbol_ratio: float = 0.35,
) -> Dict[str, Any]:
    """
    Return simple quality flags for dataset and prompt hygiene.

    The output is designed for filtering or auditing noisy corpora before they
    enter fine-tuning, evaluation, or retrieval pipelines.
    """
    normalized = normalize_whitespace(text)
    tokens = tokenize_words(text, lowercase=True)
    repeated_token_ratio = 1.0 - _safe_ratio(len(set(tokens)), len(tokens)) if tokens else 0.0
    symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
    flags = {
        "empty": not bool(normalized),
        "too_short": len(normalized) < min_chars,
        "too_long": len(normalized) > max_chars,
        "high_symbol_ratio": _safe_ratio(symbol_count, len(text)) > max_symbol_ratio,
        "mostly_numeric": digit_ratio(text) > 0.5,
        "repeated_tokens": repeated_token_ratio > 0.6,
        "contains_url": bool(extract_urls(text)),
        "contains_email": bool(extract_emails(text)),
        "contains_code": contains_code(text),
        "contains_sensitive_text": is_sensitive_text(text),
        "token_count": len(tokens),
        "character_count": len(text),
    }
    return flags


def find_repeated_phrases(text: str, phrase_length: int = 3, min_count: int = 2) -> Dict[str, int]:
    """Return repeated token phrases of length ``phrase_length``."""
    if phrase_length <= 0:
        raise ValueError("phrase_length must be positive")
    if min_count <= 1:
        raise ValueError("min_count must be greater than 1")

    counts = ngram_counts(text, n=phrase_length)
    return {" ".join(gram): count for gram, count in counts.items() if count >= min_count}


def detect_repeated_lines(text: str, min_count: int = 2) -> Dict[str, int]:
    """Return lines that repeat at least ``min_count`` times."""
    if min_count <= 1:
        raise ValueError("min_count must be greater than 1")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    counts = Counter(lines)
    return {line: count for line, count in counts.items() if count >= min_count}


def keyword_in_context(
    text: str,
    keyword: str,
    *,
    window: int = 40,
    case_sensitive: bool = False,
) -> List[str]:
    """
    Return context windows around keyword matches.

    This mirrors a simple concordance view and is useful for corpus inspection,
    debugging retrieval hits, and validating labeling heuristics.
    """
    if window < 0:
        raise ValueError("window must be non-negative")

    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(keyword), flags)
    contexts: List[str] = []
    for match in pattern.finditer(text):
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        contexts.append(text[start:end].strip())
    return contexts


def count_pattern_occurrences(
    text: str,
    pattern: str,
    *,
    ignore_case: bool = True,
    literal: bool = False,
) -> int:
    """Count occurrences of a regex or literal pattern in *text*."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled = re.compile(re.escape(pattern) if literal else pattern, flags)
    return sum(1 for _ in compiled.finditer(text))


def filter_texts_by_length(
    texts: Sequence[str],
    *,
    min_chars: int = 0,
    max_chars: Optional[int] = None,
) -> List[str]:
    """Filter texts by inclusive character-length bounds."""
    filtered = []
    for text in texts:
        length = len(text)
        if length < min_chars:
            continue
        if max_chars is not None and length > max_chars:
            continue
        filtered.append(text)
    return filtered


def sort_texts_by_length(texts: Sequence[str], *, reverse: bool = False) -> List[str]:
    """Return *texts* sorted by character length."""
    return sorted(texts, key=len, reverse=reverse)


def safe_filename_from_text(text: str, *, max_length: int = 80, separator: str = "-") -> str:
    """
    Convert free-form text into a filesystem-friendly filename stem.

    The function is useful for saving prompts, experiment artifacts, retrieved
    passages, or human-readable cache entries derived from text content.
    """
    if max_length <= 0:
        raise ValueError("max_length must be positive")

    normalized = normalize_unicode(text, form="NFKC").casefold()
    normalized = strip_accents(normalized)
    normalized = re.sub(r"[^\w\s-]", "", normalized)
    normalized = re.sub(r"[-\s]+", separator, normalized).strip(separator)
    return truncate_text(normalized or "untitled", max_length, suffix="")


def prompt_injection_risk_flags(text: str) -> Dict[str, Any]:
    """
    Return heuristic prompt-injection risk flags for *text*.

    This is intentionally a detection aid rather than an enforcement mechanism.
    It helps researchers inspect datasets, retrieved documents, or tool inputs
    for patterns that often accompany prompt-injection attempts.
    """
    flags = {name: bool(pattern.search(text)) for name, pattern in PROMPT_INJECTION_PATTERNS.items()}
    risk_score = sum(flags.values())
    flags["risk_score"] = risk_score
    flags["high_risk"] = risk_score >= 2
    return flags
