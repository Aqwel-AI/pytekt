"""
Generate text with a transformer (greedy, sampling, top-k / top-p, beam).

Aligns with ``pytekt.former.experiments.train_small_model`` (same config/corpus
when using ``--config``). Optional weights from training: ``weights.npz``.

Run: python -m pytekt.former.examples.text_generation --help
"""
from __future__ import annotations

import argparse
import os
import random
import sys
import time
from typing import List, Optional, Sequence, Tuple

import numpy as np
import yaml  # type: ignore[import-untyped]

from pytekt.former.datasets import TextDataset
from pytekt.former.experiments.train_small_model import SAMPLE_TEXT, load_config
from pytekt.former.models import Transformer
from pytekt.former.training import load_transformer_weights

try:
    # Optional native acceleration (reductions / elementwise). The main speedup
    # still comes from KV-cache decoding below.
    from pytekt._core import fast_softmax as _fast_softmax_native  # type: ignore
    from pytekt._core import fast_argmax as _fast_argmax_native  # type: ignore
except Exception:
    _fast_softmax_native = None
    _fast_argmax_native = None


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / (e.sum() + 1e-30)


def _log_softmax(x: np.ndarray) -> np.ndarray:
    return np.log(_softmax(x) + 1e-30)


def _apply_repetition_penalty(
    logits: np.ndarray,
    generated: Sequence[int],
    penalty: float,
    window: Optional[int],
) -> np.ndarray:
    if penalty <= 1.0:
        return logits
    out = logits.astype(np.float64, copy=True)
    recent = list(generated) if window is None or window <= 0 else list(generated[-window:])
    if not recent:
        return out

    # Vectorized application: fewer Python ops per generation step.
    recent_ids = np.unique(np.asarray(recent, dtype=np.int64))
    recent_ids = recent_ids[(recent_ids >= 0) & (recent_ids < out.shape[0])]
    if recent_ids.size == 0:
        return out

    pos = out[recent_ids] > 0
    out[recent_ids[pos]] /= penalty
    out[recent_ids[~pos]] *= penalty
    return out


def _apply_top_k(logits: np.ndarray, k: int) -> np.ndarray:
    if k <= 0:
        return logits
    k = min(k, logits.shape[0])
    if k <= 0:
        return logits
    thr = np.partition(logits, -k)[-k]

    # In-place mask to avoid allocating an extra array for np.where.
    logits[logits < thr] = -np.inf
    return logits


def _sample_top_p(sorted_idx: np.ndarray, sorted_logits: np.ndarray, p: float) -> int:
    probs = _softmax(sorted_logits)
    cum = np.cumsum(probs)
    if p >= 1.0:
        cut = len(probs)
    else:
        cut = int(np.searchsorted(cum, p, side="right")) + 1
        cut = min(max(cut, 1), len(probs))
    probs = probs[:cut]
    probs = probs / probs.sum()
    choice = int(np.random.choice(cut, p=probs))
    return int(sorted_idx[choice])


def sample_next_token(
    logits: np.ndarray,
    *,
    temperature: float = 1.0,
    top_k: int = 0,
    top_p: float = 1.0,
    greedy: bool = False,
    repetition_penalty: float = 1.0,
    repetition_window: Optional[int] = None,
    blocked_token_ids: Optional[Sequence[int]] = None,
    generated: Sequence[int],
) -> int:
    """
    Sample one token from last-position logits (shape (vocab_size,)).
    """
    logits_arr = np.asarray(logits, dtype=np.float64)
    logits = logits_arr.ravel() if logits_arr.ndim == 1 else logits_arr[-1].ravel()

    # Prevent generating special tokens that are valid vocab entries
    # but are not meaningful for text output.
    if blocked_token_ids:
        for tid in blocked_token_ids:
            if 0 <= tid < logits.shape[0]:
                logits[tid] = -np.inf

    logits = _apply_repetition_penalty(
        logits, generated, repetition_penalty, repetition_window
    )

    if greedy or temperature <= 0:
        if _fast_argmax_native is not None:
            return int(_fast_argmax_native(logits))
        return int(np.argmax(logits))

    scaled = logits / max(temperature, 1e-8)
    scaled = _apply_top_k(scaled, top_k)

    # Fast path: if nucleus sampling is disabled, avoid sorting.
    if top_p >= 1.0:
        if _fast_softmax_native is not None:
            probs = _fast_softmax_native(scaled)
        else:
            probs = _softmax(scaled)
        j = int(np.random.choice(probs.shape[0], p=probs))
        return j

    # Nucleus sampling: needs sorting to compute cumulative probability.
    sorted_idx = np.argsort(-scaled)
    sorted_logits = scaled[sorted_idx]
    return _sample_top_p(sorted_idx, sorted_logits, top_p)


