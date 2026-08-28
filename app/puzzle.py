"""
Core puzzle representation for the N-Puzzle (8-puzzle / 15-puzzle).

A board is represented as a flat tuple of ints of length size*size.
0 represents the empty/blank tile.
"""

import random


def goal_state(size):
    """Return the goal board for a given size (3 -> 8-puzzle, 4 -> 15-puzzle)."""
    return tuple(list(range(1, size * size)) + [0])


def get_neighbors(board, size):
    """
    Return a list of (new_board, moved_tile) pairs reachable from `board`
    by sliding one tile into the blank space.
    `moved_tile` is the value of the tile that moved (useful for display).
    """
    idx = board.index(0)
    row, col = divmod(idx, size)
    neighbors = []

    candidates = []
    if row > 0:
        candidates.append(idx - size)   # blank moves up -> tile above moves down
    if row < size - 1:
        candidates.append(idx + size)   # blank moves down
    if col > 0:
        candidates.append(idx - 1)      # blank moves left
    if col < size - 1:
        candidates.append(idx + 1)      # blank moves right

    for new_idx in candidates:
        new_board = list(board)
        moved_tile = new_board[new_idx]
        new_board[idx], new_board[new_idx] = new_board[new_idx], new_board[idx]
        neighbors.append((tuple(new_board), moved_tile))

    return neighbors


def is_valid_board(board, size):
    """Check that board is a permutation of 0..size*size-1 of the right length."""
    if len(board) != size * size:
        return False
    return sorted(board) == list(range(size * size))


def random_solvable_board(size, shuffle_moves=None):
    """
    Generate a random board by starting at the goal state and applying a
    sequence of random legal moves. This guarantees solvability by
    construction and keeps the scramble at a solvable difficulty.
    """
    if shuffle_moves is None:
        shuffle_moves = 60 if size == 3 else 30

    board = goal_state(size)
    last_idx = None
    for _ in range(shuffle_moves):
        idx = board.index(0)
        neighbors = get_neighbors(board, size)
        # avoid immediately undoing the previous move for a better shuffle
        options = [n for n in neighbors if n[0].index(0) != last_idx] or neighbors
        board, _ = random.choice(options)
        last_idx = idx
    return board
