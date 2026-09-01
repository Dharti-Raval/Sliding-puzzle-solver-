"""Flask web app for the Optimal Sliding Puzzle Solver."""

import time

from flask import Flask, jsonify, render_template, request

from app.puzzle import get_neighbors, goal_state, is_valid_board, random_solvable_board
from app.solvability import is_solvable
from app.solver import solve

app = Flask(__name__)


def moves_to_states(board, moves):
    """Replay the move list on `board` and return every intermediate state."""
    size = int(len(board) ** 0.5)
    states = [list(board)]
    current = board
    for move_tile in moves:
        for neighbor, moved_tile in get_neighbors(current, size):
            if moved_tile == move_tile:
                current = neighbor
                break
        states.append(list(current))
    return states


def parse_request_board():
    data = request.get_json(force=True)
    size = int(data.get("size", 0))
    board = data.get("board")

    if size not in (3, 4):
        raise ValueError("size must be 3 or 4")
    if not isinstance(board, list) or not all(isinstance(x, int) for x in board):
        raise ValueError("board must be a list of integers")
    if not is_valid_board(tuple(board), size):
        raise ValueError(
            f"board must contain each number from 0 to {size * size - 1} exactly once"
        )
    return tuple(board), size


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/random", methods=["POST"])
def api_random():
    data = request.get_json(force=True)
    size = int(data.get("size", 3))
    if size not in (3, 4):
        return jsonify({"error": "size must be 3 or 4"}), 400
    board = random_solvable_board(size)
    return jsonify({"board": list(board)})


@app.route("/api/solve", methods=["POST"])
def api_solve():
    try:
        board, size = parse_request_board()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    solvable = is_solvable(board, size)
    if not solvable:
        return jsonify({
            "solvable": False,
            "algorithm": "A* Search" if size == 3 else "IDA* Search",
            "moves": [],
            "move_count": 0,
            "states": [list(board)],
            "time_seconds": 0.0,
        })

    start = time.time()
    moves, algorithm = solve(board, size)
    elapsed = time.time() - start

    if moves is None:
        return jsonify({
            "error": "This 4×4 position is too hard for the current time limit (~25 s). "
                     "Try the Random Puzzle button or a board that needs fewer moves.",
            "solvable": True,
            "algorithm": algorithm,
            "time_seconds": round(elapsed, 4),
        }), 408   # or 500 – 408 Request Timeout is semantically nicer

    states = moves_to_states(board, moves)

    return jsonify({
        "solvable": True,
        "algorithm": algorithm,
        "moves": moves,
        "move_count": len(moves),
        "states": states,
        "time_seconds": round(elapsed, 4),
    })


@app.route("/api/goal", methods=["POST"])
def api_goal():
    data = request.get_json(force=True)
    size = int(data.get("size", 3))
    if size not in (3, 4):
        return jsonify({"error": "size must be 3 or 4"}), 400
    return jsonify({"board": list(goal_state(size))})


if __name__ == "__main__":
    app.run(debug=True)
