#!/usr/bin/env python3
"""
Aqwel-Aion - Text Embeddings and Vector Similarity
===================================================

Text-to-vector embedding and similarity: embed_text and embed_file produce
fixed-size vectors (primary: sentence-transformers all-MiniLM-L6-v2; fallback:
hash-based vectors when the library is unavailable). cosine_similarity and
related helpers support semantic search and document comparison. File input
uses automatic encoding detection.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import os
import hashlib
import pickle
import re
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
import numpy as np

# Import can fail with ImportError (missing package) or ValueError / OSError when
# sentence-transformers pulls sklearn built against a different NumPy ABI.
try:
    from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
    _HAS_SENTENCE_TRANSFORMERS = True
except (ImportError, OSError, ValueError, RuntimeError):
    SentenceTransformer = None  # type: ignore[assignment, misc]
    _HAS_SENTENCE_TRANSFORMERS = False

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]  # pragma: no cover


def embed_file(filepath: str, model_name: str = "all-MiniLM-L6-v2") -> Optional[np.ndarray]:
    """
    Read the file at filepath and return an embedding vector for its contents.
    Uses sentence-transformers when available (model_name, default all-MiniLM-L6-v2);
    otherwise returns a 384-dim hash-based fallback. Returns None if the file
    cannot be read.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if _HAS_SENTENCE_TRANSFORMERS:
            model = SentenceTransformer(model_name)
            embedding = model.encode(content)
            print(f"Embedded file: {filepath}")
            return embedding
        else:
            print(f"Embedding file (sentence-transformers not available): {filepath}")
            hash_val = int(hashlib.md5(content.encode()).hexdigest(), 16)
            return np.array([hash_val % 1000] * 384, dtype=float)
    except Exception as e:
        print(f"Error embedding file {filepath}: {e}")
        return None


def embed_text(text: str, model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """
    Return a dense embedding vector for the given text. Uses sentence-transformers
    (model_name, default all-MiniLM-L6-v2) when available; otherwise returns a
    384-dimensional hash-based vector. Shape is (384,) for the default model or
    (768,) for models like all-mpnet-base-v2.
    """
    if _HAS_SENTENCE_TRANSFORMERS:
        model = SentenceTransformer(model_name)
        return model.encode(text)
    else:
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return np.array([hash_val % 1000] * 384, dtype=float)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Return the cosine of the angle between vec1 and vec2, in [-1, 1].
    Computed as (vec1 · vec2) / (||vec1|| * ||vec2||). Returns 0.0 if either
    vector has zero norm. Both arrays must have the same shape.
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


# --- Phase 1: Core Metrics & Similarity ---

def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Return the Euclidean distance (L2 norm of difference) between vectors."""
    return float(np.linalg.norm(vec1 - vec2))


def manhattan_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Return the Manhattan distance (L1 norm of difference) between vectors."""
    return float(np.sum(np.abs(vec1 - vec2)))


def dot_product_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Return the raw dot product. Useful if vectors are already normalized."""
    return float(np.dot(vec1, vec2))


def normalize_l2(vec: np.ndarray) -> np.ndarray:
    """Force a vector to unit length (L2 norm = 1)."""
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def find_top_k(query_vec: np.ndarray, collection: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find indices and scores for the top K most similar vectors in a collection.
    Returns (scores, indices).
    """
    dot = np.dot(collection, query_vec)
    norms = np.linalg.norm(collection, axis=1) * np.linalg.norm(query_vec)
    similarities = dot / (norms + 1e-9)
    indices = np.argsort(similarities)[::-1][:k]
    return similarities[indices], indices


def batch_cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Vectorized cosine similarity against an entire matrix of embeddings."""
    dot = np.dot(matrix, query_vec)
    norms = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query_vec)
    return dot / (norms + 1e-9)


# --- Phase 2: Batch & Scaled Processing ---

def embed_batch(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """Efficiently embed multiple texts in a single pass."""
    if _HAS_SENTENCE_TRANSFORMERS:
        model = SentenceTransformer(model_name)
        return model.encode(texts, show_progress_bar=False)
    return np.array([embed_text(t, model_name) for t in texts])


def embed_directory_parallel(path: str, ext: str = ".py", max_workers: int = 4) -> Dict[str, np.ndarray]:
    """Recursively embed all files in a directory using multiple threads."""
    results = {}
    files = []
    for root, _, filenames in os.walk(path):
        for f in filenames:
            if f.endswith(ext):
                files.append(os.path.join(root, f))
                
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(embed_file, f): f for f in files}
        for future in concurrent.futures.as_completed(future_to_file):
            f = future_to_file[future]
            try:
                embedding = future.result()
                if embedding is not None:
                    results[f] = embedding
            except Exception as e:
                print(f"Error embedding {f}: {e}")
    return results


def embed_code_chunks(filepath: str, max_chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """Extract logical chunks from a file and embed them with metadata."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # Basic chunking: line-based for now
        lines = content.splitlines()
        chunks = []
        for i in range(0, len(lines), 20): # 20 lines per chunk approx
            chunk_text = "\n".join(lines[i:i+20])
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "embedding": embed_text(chunk_text),
                    "line_start": i + 1
                })
        return chunks
    except Exception:
        return []


def get_model_dimensions(model_name: str = "all-MiniLM-L6-v2") -> int:
    """Return the vector dimensionality of the specified model."""
    if "mpnet" in model_name:
        return 768
    return 384


# --- Phase 3: Storage & Caching ---

def save_embeddings_binary(filepath: str, embeddings: Dict[str, np.ndarray]) -> bool:
    """Save a dictionary of embeddings to a binary file using pickle."""
    try:
        with open(filepath, "wb") as f:
            pickle.dump(embeddings, f)
        return True
    except Exception as e:
        print(f"Error saving embeddings: {e}")
        return False


