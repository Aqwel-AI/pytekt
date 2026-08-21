"""Binary tree and trie algorithms: traversals, BST ops, LCA, validation."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple

from pytekt.algorithms.catalog import register_algorithm


class TreeNode:
    """Binary tree node."""

    __slots__ = ("val", "left", "right")

    def __init__(
        self,
        val: int = 0,
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
    ) -> None:
        self.val = val
        self.left = left
        self.right = right


class TrieNode:
    """Trie node with children map and end-of-word flag."""

    __slots__ = ("children", "is_end")

    def __init__(self) -> None:
        self.children: Dict[str, TrieNode] = {}
        self.is_end = False


@register_algorithm(category="trees", summary="Inorder traversal (left, root, right).")
def inorder_traversal(root: Optional[TreeNode]) -> List[int]:
    result: List[int] = []
    stack: List[TreeNode] = []
    node = root
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        result.append(node.val)
        node = node.right
    return result


@register_algorithm(category="trees", summary="Preorder traversal (root, left, right).")
def preorder_traversal(root: Optional[TreeNode]) -> List[int]:
    if not root:
        return []
    result: List[int] = []
    stack = [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return result


@register_algorithm(category="trees", summary="Postorder traversal (left, right, root).")
def postorder_traversal(root: Optional[TreeNode]) -> List[int]:
    if not root:
        return []
    result: List[int] = []
    stack: List[Tuple[TreeNode, bool]] = [(root, False)]
    while stack:
        node, visited = stack.pop()
        if visited:
            result.append(node.val)
        else:
            stack.append((node, True))
            if node.right:
                stack.append((node.right, False))
            if node.left:
                stack.append((node.left, False))
    return result


@register_algorithm(category="trees", summary="Level-order (BFS) traversal.")
def level_order_traversal(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    result: List[List[int]] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level_size = len(queue)
        level: List[int] = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


@register_algorithm(category="trees", summary="Search for a value in a BST.")
def bst_search(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    node = root
    while node:
        if val == node.val:
            return node
        node = node.left if val < node.val else node.right
    return None


@register_algorithm(category="trees", summary="Insert a value into a BST.")
def bst_insert(root: Optional[TreeNode], val: int) -> TreeNode:
    if not root:
        return TreeNode(val)
    node = root
    while True:
        if val < node.val:
            if node.left is None:
                node.left = TreeNode(val)
                break
            node = node.left
        else:
            if node.right is None:
                node.right = TreeNode(val)
                break
            node = node.right
    return root


@register_algorithm(category="trees", summary="Delete a value from a BST.")
def bst_delete(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    if not root:
        return None
    if val < root.val:
        root.left = bst_delete(root.left, val)
    elif val > root.val:
        root.right = bst_delete(root.right, val)
    else:
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = bst_delete(root.right, successor.val)
    return root


@register_algorithm(category="trees", summary="Minimum value node in a BST subtree.")
def bst_min(root: Optional[TreeNode]) -> Optional[TreeNode]:
    node = root
    while node and node.left:
        node = node.left
    return node


@register_algorithm(category="trees", summary="Maximum value node in a BST subtree.")
def bst_max(root: Optional[TreeNode]) -> Optional[TreeNode]:
    node = root
    while node and node.right:
        node = node.right
    return node


@register_algorithm(category="trees", summary="Validate binary search tree property.")
def validate_bst(root: Optional[TreeNode]) -> bool:
    def check(node: Optional[TreeNode], low: float, high: float) -> bool:
        if not node:
            return True
        if not (low < node.val < high):
            return False
        return check(node.left, low, node.val) and check(node.right, node.val, high)

    return check(root, float("-inf"), float("inf"))


@register_algorithm(category="trees", summary="Check if tree height is balanced (|h_l - h_r| <= 1).")
def is_balanced(root: Optional[TreeNode]) -> bool:
    def height(node: Optional[TreeNode]) -> int:
        if not node:
            return 0
        left = height(node.left)
        if left == -1:
            return -1
        right = height(node.right)
        if right == -1:
            return -1
        if abs(left - right) > 1:
            return -1
        return 1 + max(left, right)

    return height(root) != -1


@register_algorithm(category="trees", summary="Height of a binary tree.")
def tree_height(root: Optional[TreeNode]) -> int:
    if not root:
        return 0
    return 1 + max(tree_height(root.left), tree_height(root.right))


@register_algorithm(category="trees", summary="Number of nodes in a binary tree.")
def tree_size(root: Optional[TreeNode]) -> int:
    if not root:
        return 0
    return 1 + tree_size(root.left) + tree_size(root.right)


@register_algorithm(category="trees", summary="Invert (mirror) a binary tree.")
def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if not root:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root


@register_algorithm(category="trees", summary="Lowest common ancestor of two nodes.")
def lowest_common_ancestor(
    root: Optional[TreeNode], p: TreeNode, q: TreeNode
) -> Optional[TreeNode]:
    if not root or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root
    return left or right


@register_algorithm(category="trees", summary="Diameter (longest path) of a binary tree.")
def tree_diameter(root: Optional[TreeNode]) -> int:
    best = 0

    def depth(node: Optional[TreeNode]) -> int:
        nonlocal best
        if not node:
            return 0
        left = depth(node.left)
        right = depth(node.right)
        best = max(best, left + right)
        return 1 + max(left, right)

    depth(root)
    return best


@register_algorithm(category="trees", summary="Check if any root-to-leaf path sums to target.")
def path_sum_exists(root: Optional[TreeNode], target: int) -> bool:
    if not root:
        return False
    if not root.left and not root.right:
        return root.val == target
    remaining = target - root.val
    return path_sum_exists(root.left, remaining) or path_sum_exists(root.right, remaining)


@register_algorithm(category="trees", summary="Maximum path sum in a binary tree.")
def max_path_sum(root: Optional[TreeNode]) -> int:
    best = float("-inf")

    def gain(node: Optional[TreeNode]) -> int:
        nonlocal best
        if not node:
            return 0
        left = max(gain(node.left), 0)
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)
        return node.val + max(left, right)

    gain(root)
    return int(best)


@register_algorithm(category="trees", summary="Serialize binary tree to comma-separated preorder.")
def serialize_tree(root: Optional[TreeNode]) -> str:
    tokens: List[str] = []

    def dfs(node: Optional[TreeNode]) -> None:
        if not node:
            tokens.append("#")
            return
        tokens.append(str(node.val))
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return ",".join(tokens)


@register_algorithm(category="trees", summary="Deserialize comma-separated preorder tree string.")
def deserialize_tree(data: str) -> Optional[TreeNode]:
    tokens = deque(data.split(","))

    def dfs() -> Optional[TreeNode]:
        if not tokens:
            return None
        token = tokens.popleft()
        if token == "#":
            return None
        node = TreeNode(int(token))
        node.left = dfs()
        node.right = dfs()
        return node

    return dfs()


@register_algorithm(category="trees", summary="Build tree from preorder and inorder traversals.")
def build_tree_from_preorder_inorder(
    preorder: List[int], inorder: List[int]
) -> Optional[TreeNode]:
    if not preorder or not inorder:
        return None
    root_val = preorder[0]
    root = TreeNode(root_val)
    mid = inorder.index(root_val)
    root.left = build_tree_from_preorder_inorder(preorder[1 : 1 + mid], inorder[:mid])
    root.right = build_tree_from_preorder_inorder(preorder[1 + mid :], inorder[mid + 1 :])
    return root


@register_algorithm(category="trees", summary="Build balanced BST from sorted array.")
def build_bst_from_sorted(nums: List[int]) -> Optional[TreeNode]:
    def build(left: int, right: int) -> Optional[TreeNode]:
        if left > right:
            return None
        mid = (left + right) // 2
        node = TreeNode(nums[mid])
        node.left = build(left, mid - 1)
        node.right = build(mid + 1, right)
        return node

    return build(0, len(nums) - 1)


@register_algorithm(category="trees", summary="Kth smallest element in a BST (1-indexed).")
def kth_smallest_bst(root: Optional[TreeNode], k: int) -> int:
    stack: List[TreeNode] = []
    node = root
    count = 0
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        count += 1
        if count == k:
            return node.val
        node = node.right
    raise ValueError(f"k={k} out of range")


@register_algorithm(category="trees", summary="Sum of BST values in inclusive range [low, high].")
def range_sum_bst(root: Optional[TreeNode], low: int, high: int) -> int:
    if not root:
        return 0
    total = 0
    if low <= root.val <= high:
        total += root.val
    if root.val > low:
        total += range_sum_bst(root.left, low, high)
    if root.val < high:
        total += range_sum_bst(root.right, low, high)
    return total


@register_algorithm(category="trees", summary="Check if tree is symmetric around its center.")
def is_symmetric(root: Optional[TreeNode]) -> bool:
    def mirror(left: Optional[TreeNode], right: Optional[TreeNode]) -> bool:
        if not left and not right:
            return True
        if not left or not right:
            return False
        return (
            left.val == right.val
            and mirror(left.left, right.right)
            and mirror(left.right, right.left)
        )

    return mirror(root, root)


@register_algorithm(category="trees", summary="Check if two binary trees are identical.")
def same_tree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    if not p and not q:
        return True
    if not p or not q:
        return False
    return (
        p.val == q.val
        and same_tree(p.left, q.left)
        and same_tree(p.right, q.right)
    )


@register_algorithm(category="trees", summary="Insert word into a trie.")
def trie_insert(root: TrieNode, word: str) -> None:
    node = root
    for ch in word:
        if ch not in node.children:
            node.children[ch] = TrieNode()
        node = node.children[ch]
    node.is_end = True


@register_algorithm(category="trees", summary="Search for exact word in a trie.")
def trie_search(root: TrieNode, word: str) -> bool:
    node = root
    for ch in word:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return node.is_end


@register_algorithm(category="trees", summary="Check if any trie word starts with prefix.")
def trie_starts_with(root: TrieNode, prefix: str) -> bool:
    node = root
    for ch in prefix:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return True


@register_algorithm(category="trees", summary="LCA in a BST using ordering.")
def lca_bst(root: Optional[TreeNode], p: TreeNode, q: TreeNode) -> Optional[TreeNode]:
    node = root
    while node:
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node
    return None


@register_algorithm(category="trees", summary="Flatten binary tree to right-skewed list in-place order.")
def flatten_tree(root: Optional[TreeNode]) -> None:
    node = root
    while node:
        if node.left:
            predecessor = node.left
            while predecessor.right:
                predecessor = predecessor.right
            predecessor.right = node.right
            node.right = node.left
            node.left = None
        node = node.right


@register_algorithm(category="trees", summary="Count nodes in a complete binary tree.")
def count_complete_tree_nodes(root: Optional[TreeNode]) -> int:
    if not root:
        return 0
    left_depth = right_depth = 0
    left, right = root, root
    while left:
        left_depth += 1
        left = left.left
    while right:
        right_depth += 1
        right = right.right
    if left_depth == right_depth:
        return (1 << left_depth) - 1
    return 1 + count_complete_tree_nodes(root.left) + count_complete_tree_nodes(root.right)


@register_algorithm(category="trees", summary="Right-side view of binary tree (last node per level).")
def right_side_view(root: Optional[TreeNode]) -> List[int]:
    if not root:
        return []
    result: List[int] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result


@register_algorithm(category="trees", summary="Zigzag level-order traversal.")
def zigzag_level_order(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    result: List[List[int]] = []
    queue: deque[TreeNode] = deque([root])
    left_to_right = True
    while queue:
        level_size = len(queue)
        level: List[int] = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        if not left_to_right:
            level.reverse()
        result.append(level)
        left_to_right = not left_to_right
    return result


@register_algorithm(category="trees", summary="Vertical order traversal column by column.")
def vertical_order_traversal(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    columns: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    queue: deque[Tuple[TreeNode, int, int]] = deque([(root, 0, 0)])

    while queue:
        node, row, col = queue.popleft()
        columns[col].append((row, node.val))
        if node.left:
            queue.append((node.left, row + 1, col - 1))
        if node.right:
            queue.append((node.right, row + 1, col + 1))

    result: List[List[int]] = []
    for col in sorted(columns):
        entries = sorted(columns[col], key=lambda x: x[0])
        result.append([val for _, val in entries])
    return result
