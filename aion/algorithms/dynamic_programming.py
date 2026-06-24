"""Classic dynamic programming algorithms."""

from __future__ import annotations

import math
from typing import List, Tuple

from .catalog import register_algorithm


@register_algorithm(category="dynamic_programming", summary="Length of longest increasing subsequence")
def lis_length(nums: List[int]) -> int:
  if not nums:
    return 0
  tails: List[int] = []
  for x in nums:
    lo, hi = 0, len(tails)
    while lo < hi:
      mid = (lo + hi) // 2
      if tails[mid] < x:
        lo = mid + 1
      else:
        hi = mid
    if lo == len(tails):
      tails.append(x)
    else:
      tails[lo] = x
  return len(tails)


@register_algorithm(category="dynamic_programming", summary="One longest increasing subsequence")
def lis_sequence(nums: List[int]) -> List[int]:
  if not nums:
    return []
  n = len(nums)
  prev = [-1] * n
  tails_idx: List[int] = []
  for i, x in enumerate(nums):
    lo, hi = 0, len(tails_idx)
    while lo < hi:
      mid = (lo + hi) // 2
      if nums[tails_idx[mid]] < x:
        lo = mid + 1
      else:
        hi = mid
    if lo > 0:
      prev[i] = tails_idx[lo - 1]
    if lo == len(tails_idx):
      tails_idx.append(i)
    else:
      tails_idx[lo] = i
  k = tails_idx[-1]
  seq: List[int] = []
  while k != -1:
    seq.append(nums[k])
    k = prev[k]
  seq.reverse()
  return seq


@register_algorithm(category="dynamic_programming", summary="Longest common subsequence length")
def lcs_length(a: str, b: str) -> int:
  m, n = len(a), len(b)
  prev = [0] * (n + 1)
  for i in range(1, m + 1):
    cur = [0] * (n + 1)
    for j in range(1, n + 1):
      if a[i - 1] == b[j - 1]:
        cur[j] = prev[j - 1] + 1
      else:
        cur[j] = max(prev[j], cur[j - 1])
    prev = cur
  return prev[n]


@register_algorithm(category="dynamic_programming", summary="Longest common subsequence string")
def lcs_sequence(a: str, b: str) -> str:
  m, n = len(a), len(b)
  dp = [[0] * (n + 1) for _ in range(m + 1)]
  for i in range(1, m + 1):
    for j in range(1, n + 1):
      if a[i - 1] == b[j - 1]:
        dp[i][j] = dp[i - 1][j - 1] + 1
      else:
        dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
  i, j = m, n
  out: List[str] = []
  while i > 0 and j > 0:
    if a[i - 1] == b[j - 1]:
      out.append(a[i - 1])
      i -= 1
      j -= 1
    elif dp[i - 1][j] >= dp[i][j - 1]:
      i -= 1
    else:
      j -= 1
  out.reverse()
  return "".join(out)


@register_algorithm(category="dynamic_programming", summary="Levenshtein edit distance")
def edit_distance(a: str, b: str) -> int:
  m, n = len(a), len(b)
  prev = list(range(n + 1))
  for i in range(1, m + 1):
    cur = [i] + [0] * n
    for j in range(1, n + 1):
      cost = 0 if a[i - 1] == b[j - 1] else 1
      cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
    prev = cur
  return prev[n]


@register_algorithm(category="dynamic_programming", summary="Longest common contiguous substring")
def longest_common_substring(a: str, b: str) -> str:
  m, n = len(a), len(b)
  best_len = 0
  end = 0
  prev = [0] * (n + 1)
  for i in range(1, m + 1):
    cur = [0] * (n + 1)
    for j in range(1, n + 1):
      if a[i - 1] == b[j - 1]:
        cur[j] = prev[j - 1] + 1
        if cur[j] > best_len:
          best_len = cur[j]
          end = i
    prev = cur
  return a[end - best_len : end]


