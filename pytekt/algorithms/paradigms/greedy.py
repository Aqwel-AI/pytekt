"""Classic greedy algorithms."""

from __future__ import annotations

import heapq
from collections import Counter
from typing import Any, Dict, List, Tuple

from pytekt.algorithms.catalog import register_algorithm


@register_algorithm(category="greedy", summary="Maximum non-overlapping activities by finish time")
def activity_selection(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda x: x[1])
    chosen = [ordered[0]]
    last_end = ordered[0][1]
    for start, end in ordered[1:]:
        if start >= last_end:
            chosen.append((start, end))
            last_end = end
    return chosen


@register_algorithm(category="greedy", summary="Fractional knapsack maximum value")
def fractional_knapsack(weights: List[float], values: List[float], capacity: float) -> float:
    if capacity <= 0 or not weights:
        return 0.0
    items = sorted(
        ((v / w, w, v) for w, v in zip(weights, values) if w > 0),
        reverse=True,
    )
    total = 0.0
    remaining = capacity
    for ratio, w, v in items:
        take = min(w, remaining)
        total += take * ratio
        remaining -= take
        if remaining <= 0:
            break
    return total


@register_algorithm(category="greedy", summary="Huffman encoding bitstrings for symbols")
def huffman_encode(symbols: List[str], frequencies: List[int]) -> Dict[str, str]:
    if not symbols:
        return {}
    if len(symbols) == 1:
        return {symbols[0]: "0"}
    heap: List[Tuple[int, int, Any]] = []
    uid = 0
    for sym, freq in zip(symbols, frequencies):
        heapq.heappush(heap, (freq, uid, sym))
        uid += 1
    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, uid, (n1, n2)))
        uid += 1
    root = heap[0][2]

    def walk(node: Any, prefix: str, out: Dict[str, str]) -> None:
        if isinstance(node, str):
            out[node] = prefix or "0"
            return
        walk(node[0], prefix + "0", out)
        walk(node[1], prefix + "1", out)

    codes: Dict[str, str] = {}
    walk(root, "", codes)
    return codes


@register_algorithm(category="greedy", summary="Huffman decode bitstring to symbols")
def huffman_decode(encoded: str, codes: Dict[str, str]) -> str:
    if not encoded:
        return ""
    rev = {bits: sym for sym, bits in codes.items()}
    out: List[str] = []
    cur = ""
    for bit in encoded:
        cur += bit
        if cur in rev:
            out.append(rev[cur])
            cur = ""
    if cur:
        raise ValueError("invalid Huffman bitstream")
    return "".join(out)


@register_algorithm(category="greedy", summary="Weighted interval scheduling by earliest finish")
def interval_scheduling(intervals: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda x: x[1])
    chosen: List[Tuple[int, int, int]] = []
    last_end = -1
    for start, end, weight in ordered:
        if start >= last_end:
            chosen.append((start, end, weight))
            last_end = end
    return chosen


