"""Heuristic functions used by the solvers."""

def manhattan_distance(board, size):
    """
    Sum of Manhattan distances of every tile (except the blank) from its
    goal position. Admissible and consistent.
    """
    total = 0
    for idx, value in enumerate(board):
        if value == 0:
            continue
        goal_idx = value - 1  # tile `value` belongs at index (value - 1)
        cur_row, cur_col = divmod(idx, size)
        goal_row, goal_col = divmod(goal_idx, size)
        total += abs(cur_row - goal_row) + abs(cur_col - goal_col)
    return total


def linear_conflict(board, size):
    """
    Extra cost for tiles that are in the correct row or column
    but in the wrong order. Each conflict pair adds +2.
    Still admissible when added to Manhattan.
    """
    conflicts = 0

    # ----- Row conflicts -----
    for row in range(size):
        max_val = -1
        for col in range(size):
            val = board[row * size + col]
            if val == 0:
                continue
            goal_row = (val - 1) // size
            if goal_row == row:               # tile belongs in this row
                if val > max_val:
                    max_val = val
                else:
                    conflicts += 2

    # ----- Column conflicts -----
    for col in range(size):
        max_val = -1
        for row in range(size):
            val = board[row * size + col]
            if val == 0:
                continue
            goal_col = (val - 1) % size
            if goal_col == col:               # tile belongs in this column
                if val > max_val:
                    max_val = val
                else:
                    conflicts += 2

    return conflicts


def heuristic(board, size):
    """
    Manhattan Distance + Linear Conflict.
    Still admissible → A* / IDA* remain optimal, but much faster on 15-puzzle.
    """
    return manhattan_distance(board, size) + linear_conflict(board, size)