@register_algorithm(category="dynamic_programming", summary="0/1 knapsack maximum value")
def knapsack_01_max_value(weights: List[int], values: List[int], capacity: int) -> int:
  dp = [0] * (capacity + 1)
  for w, v in zip(weights, values):
    for c in range(capacity, w - 1, -1):
      dp[c] = max(dp[c], dp[c - w] + v)
  return dp[capacity]


@register_algorithm(category="dynamic_programming", summary="0/1 knapsack selected item indices")
def knapsack_01_items(weights: List[int], values: List[int], capacity: int) -> List[int]:
  n = len(weights)
  dp = [[0] * (capacity + 1) for _ in range(n + 1)]
  for i in range(1, n + 1):
    w, v = weights[i - 1], values[i - 1]
    for c in range(capacity + 1):
      dp[i][c] = dp[i - 1][c]
      if w <= c:
        dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)
  chosen: List[int] = []
  c = capacity
  for i in range(n, 0, -1):
    if dp[i][c] != dp[i - 1][c]:
      chosen.append(i - 1)
      c -= weights[i - 1]
  chosen.reverse()
  return chosen


@register_algorithm(category="dynamic_programming", summary="Unbounded knapsack maximum value")
def unbounded_knapsack(weights: List[int], values: List[int], capacity: int) -> int:
  dp = [0] * (capacity + 1)
  for c in range(1, capacity + 1):
    best = 0
    for w, v in zip(weights, values):
      if w <= c:
        best = max(best, dp[c - w] + v)
    dp[c] = best
  return dp[capacity]


@register_algorithm(category="dynamic_programming", summary="Minimum coins to make amount")
def coin_change_min_coins(coins: List[int], amount: int) -> int:
  if amount == 0:
    return 0
  inf = amount + 1
  dp = [inf] * (amount + 1)
  dp[0] = 0
  for a in range(1, amount + 1):
    for coin in coins:
      if coin <= a:
        dp[a] = min(dp[a], dp[a - coin] + 1)
  return -1 if dp[amount] > amount else dp[amount]


@register_algorithm(category="dynamic_programming", summary="Number of coin change orderings")
def coin_change_ways(coins: List[int], amount: int) -> int:
  dp = [0] * (amount + 1)
  dp[0] = 1
  for coin in coins:
    for a in range(coin, amount + 1):
      dp[a] += dp[a - coin]
  return dp[amount]


@register_algorithm(category="dynamic_programming", summary="Matrix chain multiplication min scalar multiplications")
def matrix_chain_order(dims: List[int]) -> int:
  n = len(dims) - 1
  if n <= 1:
    return 0
  dp = [[0] * n for _ in range(n)]
  for length in range(2, n + 1):
    for i in range(n - length + 1):
      j = i + length - 1
      dp[i][j] = math.inf
      for k in range(i, j):
        cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
        dp[i][j] = min(dp[i][j], cost)
  return int(dp[0][n - 1])


@register_algorithm(category="dynamic_programming", summary="Minimum cuts to partition string into palindromes")
def palindrome_partitioning_min_cut(s: str) -> int:
  n = len(s)
  if n == 0:
    return 0
  is_pal = [[False] * n for _ in range(n)]
  for i in range(n - 1, -1, -1):
    for j in range(i, n):
      if s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1]):
        is_pal[i][j] = True
  cuts = [0] * n
  for j in range(n):
    cuts[j] = 0 if is_pal[0][j] else min(cuts[i] + 1 for i in range(j) if is_pal[i + 1][j])
  return cuts[n - 1]


@register_algorithm(category="dynamic_programming", summary="Maximum subarray sum (Kadane)")
def max_subarray_sum(nums: List[int]) -> int:
  if not nums:
    return 0
  best = cur = nums[0]
  for x in nums[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)
  return best


@register_algorithm(category="dynamic_programming", summary="Maximum product subarray")
def max_product_subarray(nums: List[int]) -> int:
  if not nums:
    return 0
  best = nums[0]
  cur_max = cur_min = nums[0]
  for x in nums[1:]:
    if x < 0:
      cur_max, cur_min = cur_min, cur_max
    cur_max = max(x, cur_max * x)
    cur_min = min(x, cur_min * x)
    best = max(best, cur_max)
  return best


