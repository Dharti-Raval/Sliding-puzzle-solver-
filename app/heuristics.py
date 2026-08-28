"""Heuristic functions used by the solvers."""


def manhattan_distance(board, size):
    """
    Sum of Manhattan distances of every tile (except the blank) from its
    goal position. This heuristic is admissible and consistent, which is
    required for A*/IDA* to guarantee an optimal (minimum-move) solution.
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
