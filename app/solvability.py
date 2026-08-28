"""
Solvability check for the N-puzzle using the classic inversion-count rule.

Rules:
- Odd grid width (e.g. 3x3): solvable iff the number of inversions is even.
- Even grid width (e.g. 4x4): solvable iff
    (inversions + row_of_blank_counted_from_bottom) is odd.
"""


def count_inversions(tiles):
    """tiles: list of tile values with the blank (0) removed."""
    inversions = 0
    n = len(tiles)
    for i in range(n):
        for j in range(i + 1, n):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions


def is_solvable(board, size):
    tiles = [t for t in board if t != 0]
    inversions = count_inversions(tiles)

    if size % 2 == 1:
        # Odd grid: blank's row doesn't matter.
        return inversions % 2 == 0

    # Even grid: need the blank's row counted from the bottom (1-indexed).
    blank_idx = board.index(0)
    blank_row_from_top = blank_idx // size
    blank_row_from_bottom = size - blank_row_from_top

    if blank_row_from_bottom % 2 == 0:
        return inversions % 2 == 1
    else:
        return inversions % 2 == 0