@register_algorithm(category="dynamic_programming", summary="House robber maximum loot on a street")
def house_robber(nums: List[int]) -> int:
  prev2 = prev1 = 0
  for x in nums:
    prev2, prev1 = prev1, max(prev1, prev2 + x)
  return prev1


@register_algorithm(category="dynamic_programming", summary="House robber on a circular street")
def house_robber_circular(nums: List[int]) -> int:
  if not nums:
    return 0
  if len(nums) == 1:
    return nums[0]

  def rob_linear(houses: List[int]) -> int:
    prev2 = prev1 = 0
    for x in houses:
      prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1

  return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))


@register_algorithm(category="dynamic_programming", summary="Count ways to decode a digit string")
def decode_ways(s: str) -> int:
  if not s or s[0] == "0":
    return 0
  n = len(s)
  prev2, prev1 = 1, 1
  for i in range(1, n):
    cur = 0
    if s[i] != "0":
      cur += prev1
    two = int(s[i - 1 : i + 1])
    if 10 <= two <= 26:
      cur += prev2
    prev2, prev1 = prev1, cur
  return prev1


@register_algorithm(category="dynamic_programming", summary="Unique paths in m-by-n grid")
def unique_paths(m: int, n: int) -> int:
  dp = [1] * n
  for _ in range(1, m):
    for j in range(1, n):
      dp[j] += dp[j - 1]
  return dp[n - 1]


@register_algorithm(category="dynamic_programming", summary="Unique paths with obstacles")
def unique_paths_with_obstacles(grid: List[List[int]]) -> int:
  if not grid or not grid[0] or grid[0][0] == 1:
    return 0
  m, n = len(grid), len(grid[0])
  dp = [0] * n
  dp[0] = 1
  for i in range(m):
    for j in range(n):
      if grid[i][j] == 1:
        dp[j] = 0
      elif j > 0:
        dp[j] += dp[j - 1]
  return dp[n - 1]


@register_algorithm(category="dynamic_programming", summary="Minimum path sum in a grid")
def minimum_path_sum(grid: List[List[int]]) -> int:
  if not grid or not grid[0]:
    return 0
  m, n = len(grid), len(grid[0])
  dp = [math.inf] * n
  dp[0] = 0
  for i in range(m):
    dp[0] = dp[0] + grid[i][0]
    for j in range(1, n):
      dp[j] = min(dp[j], dp[j - 1]) + grid[i][j]
  return dp[n - 1]


@register_algorithm(category="dynamic_programming", summary="Minimum path sum in a number triangle")
def triangle_min_path(triangle: List[List[int]]) -> int:
  if not triangle:
    return 0
  dp = triangle[-1][:]
  for i in range(len(triangle) - 2, -1, -1):
    row = triangle[i]
    for j in range(len(row)):
      dp[j] = row[j] + min(dp[j], dp[j + 1])
  return dp[0]


@register_algorithm(category="dynamic_programming", summary="Word break feasibility")
def word_break(s: str, word_dict: List[str]) -> bool:
  words = set(word_dict)
  n = len(s)
  dp = [False] * (n + 1)
  dp[0] = True
  for i in range(1, n + 1):
    for j in range(i):
      if dp[j] and s[j:i] in words:
        dp[i] = True
        break
  return dp[n]


@register_algorithm(category="dynamic_programming", summary="Count word break segmentations")
def word_break_ii_count(s: str, word_dict: List[str]) -> int:
  words = set(word_dict)
  n = len(s)
  dp = [0] * (n + 1)
  dp[n] = 1
  for i in range(n - 1, -1, -1):
    for j in range(i + 1, n + 1):
      if s[i:j] in words:
        dp[i] += dp[j]
  return dp[0]


