"""Queue and stack algorithms (stdlib only)."""

from __future__ import annotations

from collections import deque
from typing import Deque, List, Optional, Tuple

from .catalog import register_algorithm


@register_algorithm(category="queues_stacks", summary="Stack operations: push then pop sequence.")
def stack_operations(ops: List[Tuple[str, int]]) -> List[int]:
    stack: List[int] = []
    popped: List[int] = []
    for op, val in ops:
        if op == "push":
            stack.append(val)
        elif op == "pop":
            if not stack:
                raise ValueError("pop from empty stack")
            popped.append(stack.pop())
        else:
            raise ValueError(f"unknown op: {op}")
    return popped


@register_algorithm(category="queues_stacks", summary="Queue operations: enqueue then dequeue sequence.")
def queue_operations(ops: List[Tuple[str, int]]) -> List[int]:
    q: Deque[int] = deque()
    dequeued: List[int] = []
    for op, val in ops:
        if op == "enqueue":
            q.append(val)
        elif op == "dequeue":
            if not q:
                raise ValueError("dequeue from empty queue")
            dequeued.append(q.popleft())
        else:
            raise ValueError(f"unknown op: {op}")
    return dequeued


@register_algorithm(category="queues_stacks", summary="Whether parentheses/brackets string is valid.")
def valid_parentheses(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: List[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack


@register_algorithm(category="queues_stacks", summary="Evaluate reverse Polish notation expression tokens.")
def evaluate_rpn(tokens: List[str]) -> float:
    stack: List[float] = []
    ops = {"+", "-", "*", "/"}
    for tok in tokens:
        if tok in ops:
            b = stack.pop()
            a = stack.pop()
            if tok == "+":
                stack.append(a + b)
            elif tok == "-":
                stack.append(a - b)
            elif tok == "*":
                stack.append(a * b)
            else:
                stack.append(a / b)
        else:
            stack.append(float(tok))
    return stack[0]


@register_algorithm(category="queues_stacks", summary="Minimum values after each push/pop operation sequence.")
def min_stack_simulation(ops: List[Tuple[str, int]]) -> List[Optional[int]]:
    stack: List[int] = []
    mins: List[int] = []
    out: List[Optional[int]] = []
    for op, val in ops:
        if op == "push":
            stack.append(val)
            mins.append(val if not mins else min(val, mins[-1]))
            out.append(mins[-1])
        elif op == "pop":
            if not stack:
                out.append(None)
            else:
                stack.pop()
                mins.pop()
                out.append(mins[-1] if mins else None)
        elif op == "get_min":
            out.append(mins[-1] if mins else None)
    return out


@register_algorithm(category="queues_stacks", summary="Next greater element for each item in nums.")
def next_greater_element(nums: List[int]) -> List[int]:
    out = [-1] * len(nums)
    stack: List[int] = []
    for i, val in enumerate(nums):
        while stack and nums[stack[-1]] < val:
            out[stack.pop()] = val
        stack.append(i)
    return out


@register_algorithm(category="queues_stacks", summary="Days until warmer temperature for each day.")
def daily_temperatures(temps: List[int]) -> List[int]:
    out = [0] * len(temps)
    stack: List[int] = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            prev = stack.pop()
            out[prev] = i - prev
        stack.append(i)
    return out


@register_algorithm(category="queues_stacks", summary="Largest rectangle area in histogram.")
def largest_rectangle_histogram(heights: List[int]) -> int:
    stack: List[int] = []
    best = 0
    heights = heights + [0]
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            best = max(best, height * width)
        stack.append(i)
    return best


@register_algorithm(category="queues_stacks", summary="Maximum in each sliding window using monotonic deque.")
def sliding_window_max_deque(nums: List[int], k: int) -> List[int]:
    if k <= 0 or not nums:
        return []
    dq: Deque[int] = deque()
    out: List[int] = []
    for i, val in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= val:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


@register_algorithm(category="queues_stacks", summary="Queue using two stacks: process enqueue/dequeue ops.")
def queue_using_two_stacks(ops: List[str]) -> List[int]:
    in_stack: List[int] = []
    out_stack: List[int] = []
    result: List[int] = []

    def shift() -> None:
        if not out_stack:
            while in_stack:
                out_stack.append(in_stack.pop())

    for op in ops:
        if op.startswith("enqueue"):
            _, val = op.split()
            in_stack.append(int(val))
        elif op == "dequeue":
            shift()
            if not out_stack:
                raise ValueError("dequeue from empty queue")
            result.append(out_stack.pop())
    return result


@register_algorithm(category="queues_stacks", summary="Stack using two queues: process push/pop ops.")
def stack_using_two_queues(ops: List[str]) -> List[int]:
    q1: Deque[int] = deque()
    q2: Deque[int] = deque()
    result: List[int] = []

    for op in ops:
        if op.startswith("push"):
            _, val = op.split()
            q2.append(int(val))
            while q1:
                q2.append(q1.popleft())
            q1, q2 = q2, q1
        elif op == "pop":
            if not q1:
                raise ValueError("pop from empty stack")
            result.append(q1.popleft())
    return result


@register_algorithm(category="queues_stacks", summary="Decode k[encoded_string] nested repetition.")
def decode_string(s: str) -> str:
    stack: List[Tuple[str, int]] = []
    cur_str = ""
    cur_num = 0
    for ch in s:
        if ch.isdigit():
            cur_num = cur_num * 10 + int(ch)
        elif ch == "[":
            stack.append((cur_str, cur_num))
            cur_str = ""
            cur_num = 0
        elif ch == "]":
            prev_str, num = stack.pop()
            cur_str = prev_str + cur_str * num
        else:
            cur_str += ch
    return cur_str


@register_algorithm(category="queues_stacks", summary="Simplify Unix-style absolute path.")
def simplify_path(path: str) -> str:
    stack: List[str] = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)


@register_algorithm(category="queues_stacks", summary="Simulate asteroid collisions; return surviving sizes.")
def asteroid_collision(asteroids: List[int]) -> List[int]:
    stack: List[int] = []
    for ast in asteroids:
        while stack and stack[-1] > 0 and ast < 0:
            if stack[-1] < -ast:
                stack.pop()
                continue
            if stack[-1] == -ast:
                stack.pop()
            ast = 0
            break
        if ast != 0:
            stack.append(ast)
    return stack


@register_algorithm(category="queues_stacks", summary="Remove all adjacent duplicate characters from string.")
def remove_adjacent_duplicates(s: str) -> str:
    stack: List[str] = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)