def _layer_norm_np(x: np.ndarray, gamma: np.ndarray, beta: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    # x: (B, 1, D) or (B, D)
    mean = np.mean(x, axis=-1, keepdims=True)
    var = np.var(x, axis=-1, keepdims=True)
    x_norm = (x - mean) / np.sqrt(var + eps)
    return x_norm * gamma + beta


def _feedforward_np(x: np.ndarray, ff) -> np.ndarray:
    # x: (B, 1, D)
    W1 = ff.W1._data  # (D, H)
    b1 = ff.b1._data  # (H,)
    W2 = ff.W2._data  # (H, D)
    b2 = ff.b2._data  # (D,)
    h = x @ W1 + b1
    h = np.maximum(0.0, h)
    return h @ W2 + b2


def _attention_step_np(
    x_normed: np.ndarray,
    attn,
    k_cache: Optional[np.ndarray],
    v_cache: Optional[np.ndarray],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Single-token self-attention step using KV-cache.

    x_normed: (B, 1, D)
    k_cache/v_cache: (B, H, T, Dh) or None
    Returns:
      out: (B, 1, D), new_k_cache, new_v_cache
    """
    B, _, D = x_normed.shape
    H = attn.num_heads
    Dh = D // H

    Wq = attn.W_q._data  # (D, D)
    Wk = attn.W_k._data
    Wv = attn.W_v._data
    Wo = attn.W_o._data

    q = x_normed @ Wq  # (B,1,D)
    k_new = x_normed @ Wk
    v_new = x_normed @ Wv

    # (B,1,D) -> (B,H,1,Dh)
    q = q.reshape(B, 1, H, Dh).transpose(0, 2, 1, 3)
    k_new = k_new.reshape(B, 1, H, Dh).transpose(0, 2, 1, 3)
    v_new = v_new.reshape(B, 1, H, Dh).transpose(0, 2, 1, 3)

    if k_cache is None:
        k_cache = k_new
        v_cache = v_new
    else:
        k_cache = np.concatenate([k_cache, k_new], axis=2)
        v_cache = np.concatenate([v_cache, v_new], axis=2)

    # q: (B,H,1,Dh), k_cache: (B,H,T,Dh)
    scores = np.matmul(q, k_cache.transpose(0, 1, 3, 2))  # (B,H,1,T)
    scores = scores * (1.0 / np.sqrt(Dh))

    # Softmax over T
    scores_max = np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(scores - scores_max)
    attn_weights = exp_scores / (np.sum(exp_scores, axis=-1, keepdims=True) + 1e-30)

    # (B,H,1,T) @ (B,H,T,Dh) -> (B,H,1,Dh)
    context = np.matmul(attn_weights, v_cache)
    # (B,H,1,Dh) -> (B,1,D)
    context = context.transpose(0, 2, 1, 3).reshape(B, 1, D)

    out = context @ Wo  # (B,1,D)
    return out, k_cache, v_cache


def generate_kv_cache(
    model: Transformer,
    tokenizer,
    prompt: str,
    max_new_tokens: int,
    *,
    temperature: float,
    top_k: int,
    top_p: float,
    greedy: bool,
    repetition_penalty: float,
    repetition_window: Optional[int],
    eos_token_id: Optional[int],
    seq_length: int,
    blocked_token_ids: Optional[Sequence[int]] = None,
    debug_top: bool = False,
) -> str:
    """
    Fast generation using KV-cache (single-token forward) without autograd.

    This is exact as long as the total length (prompt + new) does not exceed
    ``seq_length``, matching the original code path which doesn't slide the
    window for the full sequence.
    """
    ids = tokenizer.encode(prompt)
    if len(ids) > seq_length:
        ids = ids[-seq_length:]

    total_len_cap = seq_length
    max_new_tokens = min(max_new_tokens, total_len_cap - len(ids))

    # KV caches per transformer block: list of (k, v), each (B,H,T,Dh)
    k_caches: List[Optional[np.ndarray]] = [None for _ in model.blocks]
    v_caches: List[Optional[np.ndarray]] = [None for _ in model.blocks]

    generated: List[int] = list(ids)

    # Prepare weights for speed
    emb_w = model.embedding.weight._data  # (V, D)
    pe = model.pos_encoding._pe  # (max_len, D)

    # Process prompt tokens sequentially to fill caches
    logits: Optional[np.ndarray] = None
    for pos, tid in enumerate(ids):
        token_embed = emb_w[int(tid)] + pe[pos]
        x = token_embed.reshape(1, 1, -1)  # (B=1,1,D)

        for li, block in enumerate(model.blocks):
            x_normed = _layer_norm_np(x, block.ln1_gamma._data, block.ln1_beta._data)
            attn_out, k_new, v_new = _attention_step_np(
                x_normed, block.attn, k_caches[li], v_caches[li]
            )
            k_caches[li] = k_new
            v_caches[li] = v_new
            x = x + attn_out

            x_normed2 = _layer_norm_np(x, block.ln2_gamma._data, block.ln2_beta._data)
            ff_out = _feedforward_np(x_normed2, block.ff)
            x = x + ff_out

        # Final layer norm + LM head
        x = _layer_norm_np(x, model.ln_f_gamma._data, model.ln_f_beta._data)
        logits = x @ model.lm_head._data  # (1,1,V)
        logits = logits[0, 0]  # (V,)

        if debug_top:
            _debug_top_tokens(tokenizer, logits)

    assert logits is not None

    for _ in range(max_new_tokens):
        next_id = sample_next_token(
            logits,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            greedy=greedy,
            repetition_penalty=repetition_penalty,
            repetition_window=repetition_window,
            blocked_token_ids=blocked_token_ids,
            generated=generated,
        )
        generated.append(int(next_id))
        if eos_token_id is not None and int(next_id) == eos_token_id:
            break

        # Advance one step for the new token id
        pos = len(generated) - 1
        tid = generated[-1]
        token_embed = emb_w[int(tid)] + pe[pos]
        x = token_embed.reshape(1, 1, -1)

        for li, block in enumerate(model.blocks):
            x_normed = _layer_norm_np(x, block.ln1_gamma._data, block.ln1_beta._data)
            attn_out, k_new, v_new = _attention_step_np(
                x_normed, block.attn, k_caches[li], v_caches[li]
            )
            k_caches[li] = k_new
            v_caches[li] = v_new
            x = x + attn_out

            x_normed2 = _layer_norm_np(x, block.ln2_gamma._data, block.ln2_beta._data)
            ff_out = _feedforward_np(x_normed2, block.ff)
            x = x + ff_out

        x = _layer_norm_np(x, model.ln_f_gamma._data, model.ln_f_beta._data)
        logits = (x @ model.lm_head._data)[0, 0]

    return tokenizer.decode(generated)


def _debug_top_tokens(
    tokenizer,
    logits_row: np.ndarray,
    k: int = 5,
) -> None:
    logits_row = np.asarray(logits_row, dtype=np.float64).ravel()
    top_idx = np.argpartition(-logits_row, kth=min(k, logits_row.size - 1))[:k]
    top_idx = top_idx[np.argsort(-logits_row[top_idx])]
    probs = _softmax(logits_row)
    print(f"  [debug] top-{k} next tokens:")
    for i in top_idx[:k]:
        tok = tokenizer.decode([int(i)])
        rep = repr(tok) if len(tok) <= 20 else repr(tok[:17] + "...")
        print(f"    id={int(i):4d} p={probs[int(i)]:.4f} tok={rep}")


def _make_causal_attention_mask(
    seq_len: int,
    num_heads: int,
    batch_size: int,
    mask_value: float = -1e9,
) -> np.ndarray:
    """
    Additive causal attention mask for Transformer attention scores.

    Shape: (batch, num_heads, seq, seq)
    """
    base = np.zeros((seq_len, seq_len), dtype=np.float64)
    base[np.triu_indices(seq_len, k=1)] = mask_value
    return np.broadcast_to(
        base[None, None, :, :], (batch_size, num_heads, seq_len, seq_len)
    ).copy()


def generate(
    model: Transformer,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 50,
    temperature: float = 0.8,
    seq_length: int = 64,
    top_k: int = 0,
    top_p: float = 1.0,
    greedy: bool = False,
    repetition_penalty: float = 1.0,
    repetition_window: Optional[int] = None,
    eos_token_id: Optional[int] = None,
    blocked_token_ids: Optional[Sequence[int]] = None,
    debug_top: bool = False,
) -> str:
    """
    Autoregressive generation with temperature / top-k / top-p / greedy.
    """
    ids = tokenizer.encode(prompt)
    if len(ids) > seq_length:
        ids = ids[-seq_length:]
    generated = list(ids)
    for _ in range(max_new_tokens):
        context = np.array([generated[-seq_length:]], dtype=np.int64)
        mask = _make_causal_attention_mask(
            seq_len=context.shape[1],
            num_heads=int(getattr(model, "num_heads", 1)),
            batch_size=int(context.shape[0]),
        )
        logits_t, _ = model.forward(context, mask)
        row = logits_t._data[0]
        if debug_top and len(generated) == len(ids):
            _debug_top_tokens(tokenizer, row[-1])
        next_id = sample_next_token(
            row,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            greedy=greedy,
            repetition_penalty=repetition_penalty,
            repetition_window=repetition_window,
            blocked_token_ids=blocked_token_ids,
            generated=generated,
        )
        generated.append(next_id)
        if eos_token_id is not None and next_id == eos_token_id:
            break
    return tokenizer.decode(generated)


def generate_beam(
    model: Transformer,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 50,
    seq_length: int = 64,
    beam_width: int = 4,
    branch_factor: int = 24,
    eos_token_id: Optional[int] = None,
    blocked_token_ids: Optional[Sequence[int]] = None,
) -> str:
    """
    Beam search with per-step branching over the top ``branch_factor`` logits.
    """
    ids = tokenizer.encode(prompt)
    if len(ids) > seq_length:
        ids = ids[-seq_length:]
    beams: List[Tuple[float, List[int]]] = [(0.0, list(ids))]

    for _ in range(max_new_tokens):
        candidates: List[Tuple[float, List[int]]] = []
        done: List[Tuple[float, List[int]]] = []

        contexts = []
        beam_meta: List[Tuple[float, List[int]]] = []
        for score, seq in beams:
            if eos_token_id is not None and seq and seq[-1] == eos_token_id:
                done.append((score, seq))
                continue
            contexts.append(seq[-seq_length:])
            beam_meta.append((score, seq))

        if not contexts:
            beams = done[:beam_width] if done else beams
            break

        batch = np.array(contexts, dtype=np.int64)
        mask = _make_causal_attention_mask(
            seq_len=batch.shape[1],
            num_heads=int(getattr(model, "num_heads", 1)),
            batch_size=int(batch.shape[0]),
        )
        logits_t, _ = model.forward(batch, mask)
        last = logits_t._data[:, -1, :]

        for row, (score, seq) in zip(last, beam_meta):
            log_p = _log_softmax(np.asarray(row, dtype=np.float64))

            if blocked_token_ids:
                for tid in blocked_token_ids:
                    if 0 <= tid < log_p.shape[0]:
                        log_p[tid] = -np.inf

            bf = min(branch_factor, log_p.shape[0])
            top_i = np.argpartition(-log_p, bf - 1)[:bf]
            top_i = top_i[np.argsort(-log_p[top_i])]
            for j in top_i:
                j = int(j)
                new_seq = seq + [j]
                candidates.append((score + float(log_p[j]), new_seq))

        candidates.extend(done)
        candidates.sort(key=lambda x: -x[0])
        beams = candidates[:beam_width]
        if not beams:
            break

    best = max(beams, key=lambda x: x[0])
    return tokenizer.decode(best[1])


def build_model_and_dataset(
    corpus: str,
    config_path: Optional[str] = None,
    seq_length: Optional[int] = None,
    level: Optional[str] = None,
) -> Tuple[Transformer, TextDataset]:
    if config_path and os.path.isfile(config_path):
        cfg = yaml_load_file(config_path)
    else:
        cfg = load_config()

    data_cfg = cfg.get("data", {})
    model_cfg = cfg.get("model", {})

    sl = seq_length if seq_length is not None else data_cfg.get("seq_length", 64)
    lv = level if level is not None else data_cfg.get("level", "char")

    dataset = TextDataset(corpus, seq_length=sl, level=lv)
    vocab_size = dataset.vocab_size

    model = Transformer(
        vocab_size=vocab_size,
        embed_dim=model_cfg.get("embedding_dim", 128),
        num_heads=model_cfg.get("num_heads", 4),
        num_layers=model_cfg.get("num_layers", 2),
        max_seq_len=model_cfg.get("max_seq_len", sl),
        hidden_dim=model_cfg.get("hidden_dim"),
    )
    return model, dataset


def yaml_load_file(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def interactive_loop(
    model: Transformer,
    tokenizer,
    seq_length: int,
    args: argparse.Namespace,
    blocked_token_ids: Optional[Sequence[int]] = None,
) -> None:
    print("Interactive mode (empty line to exit).")
    while True:
        try:
            line = input("prompt> ")
        except EOFError:
            break
        if not line.strip():
            break
        t0 = time.perf_counter()
        if args.beam_width > 1:
            out = generate_beam(
                model,
                tokenizer,
                line,
                max_new_tokens=args.max_new_tokens,
                seq_length=seq_length,
                beam_width=args.beam_width,
                branch_factor=args.beam_branch,
                eos_token_id=args.eos_id,
                blocked_token_ids=blocked_token_ids,
            )
        else:
            if args.kv_cache:
                out = generate_kv_cache(
                    model,
                    tokenizer,
                    line,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    top_k=args.top_k,
                    top_p=args.top_p,
                    greedy=args.greedy,
                    repetition_penalty=args.repetition_penalty,
                    repetition_window=args.repetition_window or None,
                    eos_token_id=args.eos_id,
                    seq_length=seq_length,
                    blocked_token_ids=blocked_token_ids,
                    debug_top=args.debug_top,
                )
            else:
                out = generate(
                    model,
                    tokenizer,
                    line,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    seq_length=seq_length,
                    top_k=args.top_k,
                    top_p=args.top_p,
                    greedy=args.greedy,
                    repetition_penalty=args.repetition_penalty,
                    repetition_window=args.repetition_window or None,
                    eos_token_id=args.eos_id,
                    debug_top=args.debug_top,
                    blocked_token_ids=blocked_token_ids,
                )
        dt = time.perf_counter() - t0
        n_new = max(0, len(out) - len(line))
        tps = (n_new / dt) if dt > 0 else 0.0
        print(out)
        print(f"  ({dt:.3f}s, ~{tps:.1f} chars/s)\n")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prompt", type=str, default="To be ", help="Seed text")
    p.add_argument("--max-new-tokens", type=int, default=60)
    p.add_argument(
        "--context-length",
        type=int,
        default=None,
        help="Override decoding context length (faster with smaller values).",
    )
    p.add_argument(
        "--kv-cache",
        action="store_true",
        default=False,
        help="Enable KV-cache fast decoding (faster, but only safe when total length stays within context-length).",
    )
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--top-k", type=int, default=0, help="0 = disabled")
    p.add_argument("--top-p", type=float, default=1.0, help="1.0 = disabled (nucleus)")
    p.add_argument("--greedy", action="store_true", help="Argmax decoding")
    p.add_argument("--beam-width", type=int, default=1, help=">1 enables beam search")
    p.add_argument("--beam-branch", type=int, default=24, help="Top logits per beam step")
    p.add_argument("--repetition-penalty", type=float, default=1.0, help=">1 discourages repeats")
    p.add_argument(
        "--repetition-window",
        type=int,
        default=0,
        help="Recent tokens penalized; 0 = full sequence",
    )
    p.add_argument("--eos-id", type=int, default=None, help="Stop when this token id is emitted")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--num-samples", type=int, default=1, help="Print this many independent samples")
    p.add_argument("--block-pad", dest="block_pad", action="store_true", default=True, help="Avoid generating <pad>")
    p.add_argument("--no-block-pad", dest="block_pad", action="store_false", help="Allow generating <pad>")
    p.add_argument("--block-unk", dest="block_unk", action="store_true", default=True, help="Avoid generating <unk>")
    p.add_argument("--no-block-unk", dest="block_unk", action="store_false", help="Allow generating <unk>")
    p.add_argument(
        "--weights",
        type=str,
        default=None,
        help="Path to weights.npz (e.g. former/experiments/weights.npz after training)",
    )
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="YAML config (default: experiments/config.yaml if present)",
    )
    p.add_argument("--data-file", type=str, default=None, help="Corpus text file")
    p.add_argument("--interactive", action="store_true", help="REPL: repeated prompts")
    p.add_argument("--debug-top", action="store_true", help="Print top-5 logits after first step")
    p.add_argument("--no-time", action="store_true", help="Do not print timing line")
    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    config_path = args.config
    if config_path is None:
        default_cfg = os.path.join(
            os.path.dirname(__file__), "..", "experiments", "config.yaml"
        )
        if os.path.isfile(default_cfg):
            config_path = default_cfg

    if args.data_file and os.path.isfile(args.data_file):
        with open(args.data_file) as f:
            corpus = f.read()
    else:
        corpus = SAMPLE_TEXT

    model, dataset = build_model_and_dataset(
        corpus,
        config_path=config_path,
    )
    seq_length = dataset.seq_length
    tokenizer = dataset.tokenizer
    context_length = int(args.context_length) if args.context_length else seq_length

    blocked_token_ids: List[int] = []
    if getattr(args, "block_pad", True):
        blocked_token_ids.append(int(tokenizer.pad_id))
    if getattr(args, "block_unk", True):
        if hasattr(tokenizer, "vocab") and "<unk>" in tokenizer.vocab:
            blocked_token_ids.append(int(tokenizer.vocab["<unk>"]))

    weights_path = args.weights
    if weights_path is None:
        default_w = os.path.join(
            os.path.dirname(__file__), "..", "experiments", "weights.npz"
        )
        if os.path.isfile(default_w):
            weights_path = default_w

    if weights_path and os.path.isfile(weights_path):
        load_transformer_weights(model, weights_path)
        print(f"Loaded weights: {weights_path}")
    elif args.weights:
        print(f"Warning: weights file not found: {args.weights}", file=sys.stderr)

    if args.interactive:
        interactive_loop(
            model,
            tokenizer,
            context_length,
            args,
            blocked_token_ids=blocked_token_ids,
        )
        return

    for s in range(args.num_samples):
        if args.num_samples > 1:
            print(f"--- sample {s + 1}/{args.num_samples} ---")
        if args.seed is not None:
            np.random.seed(args.seed + s)
            random.seed(args.seed + s)

        t0 = time.perf_counter()
        if args.beam_width > 1:
            out = generate_beam(
                model,
                tokenizer,
                args.prompt,
                max_new_tokens=args.max_new_tokens,
                seq_length=context_length,
                beam_width=args.beam_width,
                branch_factor=args.beam_branch,
                eos_token_id=args.eos_id,
                blocked_token_ids=blocked_token_ids,
            )
        else:
            if args.kv_cache:
                out = generate_kv_cache(
                    model,
                    tokenizer,
                    args.prompt,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    top_k=args.top_k,
                    top_p=args.top_p,
                    greedy=args.greedy,
                    repetition_penalty=args.repetition_penalty,
                    repetition_window=args.repetition_window or None,
                    eos_token_id=args.eos_id,
                    seq_length=context_length,
                    blocked_token_ids=blocked_token_ids,
                    debug_top=args.debug_top and s == 0,
                )
            else:
                out = generate(
                    model,
                    tokenizer,
                    args.prompt,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    seq_length=context_length,
                    top_k=args.top_k,
                    top_p=args.top_p,
                    greedy=args.greedy,
                    repetition_penalty=args.repetition_penalty,
                    repetition_window=args.repetition_window or None,
                    eos_token_id=args.eos_id,
                    blocked_token_ids=blocked_token_ids,
                    debug_top=args.debug_top and s == 0,
                )
        dt = time.perf_counter() - t0

        print("Prompt:", repr(args.prompt))
        print("Generated:", out)
        if not args.no_time:
            n_new = max(0, len(out) - len(args.prompt))
            tps = n_new / dt if dt > 0 else 0.0
            print(f"Time: {dt:.3f}s (~{tps:.1f} new chars/s)")


if __name__ == "__main__":
    main()
