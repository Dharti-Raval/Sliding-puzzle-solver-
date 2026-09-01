"""
Optimal solvers for the N-puzzle.

- solve_astar: A* search, used for the 3x3 (8-puzzle).
- solve_idastar: Iterative Deepening A*, used for the 4x4 (15-puzzle) because
  it needs only O(depth) memory instead of A*'s O(states) memory.

Both use f(n) = g(n) + h(n) with the Manhattan + Linear Conflict heuristic,
which is admissible and consistent, so both return a minimum-length (optimal) solution.
"""

import heapq
import sys
import time

from app.heuristics import heuristic
from app.puzzle import get_neighbors, goal_state

sys.setrecursionlimit(2000)

FOUND = "FOUND"
IDA_TIMEOUT_SECONDS = 25          # soft timeout to avoid Render killing the request


def solve_astar(board, size):
    """Return the optimal list of moved-tile values, or None if unsolvable."""
    goal = goal_state(size)
    if board == goal:
        return []

    g_score = {board: 0}
    counter = 0  # tie-breaker so heapq never compares boards directly
    open_heap = [(heuristic(board, size), counter, board, [])]
    closed = set()

    while open_heap:
        _, _, current, path = heapq.heappop(open_heap)

        if current == goal:
            return path
        if current in closed:
            continue
        closed.add(current)

        for neighbor, move in get_neighbors(current, size):
            tentative_g = g_score[current] + 1
            if neighbor in g_score and tentative_g >= g_score[neighbor]:
                continue
            g_score[neighbor] = tentative_g
            counter += 1
            f = tentative_g + heuristic(neighbor, size)
            heapq.heappush(open_heap, (f, counter, neighbor, path + [move]))

    return None


def solve_idastar(board, size):
    """Return the optimal list of moved-tile values, or None if unsolvable / timed out."""
    goal = goal_state(size)
    if board == goal:
        return []

    bound = heuristic(board, size)
    path_boards = [board]
    path_moves = []
    deadline = time.time() + IDA_TIMEOUT_SECONDS

    while True:
        if time.time() > deadline:
            return None

        result = _ida_search(path_boards, path_moves, 0, bound, size, goal, deadline)
        if result == FOUND:
            return list(path_moves)
        if result == float("inf"):
            return None
        bound = result


def _ida_search(path_boards, path_moves, g, bound, size, goal, deadline):
    if time.time() > deadline:
        return float("inf")

    current = path_boards[-1]
    f = g + heuristic(current, size)
    if f > bound:
        return f
    if current == goal:
        return FOUND

    min_exceeded = float("inf")
    prev_board = path_boards[-2] if len(path_boards) > 1 else None

    for neighbor, move in get_neighbors(current, size):
        if neighbor == prev_board:
            continue  # don't immediately undo the last move
        path_boards.append(neighbor)
        path_moves.append(move)

        result = _ida_search(path_boards, path_moves, g + 1, bound, size, goal, deadline)
        if result == FOUND:
            return FOUND
        if result < min_exceeded:
            min_exceeded = result

        path_boards.pop()
        path_moves.pop()

    return min_exceeded


def solve(board, size):
    """Pick the right optimal algorithm for the given puzzle size."""
    if size == 3:
        return solve_astar(board, size), "A* Search"
    return solve_idastar(board, size), "IDA* Search"
