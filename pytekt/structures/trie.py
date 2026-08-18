"""Trie (prefix tree) for fast prefix lookup and autocomplete."""

from __future__ import annotations

from typing import Dict, List, Optional


class _TrieNode:
    __slots__ = ("children", "is_end", "value")

    def __init__(self) -> None:
        self.children: Dict[str, _TrieNode] = {}
        self.is_end: bool = False
        self.value: Optional[object] = None


class Trie:
    """
    Prefix tree supporting insert, search, delete, prefix listing, and
    autocomplete with optional associated values.
    """

    def __init__(self) -> None:
        self._root = _TrieNode()
        self._size = 0

    def insert(self, word: str, value: object = None) -> None:
        node = self._root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = _TrieNode()
            node = node.children[ch]
        if not node.is_end:
            self._size += 1
        node.is_end = True
        node.value = value

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_end

    def get(self, word: str) -> Optional[object]:
        """Return the value associated with *word*, or ``None``."""
        node = self._find_node(word)
        if node is not None and node.is_end:
            return node.value
        return None

    def starts_with(self, prefix: str) -> List[str]:
        """Return all words that begin with *prefix*."""
        node = self._find_node(prefix)
        if node is None:
            return []
        results: List[str] = []
        self._collect(node, list(prefix), results)
        return results

    def delete(self, word: str) -> bool:
        """Remove *word* from the trie. Returns ``True`` if it was present."""
        return self._delete(self._root, word, 0)

    def __len__(self) -> int:
        return self._size

    def __contains__(self, word: str) -> bool:
        return self.search(word)

    def _find_node(self, prefix: str) -> Optional[_TrieNode]:
        node = self._root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _collect(self, node: _TrieNode, path: List[str], results: List[str]) -> None:
        if node.is_end:
            results.append("".join(path))
        for ch, child in sorted(node.children.items()):
            path.append(ch)
            self._collect(child, path, results)
            path.pop()

    def _delete(self, node: _TrieNode, word: str, depth: int) -> bool:
        if depth == len(word):
            if not node.is_end:
                return False
            node.is_end = False
            node.value = None
            self._size -= 1
            return len(node.children) == 0
        ch = word[depth]
        child = node.children.get(ch)
        if child is None:
            return False
        should_remove = self._delete(child, word, depth + 1)
        if should_remove:
            del node.children[ch]
            return not node.is_end and len(node.children) == 0
        return False
