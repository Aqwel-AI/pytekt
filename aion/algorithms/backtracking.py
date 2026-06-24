"""Backtracking algorithms (stdlib only)."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from .catalog import register_algorithm


@register_algorithm(category="backtracking", summary="All permutations of a list.")
def permutations(nums: List[int]) -> List[List[int]]:
    out: List[List[int]] = []

    def backtrack(path: List[int], remaining: List[int]) -> None:
        if not remaining:
            out.append(path[:])
            return
        for i, x in enumerate(remaining):
            path.append(x)
            backtrack(path, remaining[:i] + remaining[i + 1 :])
            path.pop()

    backtrack([], nums)
    return out


@register_algorithm(category="backtracking", summary="All k-combinations of n elements labeled 1..n.")
def combinations(n: int, k: int) -> List[List[int]]:
    out: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        if len(path) == k:
            out.append(path[:])
            return
        need = k - len(path)
        for i in range(start, n - need + 2):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return out


@register_algorithm(category="backtracking", summary="All subsets (power set) of nums.")
def subsets(nums: List[int]) -> List[List[int]]:
    out: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        out.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return out


@register_algorithm(category="backtracking", summary="Combinations summing to target (reuse allowed).")
def combination_sum(candidates: List[int], target: int) -> List[List[int]]:
    out: List[List[int]] = []
    candidates.sort()

    def backtrack(start: int, remain: int, path: List[int]) -> None:
        if remain == 0:
            out.append(path[:])
            return
        for i in range(start, len(candidates)):
            val = candidates[i]
            if val > remain:
                break
            path.append(val)
            backtrack(i, remain - val, path)
            path.pop()

    backtrack(0, target, [])
    return out


@register_algorithm(category="backtracking", summary="Combinations summing to target without reusing same index.")
def combination_sum_ii(candidates: List[int], target: int) -> List[List[int]]:
    out: List[List[int]] = []
    candidates.sort()

    def backtrack(start: int, remain: int, path: List[int]) -> None:
        if remain == 0:
            out.append(path[:])
            return
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue
            val = candidates[i]
            if val > remain:
                break
            path.append(val)
            backtrack(i + 1, remain - val, path)
            path.pop()

    backtrack(0, target, [])
    return out


@register_algorithm(category="backtracking", summary="Letter combinations from phone digit string.")
def letter_combinations(digits: str) -> List[str]:
    if not digits:
        return []
    phone = {
        "2": "abc",
        "3": "def",
        "4": "ghi",
        "5": "jkl",
        "6": "mno",
        "7": "pqrs",
        "8": "tuv",
        "9": "wxyz",
    }
    out: List[str] = []

    def backtrack(idx: int, path: List[str]) -> None:
        if idx == len(digits):
            out.append("".join(path))
            return
        for ch in phone[digits[idx]]:
            path.append(ch)
            backtrack(idx + 1, path)
            path.pop()

    backtrack(0, [])
    return out


@register_algorithm(category="backtracking", summary="All valid parentheses strings of n pairs.")
def generate_parentheses(n: int) -> List[str]:
    out: List[str] = []

    def backtrack(opened: int, closed: int, path: List[str]) -> None:
        if len(path) == 2 * n:
            out.append("".join(path))
            return
        if opened < n:
            path.append("(")
            backtrack(opened + 1, closed, path)
            path.pop()
        if closed < opened:
            path.append(")")
            backtrack(opened, closed + 1, path)
            path.pop()

    backtrack(0, 0, [])
    return out


@register_algorithm(category="backtracking", summary="Count solutions to N-Queens on n x n board.")
def n_queens_count(n: int) -> int:
    cols: Set[int] = set()
    diag1: Set[int] = set()
    diag2: Set[int] = set()
    count = 0

    def backtrack(row: int) -> None:
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            d1, d2 = row - col, row + col
            if col in cols or d1 in diag1 or d2 in diag2:
                continue
            cols.add(col)
            diag1.add(d1)
            diag2.add(d2)
            backtrack(row + 1)
            cols.remove(col)
            diag1.remove(d1)
            diag2.remove(d2)

    backtrack(0)
    return count


@register_algorithm(category="backtracking", summary="All N-Queens board configurations.")
def n_queens_solutions(n: int) -> List[List[str]]:
    cols: Set[int] = set()
    diag1: Set[int] = set()
    diag2: Set[int] = set()
    boards: List[List[str]] = []
    placement = [-1] * n

    def backtrack(row: int) -> None:
        if row == n:
            boards.append(
                ["." * c + "Q" + "." * (n - c - 1) for c in placement]
            )
            return
        for col in range(n):
            d1, d2 = row - col, row + col
            if col in cols or d1 in diag1 or d2 in diag2:
                continue
            cols.add(col)
            diag1.add(d1)
            diag2.add(d2)
            placement[row] = col
            backtrack(row + 1)
            cols.remove(col)
            diag1.remove(d1)
            diag2.remove(d2)

    backtrack(0)
    return boards


@register_algorithm(category="backtracking", summary="Solve 9x9 Sudoku in-place on copied grid.")
def sudoku_solve(board: List[List[str]]) -> Optional[List[List[str]]]:
    grid = [row[:] for row in board]
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empty: List[Tuple[int, int]] = []
    for r in range(9):
        for c in range(9):
            ch = grid[r][c]
            if ch == ".":
                empty.append((r, c))
            else:
                rows[r].add(ch)
                cols[c].add(ch)
                boxes[(r // 3) * 3 + c // 3].add(ch)

    def backtrack(idx: int) -> bool:
        if idx == len(empty):
            return True
        r, c = empty[idx]
        b = (r // 3) * 3 + c // 3
        for d in "123456789":
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                continue
            grid[r][c] = d
            rows[r].add(d)
            cols[c].add(d)
            boxes[b].add(d)
            if backtrack(idx + 1):
                return True
            grid[r][c] = "."
            rows[r].remove(d)
            cols[c].remove(d)
            boxes[b].remove(d)
        return False

    return grid if backtrack(0) else None


@register_algorithm(category="backtracking", summary="Whether word exists in letter grid.")
def word_search(board: List[List[str]], word: str) -> bool:
    if not word:
        return True
    rows, cols = len(board), len(board[0])

    def dfs(r: int, c: int, idx: int) -> bool:
        if idx == len(word):
            return True
        if r < 0 or c < 0 or r >= rows or c >= cols or board[r][c] != word[idx]:
            return False
        tmp = board[r][c]
        board[r][c] = "#"
        found = (
            dfs(r + 1, c, idx + 1)
            or dfs(r - 1, c, idx + 1)
            or dfs(r, c + 1, idx + 1)
            or dfs(r, c - 1, idx + 1)
        )
        board[r][c] = tmp
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False


@register_algorithm(category="backtracking", summary="Partition string into palindrome substrings.")
def palindrome_partitioning(s: str) -> List[List[str]]:
    out: List[List[str]] = []

    def is_pal(lo: int, hi: int) -> bool:
        while lo < hi:
            if s[lo] != s[hi]:
                return False
            lo += 1
            hi -= 1
        return True

    def backtrack(start: int, path: List[str]) -> None:
        if start == len(s):
            out.append(path[:])
            return
        for end in range(start, len(s)):
            if is_pal(start, end):
                path.append(s[start : end + 1])
                backtrack(end + 1, path)
                path.pop()

    backtrack(0, [])
    return out


@register_algorithm(category="backtracking", summary="Restore valid IP addresses from digit string.")
def restore_ip_addresses(s: str) -> List[str]:
    out: List[str] = []

    def valid(segment: str) -> bool:
        return len(segment) <= 3 and (not segment.startswith("0") or segment == "0") and int(segment) <= 255

    def backtrack(start: int, parts: List[str]) -> None:
        if len(parts) == 4:
            if start == len(s):
                out.append(".".join(parts))
            return
        for end in range(start + 1, min(start + 4, len(s) + 1)):
            seg = s[start:end]
            if valid(seg):
                parts.append(seg)
                backtrack(end, parts)
                parts.pop()

    backtrack(0, [])
    return out


@register_algorithm(category="backtracking", summary="Subsets with duplicate elements.")
def subsets_with_dup(nums: List[int]) -> List[List[int]]:
    nums.sort()
    out: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        out.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return out


@register_algorithm(category="backtracking", summary="Unique permutations of list with duplicates.")
def permutations_unique(nums: List[int]) -> List[List[int]]:
    nums.sort()
    out: List[List[int]] = []
    used = [False] * len(nums)

    def backtrack(path: List[int]) -> None:
        if len(path) == len(nums):
            out.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i] or (i > 0 and nums[i] == nums[i - 1] and not used[i - 1]):
                continue
            used[i] = True
            path.append(x)
            backtrack(path)
            path.pop()
            used[i] = False

    backtrack([])
    return out


@register_algorithm(category="backtracking", summary="Combinations of k numbers 1-9 summing to n.")
def combination_sum_iii(k: int, n: int) -> List[List[int]]:
    out: List[List[int]] = []

    def backtrack(start: int, remain: int, path: List[int]) -> None:
        if len(path) == k:
            if remain == 0:
                out.append(path[:])
            return
        need = k - len(path)
        for i in range(start, 10 - need + 1):
            if i > remain:
                break
            path.append(i)
            backtrack(i + 1, remain - i, path)
            path.pop()

    backtrack(1, n, [])
    return out


@register_algorithm(category="backtracking", summary="Whether array can be partitioned into k equal-sum subsets.")
def partition_k_equal_sum(nums: List[int], k: int) -> bool:
    if k <= 0:
        return False
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    nums.sort(reverse=True)
    used = [False] * len(nums)

    def backtrack(bucket: int, idx: int, current: int) -> bool:
        if bucket == k:
            return True
        if current == target:
            return backtrack(bucket + 1, 0, 0)
        seen: Set[int] = set()
        for i in range(idx, len(nums)):
            if used[i] or nums[i] in seen:
                continue
            if current + nums[i] > target:
                continue
            seen.add(nums[i])
            used[i] = True
            if backtrack(bucket, i + 1, current + nums[i]):
                return True
            used[i] = False
        return False

    return backtrack(0, 0, 0)


@register_algorithm(category="backtracking", summary="Whether path exists in maze from start to end.")
def solve_maze(maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> bool:
    rows, cols = len(maze), len(maze[0])
    visited = [[False] * cols for _ in range(rows)]

    def dfs(r: int, c: int) -> bool:
        if (r, c) == end:
            return True
        visited[r][c] = True
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and not visited[nr][nc]:
                if dfs(nr, nc):
                    return True
        return False

    sr, sc = start
    if maze[sr][sc] == 1:
        return False
    return dfs(sr, sc)


@register_algorithm(category="backtracking", summary="Count all paths in maze from top-left to bottom-right.")
def rat_in_maze_paths(maze: List[List[int]]) -> int:
    rows, cols = len(maze), len(maze[0])
    if maze[0][0] == 1 or maze[rows - 1][cols - 1] == 1:
        return 0
    count = 0

    def dfs(r: int, c: int) -> None:
        nonlocal count
        if r == rows - 1 and c == cols - 1:
            count += 1
            return
        tmp = maze[r][c]
        maze[r][c] = 1
        for dr, dc in ((0, 1), (1, 0)):
            nr, nc = r + dr, c + dc
            if nr < rows and nc < cols and maze[nr][nc] == 0:
                dfs(nr, nc)
        maze[r][c] = tmp

    dfs(0, 0)
    return count


@register_algorithm(category="backtracking", summary="Whether subset of nums sums to target.")
def subset_sum_exists(nums: List[int], target: int) -> bool:
    nums.sort()

    def backtrack(idx: int, remain: int) -> bool:
        if remain == 0:
            return True
        for i in range(idx, len(nums)):
            if nums[i] > remain:
                break
            if backtrack(i + 1, remain - nums[i]):
                return True
        return False

    return backtrack(0, target)


@register_algorithm(category="backtracking", summary="Count Hamiltonian paths in undirected graph adjacency list.")
def hamiltonian_path_count(adj: List[List[int]], n: int) -> int:
    count = 0
    visited = [False] * n

    def dfs(node: int, depth: int) -> None:
        nonlocal count
        if depth == n:
            count += 1
            return
        for nxt in adj[node]:
            if not visited[nxt]:
                visited[nxt] = True
                dfs(nxt, depth + 1)
                visited[nxt] = False

    for start in range(n):
        visited[start] = True
        dfs(start, 1)
        visited[start] = False
    return count


@register_algorithm(category="backtracking", summary="Graph m-coloring feasibility.")
def graph_coloring_possible(adj: List[List[int]], m: int) -> bool:
    n = len(adj)
    colors = [0] * n

    def valid(node: int, color: int) -> bool:
        for nxt in adj[node]:
            if colors[nxt] == color:
                return False
        return True

    def backtrack(node: int) -> bool:
        if node == n:
            return True
        for c in range(1, m + 1):
            if valid(node, c):
                colors[node] = c
                if backtrack(node + 1):
                    return True
                colors[node] = 0
        return False

    return backtrack(0)


@register_algorithm(category="backtracking", summary="All ways to segment string into dictionary words.")
def word_break_all(s: str, word_dict: List[str]) -> List[str]:
    words = set(word_dict)
    out: List[str] = []
    n = len(s)

    def backtrack(start: int, path: List[str]) -> None:
        if start == n:
            out.append(" ".join(path))
            return
        for end in range(start + 1, n + 1):
            word = s[start:end]
            if word in words:
                path.append(word)
                backtrack(end, path)
                path.pop()

    backtrack(0, [])
    return out


@register_algorithm(category="backtracking", summary="Ways to insert + and - between digits to reach target.")
def expression_add_operators(num: str, target: int) -> List[str]:
    out: List[str] = []

    def backtrack(idx: int, path: str, value: int, last: int) -> None:
        if idx == len(num):
            if value == target:
                out.append(path)
            return
        for end in range(idx + 1, len(num) + 1):
            if num[idx] == "0" and end > idx + 1:
                break
            cur = int(num[idx:end])
            if idx == 0:
                backtrack(end, num[idx:end], cur, cur)
            else:
                backtrack(end, path + "+" + num[idx:end], value + cur, cur)
                backtrack(end, path + "-" + num[idx:end], value - cur, -cur)
                backtrack(end, path + "*" + num[idx:end], value - last + last * cur, last * cur)

    backtrack(0, "", 0, 0)
    return out


@register_algorithm(category="backtracking", summary="Count valid Android unlock patterns of length m on 3x3 grid.")
def android_unlock_patterns(m: int) -> int:
    if m < 1:
        return 0
    skip: Dict[Tuple[int, int], int] = {}
    for r in range(3):
        for c in range(3):
            for dr in (-2, -1, 0, 1, 2):
                for dc in (-2, -1, 0, 1, 2):
                    if dr == 0 and dc == 0:
                        continue
                    r2, c2 = r + dr, c + dc
                    if 0 <= r2 < 3 and 0 <= c2 < 3:
                        skip[(r * 3 + c, r2 * 3 + c2)] = ((r + r2) // 2) * 3 + (c + c2) // 2
    count = 0

    def dfs(node: int, visited: int, length: int) -> None:
        nonlocal count
        if length == m:
            count += 1
            return
        for nxt in range(9):
            if visited & (1 << nxt):
                continue
            mid = skip.get((node, nxt))
            if mid is not None and not (visited & (1 << mid)):
                continue
            dfs(nxt, visited | (1 << nxt), length + 1)

    for start in range(9):
        dfs(start, 1 << start, 1)
    return count


@register_algorithm(category="backtracking", summary="Maximum score placing + and - signs on digit string.")
def maximize_expression_score(digits: str) -> int:
    best = float("-inf")

    def backtrack(idx: int, current: int) -> None:
        nonlocal best
        if idx == len(digits):
            best = max(best, current)
            return
        val = int(digits[idx])
        if idx == 0:
            backtrack(idx + 1, val)
        else:
            backtrack(idx + 1, current + val)
            backtrack(idx + 1, current - val)

    backtrack(0, 0)
    return int(best)


@register_algorithm(category="backtracking", summary="One valid N-Queens column placement list.")
def n_queens_one_solution(n: int) -> List[int]:
    cols: Set[int] = set()
    diag1: Set[int] = set()
    diag2: Set[int] = set()
    placement = [-1] * n
    found = False

    def backtrack(row: int) -> bool:
        nonlocal found
        if row == n:
            found = True
            return True
        for col in range(n):
            d1, d2 = row - col, row + col
            if col in cols or d1 in diag1 or d2 in diag2:
                continue
            cols.add(col)
            diag1.add(d1)
            diag2.add(d2)
            placement[row] = col
            if backtrack(row + 1):
                return True
            cols.remove(col)
            diag1.remove(d1)
            diag2.remove(d2)
        return False

    backtrack(0)
    return placement if found else []


@register_algorithm(category="backtracking", summary="k-th lexicographic permutation of 1..n (1-indexed k).")
def kth_permutation(n: int, k: int) -> List[int]:
    nums = list(range(1, n + 1))
    k -= 1
    out: List[int] = []
    fact = 1
    for i in range(1, n):
        fact *= i
    for i in range(n, 0, -1):
        idx = k // fact
        out.append(nums.pop(idx))
        k %= fact
        if i > 1:
            fact //= (i - 1)
    return out


@register_algorithm(category="backtracking", summary="All subsets of nums with exactly k elements.")
def k_subsets(nums: List[int], k: int) -> List[List[int]]:
    out: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        if len(path) == k:
            out.append(path[:])
            return
        need = k - len(path)
        for i in range(start, len(nums) - need + 1):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return out


@register_algorithm(category="backtracking", summary="Next lexicographic permutation of nums.")
def next_permutation(nums: List[int]) -> List[int]:
    out = nums[:]
    i = len(out) - 2
    while i >= 0 and out[i] >= out[i + 1]:
        i -= 1
    if i < 0:
        out.reverse()
        return out
    j = len(out) - 1
    while out[j] <= out[i]:
        j -= 1
    out[i], out[j] = out[j], out[i]
    out[i + 1 :] = reversed(out[i + 1 :])
    return out