@register_algorithm(category="greedy", summary="Minimum railway platforms required")
def min_platforms(arrivals: List[int], departures: List[int]) -> int:
    if not arrivals:
        return 0
    events: List[Tuple[int, int]] = []
    for t in arrivals:
        events.append((t, 1))
    for t in departures:
        events.append((t, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    cur = best = 0
    for _, delta in events:
        cur += delta
        best = max(best, cur)
    return best


@register_algorithm(category="greedy", summary="Maximum meetings in one room")
def max_meetings(intervals: List[Tuple[int, int]]) -> int:
    return len(activity_selection(intervals))


@register_algorithm(category="greedy", summary="Job sequencing with deadlines and profits")
def job_sequencing(jobs: List[Tuple[int, int, int]]) -> int:
    if not jobs:
        return 0
    ordered = sorted(jobs, key=lambda x: x[2], reverse=True)
    max_deadline = max(d for _, d, _ in jobs)
    slots = [-1] * (max_deadline + 1)
    profit = 0
    for job_id, deadline, p in ordered:
        for slot in range(min(deadline, max_deadline), 0, -1):
            if slots[slot] == -1:
                slots[slot] = job_id
                profit += p
                break
    return profit


@register_algorithm(category="greedy", summary="Egyptian fraction greedy decomposition")
def egyptian_fraction(numerator: int, denominator: int) -> List[Tuple[int, int]]:
    if denominator == 0:
        raise ValueError("denominator must be non-zero")
    if numerator <= 0 or denominator <= 0:
        raise ValueError("numerator and denominator must be positive")
    parts: List[Tuple[int, int]] = []
    num, den = numerator, denominator
    while num > 0:
        unit = (den + num - 1) // num
        parts.append((1, unit))
        num = num * unit - den
        den *= unit
        g = math_gcd(num, den)
        num //= g
        den //= g
    return parts


def math_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


@register_algorithm(category="greedy", summary="Prim greedy MST edge list")
def prims_greedy_mst_edges(
    graph: Dict[Any, List[Tuple[Any, float]]],
) -> List[Tuple[Any, Any, float]]:
    if not graph:
        return []
    start = next(iter(graph))
    visited = {start}
    heap: List[Tuple[float, Any, Any]] = [
        (w, start, v) for v, w in graph.get(start, [])
    ]
    heapq.heapify(heap)
    mst: List[Tuple[Any, Any, float]] = []
    while heap and len(visited) < len(graph):
        w, u, v = heapq.heappop(heap)
        if v in visited:
            continue
        visited.add(v)
        mst.append((u, v, w))
        for nxt, nw in graph.get(v, []):
            if nxt not in visited:
                heapq.heappush(heap, (nw, v, nxt))
    return mst


@register_algorithm(category="greedy", summary="Kruskal greedy MST edge list")
def kruskals_greedy_mst_edges(
    graph: Dict[Any, List[Tuple[Any, float]]],
) -> List[Tuple[Any, Any, float]]:
    parent = {node: node for node in graph}

    def find(x: Any) -> Any:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    edges: List[Tuple[float, Any, Any]] = []
    for u, nbrs in graph.items():
        for v, w in nbrs:
            if str(u) <= str(v):
                edges.append((w, u, v))
    edges.sort()
    mst: List[Tuple[Any, Any, float]] = []
    for w, u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            mst.append((u, v, w))
    return mst


@register_algorithm(category="greedy", summary="Dijkstra greedy shortest path")
def dijkstra_greedy_path(
    graph: Dict[Any, List[Tuple[Any, float]]],
    start: Any,
    end: Any,
) -> Tuple[float, List[Any]]:
    dist: Dict[Any, float] = {start: 0.0}
    prev: Dict[Any, Any] = {}
    pq: List[Tuple[float, Any]] = [(0.0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")):
            continue
        if u == end:
            break
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if end not in dist:
        return float("inf"), []
    path = [end]
    cur = end
    while cur != start:
        cur = prev[cur]
        path.append(cur)
    path.reverse()
    return dist[end], path


@register_algorithm(category="greedy", summary="Gas station circuit feasibility")
def gas_station(gas: List[int], cost: List[int]) -> int:
    if not gas:
        return -1
    total = tank = 0
    start = 0
    for i, (g, c) in enumerate(zip(gas, cost)):
        diff = g - c
        tank += diff
        total += diff
        if tank < 0:
            start = i + 1
            tank = 0
    return start if total >= 0 else -1


@register_algorithm(category="greedy", summary="Jump game reachability")
def jump_game(nums: List[int]) -> bool:
    reach = 0
    for i, jump in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + jump)
    return True


@register_algorithm(category="greedy", summary="Jump game II minimum jumps")
def jump_game_ii(nums: List[int]) -> int:
    if len(nums) <= 1:
        return 0
    jumps = 0
    cur_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
    return jumps


@register_algorithm(category="greedy", summary="Assign cookies to children greedily")
def assign_cookies(greed: List[int], cookies: List[int]) -> int:
    greed.sort()
    cookies.sort()
    i = j = satisfied = 0
    while i < len(greed) and j < len(cookies):
        if cookies[j] >= greed[i]:
            satisfied += 1
            i += 1
        j += 1
    return satisfied


@register_algorithm(category="greedy", summary="Lemonade change for $5/$10/$20 bills")
def lemonade_change(bills: List[int]) -> bool:
    five = ten = 0
    for bill in bills:
        if bill == 5:
            five += 1
        elif bill == 10:
            if five == 0:
                return False
            five -= 1
            ten += 1
        elif bill == 20:
            if ten > 0 and five > 0:
                ten -= 1
                five -= 1
            elif five >= 3:
                five -= 3
            else:
                return False
        else:
            raise ValueError("bills must be 5, 10, or 20")
    return True


@register_algorithm(category="greedy", summary="Partition labels into max parts")
def partition_labels(s: str) -> List[int]:
    last = {ch: i for i, ch in enumerate(s)}
    parts: List[int] = []
    start = end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:
            parts.append(end - start + 1)
            start = i + 1
    return parts


@register_algorithm(category="greedy", summary="Reorganize string so no adjacent equals")
def reorganize_string(s: str) -> str:
    if not s:
        return ""
    counts = Counter(s)
    max_count = max(counts.values())
    if max_count > (len(s) + 1) // 2:
        return ""
    heap = [(-cnt, ch) for ch, cnt in counts.items()]
    heapq.heapify(heap)
    result: List[str] = []
    prev_count = 0
    prev_char = ""
    while heap:
        cnt, ch = heapq.heappop(heap)
        result.append(ch)
        if prev_count < 0:
            heapq.heappush(heap, (prev_count, prev_char))
        prev_count = cnt + 1
        prev_char = ch
    return "".join(result)


@register_algorithm(category="greedy", summary="Task scheduler minimum idle slots")
def task_scheduler(tasks: List[str], n: int) -> int:
    counts = Counter(tasks)
    max_freq = max(counts.values())
    max_count = sum(1 for c in counts.values() if c == max_freq)
    return max(len(tasks), (max_freq - 1) * (n + 1) + max_count)


@register_algorithm(category="greedy", summary="Minimum arrows to burst balloons")
def minimum_arrows(points: List[List[int]]) -> int:
    if not points:
        return 0
    ordered = sorted(points, key=lambda p: p[1])
    arrows = 0
    end = float("-inf")
    for start, finish in ordered:
        if start > end:
            arrows += 1
            end = finish
    return arrows


@register_algorithm(category="greedy", summary="Remove k digits for smallest number")
def remove_k_digits(num: str, k: int) -> str:
    if k >= len(num):
        return "0"
    stack: List[str] = []
    for ch in num:
        while k > 0 and stack and stack[-1] > ch:
            stack.pop()
            k -= 1
        stack.append(ch)
    if k:
        stack = stack[:-k]
    out = "".join(stack).lstrip("0")
    return out or "0"


@register_algorithm(category="greedy", summary="Maximum removals keeping balanced parentheses")
def max_remove_to_balanced(s: str) -> int:
    balance = 0
    removals = 0
    for ch in s:
        if ch == "(":
            balance += 1
        elif ch == ")":
            if balance == 0:
                removals += 1
            else:
                balance -= 1
    removals += balance
    return removals


@register_algorithm(category="greedy", summary="Candy distribution with neighbor constraints")
def candy_distribution(ratings: List[int]) -> int:
    if not ratings:
        return 0
    n = len(ratings)
    candies = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)
    return sum(candies)


@register_algorithm(category="greedy", summary="Queue reconstruction by height")
def queue_reconstruction_by_height(people: List[List[int]]) -> List[List[int]]:
    ordered = sorted(people, key=lambda p: (-p[0], p[1]))
    result: List[List[int]] = []
    for person in ordered:
        result.insert(person[1], person)
    return result