@register_algorithm(category="dynamic_programming", summary="Check if s3 is interleaving of s1 and s2")
def interleaving_string(s1: str, s2: str, s3: str) -> bool:
  if len(s1) + len(s2) != len(s3):
    return False
  dp = [False] * (len(s2) + 1)
  dp[0] = True
  for j, ch in enumerate(s2, 1):
    dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]
  for i in range(1, len(s1) + 1):
    dp[0] = dp[0] and s1[i - 1] == s3[i - 1]
    for j in range(1, len(s2) + 1):
      dp[j] = (dp[j] and s1[i - 1] == s3[i + j - 1]) or (
        dp[j - 1] and s2[j - 1] == s3[i + j - 1]
      )
  return dp[len(s2)]


@register_algorithm(category="dynamic_programming", summary="Simple regex match with . and *")
def regex_match_simple(s: str, p: str) -> bool:
  m, n = len(s), len(p)
  dp = [[False] * (n + 1) for _ in range(m + 1)]
  dp[0][0] = True
  for j in range(2, n + 1):
    if p[j - 1] == "*":
      dp[0][j] = dp[0][j - 2]
  for i in range(1, m + 1):
    for j in range(1, n + 1):
      if p[j - 1] == "*":
        dp[i][j] = dp[i][j - 2]
        if p[j - 2] == "." or p[j - 2] == s[i - 1]:
          dp[i][j] = dp[i][j] or dp[i - 1][j]
      elif p[j - 1] == "." or p[j - 1] == s[i - 1]:
        dp[i][j] = dp[i - 1][j - 1]
  return dp[m][n]


@register_algorithm(category="dynamic_programming", summary="Burst balloons maximum coins")
def burst_balloons(nums: List[int]) -> int:
  balloons = [1] + nums + [1]
  n = len(balloons)
  dp = [[0] * n for _ in range(n)]
  for length in range(3, n + 1):
    for left in range(n - length + 1):
      right = left + length - 1
      for k in range(left + 1, right):
        coins = (
          balloons[left] * balloons[k] * balloons[right]
          + dp[left][k]
          + dp[k][right]
        )
        dp[left][right] = max(dp[left][right], coins)
  return dp[0][n - 1]


@register_algorithm(category="dynamic_programming", summary="Stone game: first player wins")
def stone_game(piles: List[int]) -> bool:
  n = len(piles)
  dp = [[0] * n for _ in range(n)]
  for i in range(n):
    dp[i][i] = piles[i]
  for length in range(2, n + 1):
    for i in range(n - length + 1):
      j = i + length - 1
      dp[i][j] = max(piles[i] - dp[i + 1][j], piles[j] - dp[i][j - 1])
  return dp[0][n - 1] > 0


@register_algorithm(category="dynamic_programming", summary="Largest square of ones in binary matrix")
def max_square(matrix: List[List[int]]) -> int:
  if not matrix or not matrix[0]:
    return 0
  m, n = len(matrix), len(matrix[0])
  prev = [0] * (n + 1)
  best = 0
  for i in range(m):
    cur = [0] * (n + 1)
    for j in range(n):
      if matrix[i][j] == 1:
        side = min(prev[j], prev[j + 1], cur[j]) + 1
        cur[j + 1] = side
        best = max(best, side)
    prev = cur
  return best * best


@register_algorithm(category="dynamic_programming", summary="Maximal rectangle of ones in binary matrix")
def maximal_rectangle(matrix: List[List[str]]) -> int:
  if not matrix or not matrix[0]:
    return 0
  cols = len(matrix[0])
  heights = [0] * cols
  best = 0
  for row in matrix:
    for j in range(cols):
      heights[j] = heights[j] + 1 if row[j] == "1" else 0
    stack: List[int] = []
    for j in range(cols + 1):
      h = heights[j] if j < cols else 0
      while stack and h < heights[stack[-1]]:
        height = heights[stack.pop()]
        width = j if not stack else j - stack[-1] - 1
        best = max(best, height * width)
      stack.append(j)
  return best


@register_algorithm(category="dynamic_programming", summary="Partition into two equal-sum subsets")
def partition_equal_subset(nums: List[int]) -> bool:
  total = sum(nums)
  if total % 2:
    return False
  target = total // 2
  dp = [False] * (target + 1)
  dp[0] = True
  for x in nums:
    for t in range(target, x - 1, -1):
      dp[t] = dp[t] or dp[t - x]
  return dp[target]