def load_embeddings_binary(filepath: str) -> Dict[str, np.ndarray]:
    """Load a dictionary of embeddings from a binary pickle file."""
    try:
        with open(filepath, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {}


def export_to_faiss_index(embeddings: np.ndarray) -> Any:
    """
    Placeholder/Helper to prepare a FAISS index from a matrix.
    Requires 'faiss' package; returns None if not available.
    """
    try:
        import faiss # type: ignore[import-not-found]
        d = embeddings.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(embeddings.astype('float32'))
        return index
    except (ImportError, Exception):
        return None


def cache_embedding(text: str, vector: np.ndarray, cache_dir: str = ".aion_cache"):
    """Save an individual embedding to a local cache directory."""
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    text_hash = hashlib.md5(text.encode()).hexdigest()
    filepath = os.path.join(cache_dir, f"{text_hash}.npy")
    np.save(filepath, vector)


def get_cached_embedding(text: str, cache_dir: str = ".aion_cache") -> Optional[np.ndarray]:
    """Retrieve an individual embedding from the local cache."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    filepath = os.path.join(cache_dir, f"{text_hash}.npy")
    if os.path.exists(filepath):
        return np.load(filepath)
    return None


# --- Phase 4: Semantic Text Operations ---

def semantic_chunking(text: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for semantic processing."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_chunk_size - overlap):
        chunks.append(" ".join(words[i : i + max_chunk_size]))
    return chunks


def semantic_deduplication(texts: List[str], threshold: float = 0.95) -> List[str]:
    """Remove semantically similar texts based on a cosine similarity threshold."""
    if not texts:
        return []
    embeddings = embed_batch(texts)
    unique_indices = [0]
    for i in range(1, len(texts)):
        is_duplicate = False
        for j in unique_indices:
            if cosine_similarity(embeddings[i], embeddings[j]) > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_indices.append(i)
    return [texts[i] for i in unique_indices]


def generate_embedding_id(text: str) -> str:
    """Generate a unique ID for a text string based on its content."""
    return hashlib.sha256(text.encode()).hexdigest()


def mask_pii_and_embed(text: str) -> np.ndarray:
    """Mask potential PII (emails) before embedding."""
    masked = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    return embed_text(masked)


# --- Phase 5: Advanced Vector Operations ---

def compute_centroid(vectors: np.ndarray) -> np.ndarray:
    """Calculate the average vector (centroid) of a set of embeddings."""
    return np.mean(vectors, axis=0)


def detect_semantic_outliers(vectors: np.ndarray, threshold: float = 0.5) -> List[int]:
    """Find indices of vectors that are significantly distant from the centroid."""
    centroid = compute_centroid(vectors)
    distances = [euclidean_distance(v, centroid) for v in vectors]
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    return [i for i, d in enumerate(distances) if d > mean_dist + 2 * std_dist]


def weighted_merge_embeddings(embeddings: List[np.ndarray], weights: List[float]) -> np.ndarray:
    """Merge multiple embeddings into one using specific weights."""
    return np.average(embeddings, axis=0, weights=weights)


def reduce_dimensions_pca(matrix: np.ndarray, n_components: int = 64) -> np.ndarray:
    """Simple PCA implementation using SVD to reduce vector dimensionality."""
    matrix_centered = matrix - np.mean(matrix, axis=0)
    _, _, vh = np.linalg.svd(matrix_centered, full_matrices=False)
    return np.dot(matrix_centered, vh.T[:, :n_components])


def cluster_embeddings_kmeans(matrix: np.ndarray, n_clusters: int = 5) -> Any:
    """
    Cluster embeddings using K-Means. Requires 'sklearn'.
    Returns cluster labels.
    """
    try:
        from sklearn.cluster import KMeans # type: ignore[import-not-found]
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto").fit(matrix)
        return kmeans.labels_
    except (ImportError, Exception):
        return None


# --- Phase 6: Search & RAG Optimization ---

def generate_query_variations(query: str) -> List[str]:
    """Placeholder for query expansion logic. Returns the original query for now."""
    return [query]


def rank_by_relevance(query: str, texts: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
    """Complete pipeline: embed query, compare against texts, and return ranked results."""
    query_vec = embed_text(query)
    text_vecs = embed_batch(texts)
    scores, indices = find_top_k(query_vec, text_vecs, k=top_k)
    
    return [{"text": texts[i], "score": float(scores[j])} for j, i in enumerate(indices)]


def compute_reciprocal_rank_fusion(results_list: List[List[str]], k: int = 60) -> List[str]:
    """Merge multiple ranked lists using the Reciprocal Rank Fusion algorithm."""
    scores: Dict[str, float] = {}
    for results in results_list:
        for rank, item in enumerate(results):
            scores[item] = scores.get(item, 0) + 1.0 / (k + rank + 1)
    
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [item for item, score in sorted_items]


def filter_by_metadata(results: List[Dict[str, Any]], key: str, value: Any) -> List[Dict[str, Any]]:
    """Filter search results based on a metadata key-value pair."""
    return [r for r in results if r.get("metadata", {}).get(key) == value]


# --- Phase 7: Evaluation & Health ---

def check_vector_compatibility(vec1: np.ndarray, vec2: np.ndarray) -> bool:
    """Check if two vectors have the same shape/dimensionality."""
    return vec1.shape == vec2.shape


def measure_embedding_drift(set_a: np.ndarray, set_b: np.ndarray) -> float:
    """Measure the semantic shift between two sets of embeddings (distance between centroids)."""
    centroid_a = compute_centroid(set_a)
    centroid_b = compute_centroid(set_b)
    return euclidean_distance(centroid_a, centroid_b)