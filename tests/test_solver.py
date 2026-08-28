import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.heuristics import manhattan_distance
from app.puzzle import get_neighbors, goal_state, is_valid_board, random_solvable_board
from app.solvability import is_solvable
from app.solver import solve, solve_astar, solve_idastar


def apply_moves(board, moves, size):
    current = board
    for move_tile in moves:
        for neighbor, moved_tile in get_neighbors(current, size):
            if moved_tile == move_tile:
                current = neighbor
                break
    return current


def test_goal_state_is_solved():
    assert manhattan_distance(goal_state(3), 3) == 0
    assert manhattan_distance(goal_state(4), 4) == 0


def test_is_valid_board():
    assert is_valid_board((1, 2, 3, 4, 5, 6, 7, 8, 0), 3)
    assert not is_valid_board((1, 2, 3, 4, 5, 6, 7, 8, 8), 3)
    assert not is_valid_board((1, 2, 3), 3)


def test_solvability_known_cases():
    # Classic unsolvable 8-puzzle (odd single swap of 1,2 from goal)
    unsolvable = (2, 1, 3, 4, 5, 6, 7, 8, 0)
    assert is_solvable(unsolvable, 3) is False

    solvable = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    assert is_solvable(solvable, 3) is True

    assert is_solvable(goal_state(4), 4) is True


def test_astar_solves_8puzzle_optimally():
    # One move away from goal: swap 8 and 0
    board = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    moves = solve_astar(board, 3)
    assert moves is not None
    assert len(moves) == 1

    result = apply_moves(board, moves, 3)
    assert result == goal_state(3)


def test_astar_matches_known_optimal_length():
    # A well-known 8-puzzle instance with optimal solution length 31.
    board = (8, 6, 7, 2, 5, 4, 3, 0, 1)
    moves = solve_astar(board, 3)
    assert moves is not None
    assert apply_moves(board, moves, 3) == goal_state(3)
    assert len(moves) == 31


def test_idastar_solves_15puzzle():
    board = list(goal_state(4))
    # swap last two tiles (14 <-> 0) -> 1 move from goal
    board[-1], board[-2] = board[-2], board[-1]
    board = tuple(board)
    moves = solve_idastar(board, 4)
    assert moves is not None
    assert len(moves) == 1
    assert apply_moves(board, moves, 4) == goal_state(4)


def test_solve_dispatches_correct_algorithm():
    moves3, algo3 = solve(goal_state(3), 3)
    assert algo3 == "A* Search"
    assert moves3 == []

    moves4, algo4 = solve(goal_state(4), 4)
    assert algo4 == "IDA* Search"
    assert moves4 == []


def test_random_solvable_board_is_always_solvable():
    for size in (3, 4):
        for _ in range(5):
            board = random_solvable_board(size, shuffle_moves=20)
            assert is_valid_board(board, size)
            assert is_solvable(board, size)