@register_algorithm(category="dynamic_programming", summary="Count ways to reach target with +/- signs")
def target_sum(nums: List[int], target: int) -> int:
  total = sum(nums)
  if abs(target) > total or (total + target) % 2:
    return 0
  subset_sum = (total + target) // 2
  dp = [0] * (subset_sum + 1)
  dp[0] = 1
  for x in nums:
    for s in range(subset_sum, x - 1, -1):
      dp[s] += dp[s - x]
  return dp[subset_sum]


@register_algorithm(category="dynamic_programming", summary="Coin change II combination count")
def coin_change2(amount: int, coins: List[int]) -> int:
  dp = [0] * (amount + 1)
  dp[0] = 1
  for coin in coins:
    for a in range(coin, amount + 1):
      dp[a] += dp[a - coin]
  return dp[amount]


@register_algorithm(category="dynamic_programming", summary="Minimum perfect squares summing to n")
def perfect_squares(n: int) -> int:
  dp = [0] * (n + 1)
  for i in range(1, n + 1):
    best = i
    k = 1
    while k * k <= i:
      best = min(best, dp[i - k * k] + 1)
      k += 1
    dp[i] = best
  return dp[n]


@register_algorithm(category="dynamic_programming", summary="Integer break maximum product")
def integer_break(n: int) -> int:
  if n <= 3:
    return n - 1
  dp = [0] * (n + 1)
  for i in range(2, n + 1):
    for j in range(1, i):
      dp[i] = max(dp[i], max(j, dp[j]) * max(i - j, dp[i - j]))
  return dp[n]


@register_algorithm(category="dynamic_programming", summary="Last stone weight II after optimal smashes")
def last_stone_weight_ii(stones: List[int]) -> int:
  total = sum(stones)
  target = total // 2
  dp = [False] * (target + 1)
  dp[0] = True
  for stone in stones:
    for t in range(target, stone - 1, -1):
      dp[t] = dp[t] or dp[t - stone]
  for t in range(target, -1, -1):
    if dp[t]:
      return total - 2 * t
  return 0


@register_algorithm(category="dynamic_programming", summary="Max strings with m zeros and n ones")
def ones_and_zeroes(strs: List[str], m: int, n: int) -> int:
  dp = [[0] * (n + 1) for _ in range(m + 1)]
  for s in strs:
    zeros = s.count("0")
    ones = s.count("1")
    for i in range(m, zeros - 1, -1):
      for j in range(n, ones - 1, -1):
        dp[i][j] = max(dp[i][j], dp[i - zeros][j - ones] + 1)
  return dp[m][n]


@register_algorithm(category="dynamic_programming", summary="Profitable schemes count modulo 10^9+7")
def profitable_schemes(
  n: int,
  min_profit: int,
  group: List[int],
  profit: List[int],
) -> int:
  mod = 10**9 + 7
  cap = n
  dp = [[0] * (min_profit + 1) for _ in range(cap + 1)]
  dp[0][0] = 1
  for g, p in zip(group, profit):
    for members in range(cap, g - 1, -1):
      for prof in range(min_profit, -1, -1):
        nprof = min(min_profit, prof + p)
        dp[members][nprof] = (dp[members][nprof] + dp[members - g][prof]) % mod
  return sum(dp[members][min_profit] for members in range(cap + 1)) % mod


@register_algorithm(category="dynamic_programming", summary="Cherry pickup maximum in grid")
def cherry_pickup(grid: List[List[int]]) -> int:
  n = len(grid)
  if n == 0:
    return 0
  neg = -10**9
  dp = [[[neg] * n for _ in range(n)] for _ in range(n)]
  dp[0][0][0] = grid[0][0]
  for steps in range(1, 2 * n - 1):
    ndp = [[[neg] * n for _ in range(n)] for _ in range(n)]
    for r1 in range(n):
      for c1 in range(n):
        for r2 in range(n):
          c2 = steps - r1 - r2
          if c2 < 0 or c2 >= n or dp[r1][c1][r2] == neg:
            continue
          cherries = grid[r1][c1]
          if (r1, c1) != (r2, c2):
            cherries += grid[r2][c2]
          for dr1, dr2 in ((0, 0), (0, 1), (1, 0), (1, 1)):
            pr1, pc1 = r1 - dr1, c1 - (1 - dr1)
            pr2, pc2 = r2 - dr2, c2 - (1 - dr2)
            if pr1 >= 0 and pc1 >= 0 and pr2 >= 0 and pc2 >= 0:
              ndp[r1][c1][r2] = max(ndp[r1][c1][r2], dp[pr1][pc1][pr2] + cherries)
    dp = ndp
  return max(0, dp[n - 1][n - 1][n - 1])


@register_algorithm(category="dynamic_programming", summary="Minimum cost to reach top of stairs")
def min_cost_climbing_stairs(cost: List[int]) -> int:
  n = len(cost)
  if n == 0:
    return 0
  prev2 = prev1 = 0
  for i in range(n):
    cur = min(prev1 + cost[i], prev2 + cost[i])
    prev2, prev1 = prev1, cur
  return min(prev1, prev2)


@register_algorithm(category="dynamic_programming", summary="Paint house minimum cost with 3 colors")
def paint_house(costs: List[List[int]]) -> int:
  if not costs:
    return 0
  prev = costs[0][:]
  for i in range(1, len(costs)):
    cur = costs[i][:]
    for c in range(3):
      cur[c] += min(prev[j] for j in range(3) if j != c)
    prev = cur
  return min(prev)


@register_algorithm(category="dynamic_programming", summary="Maximum profit job scheduling")
def max_profit_job_scheduling(
  start: List[int],
  end: List[int],
  profit: List[int],
) -> int:
  jobs = sorted(zip(end, start, profit))
  ends = [j[0] for j in jobs]
  dp = [0] * (len(jobs) + 1)
  for i in range(1, len(jobs) + 1):
    e, s, p = jobs[i - 1]
    lo, hi = 0, i - 1
    j = 0
    while lo <= hi:
      mid = (lo + hi) // 2
      if ends[mid] <= s:
        j = mid + 1
        lo = mid + 1
      else:
        hi = mid - 1
    dp[i] = max(dp[i - 1], dp[j] + p)
  return dp[len(jobs)]


@register_algorithm(category="dynamic_programming", summary="Egg drop minimum trials")
def egg_drop(eggs: int, floors: int) -> int:
  dp = [[0] * (floors + 1) for _ in range(eggs + 1)]
  for f in range(1, floors + 1):
    dp[1][f] = f
  for k in range(2, eggs + 1):
    for f in range(1, floors + 1):
      lo, hi, best = 1, f, f
      while lo <= hi:
        mid = (lo + hi) // 2
        broken = dp[k - 1][mid - 1]
        intact = dp[k][f - mid]
        if broken > intact:
          hi = mid - 1
          best = mid
        else:
          lo = mid + 1
          best = mid
      dp[k][f] = 1 + best
  return dp[eggs][floors]


@register_algorithm(category="dynamic_programming", summary="Catalan number C_n")
def catalan_number(n: int) -> int:
  if n < 0:
    return 0
  dp = [0] * (n + 1)
  dp[0] = 1
  for i in range(1, n + 1):
    total = 0
    for j in range(i):
      total += dp[j] * dp[i - 1 - j]
    dp[i] = total
  return dp[n]


@register_algorithm(category="dynamic_programming", summary="Bell number B_n")
def bell_number(n: int) -> int:
  if n < 0:
    return 0
  bell = [[0] * (n + 1) for _ in range(n + 1)]
  bell[0][0] = 1
  for i in range(1, n + 1):
    bell[i][0] = bell[i - 1][i - 1]
    for j in range(1, i + 1):
      bell[i][j] = bell[i - 1][j - 1] + bell[i][j - 1]
  return bell[n][0]

