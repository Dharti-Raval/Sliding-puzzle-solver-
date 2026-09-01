// ---- State ----
let size = 3;
let board = [];          // current board shown in the grid
let solutionStates = []; // list of board states returned by the solver
let animTimer = null;
let animStep = 0;

// ---- Elements ----
const sizeSelect = document.getElementById("sizeSelect");
const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const detailsEl = document.getElementById("details");
const movesListEl = document.getElementById("movesList");
const animControls = document.getElementById("animControls");
const stepLabel = document.getElementById("stepLabel");

// ---- Helpers ----
function goalBoard(n) {
  const g = [];
  for (let i = 1; i < n * n; i++) g.push(i);
  g.push(0);
  return g;
}

function renderBoard(values) {
  board = values.slice();
  boardEl.style.gridTemplateColumns = `repeat(${size}, 64px)`;
  boardEl.innerHTML = "";
  values.forEach((val, idx) => {
    const cell = document.createElement("input");
    cell.className = "cell" + (val === 0 ? " blank" : "");
    cell.value = val === 0 ? "" : val;
    cell.maxLength = 2;
    cell.dataset.idx = idx;
    cell.addEventListener("change", onCellEdit);
    boardEl.appendChild(cell);
  });
}

function onCellEdit(e) {
  const idx = parseInt(e.target.dataset.idx, 10);
  let val = e.target.value.trim();
  val = val === "" ? 0 : parseInt(val, 10);
  if (isNaN(val) || val < 0 || val >= size * size) {
    e.target.value = board[idx] === 0 ? "" : board[idx];
    return;
  }
  board[idx] = val;
  // only update the CSS class of this cell
  e.target.className = "cell" + (val === 0 ? " blank" : "");
  e.target.value = val === 0 ? "" : val;
}

function readBoardFromInputs() {
  return board.slice();
}

function setStatus(text, cls) {
  statusEl.textContent = text;
  statusEl.className = "status" + (cls ? " " + cls : "");
}

async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

// ---- Actions ----
async function loadRandom() {
  clearAnimation();
  setStatus("Generating random solvable puzzle...");
  try {
    const data = await postJSON("/api/random", { size });
    renderBoard(data.board);
    setStatus("Random puzzle loaded. Click Solve.");
  } catch (err) {
    setStatus("Error: " + err.message, "unsolvable");
  }
}

function resetToGoal() {
  clearAnimation();
  renderBoard(goalBoard(size));
  setStatus("Reset to goal state.");
  detailsEl.innerHTML = "";
  movesListEl.textContent = "No solution yet.";
}

async function solvePuzzle() {
  clearAnimation();
  const currentBoard = readBoardFromInputs();
  setStatus("Solving...");
  detailsEl.innerHTML = "";
  movesListEl.textContent = "";

  try {
    const data = await postJSON("/api/solve", { board: currentBoard, size });

    if (!data.solvable) {
      setStatus("❌ Unsolvable puzzle", "unsolvable");
      detailsEl.innerHTML = `<div><b>Algorithm:</b> ${data.algorithm}</div>`;
      movesListEl.textContent = "No solution exists for this configuration.";
      animControls.style.display = "none";
      return;
    }

    setStatus("✅ Solvable — optimal solution found", "solvable");
    detailsEl.innerHTML = `
      <div><b>Algorithm:</b> ${data.algorithm}</div>
      <div><b>Minimum moves:</b> ${data.move_count}</div>
      <div><b>Time taken:</b> ${data.time_seconds}s</div>
    `;

    if (data.move_count === 0) {
      movesListEl.textContent = "Already solved!";
    } else {
      movesListEl.innerHTML = data.moves
        .map((m, i) => `<span>${i + 1}. tile ${m}</span>`)
        .join("");
    }

    solutionStates = data.states;
    animStep = 0;
    animControls.style.display = data.move_count > 0 ? "flex" : "none";
    stepLabel.textContent = `Step 0 / ${data.move_count}`;
    renderBoard(solutionStates[0]);
  } catch (err) {
    setStatus("Error: " + err.message, "unsolvable");
  }
}

function clearAnimation() {
  if (animTimer) {
    clearInterval(animTimer);
    animTimer = null;
  }
}

function playAnimation() {
  if (!solutionStates.length) return;
  clearAnimation();
  animStep = 0;
  renderBoard(solutionStates[0]);
  stepLabel.textContent = `Step 0 / ${solutionStates.length - 1}`;

  animTimer = setInterval(() => {
    animStep++;
    if (animStep >= solutionStates.length) {
      clearAnimation();
      return;
    }
    renderBoard(solutionStates[animStep]);
    stepLabel.textContent = `Step ${animStep} / ${solutionStates.length - 1}`;
  }, 500);
}

// ---- Events ----
sizeSelect.addEventListener("change", () => {
  size = parseInt(sizeSelect.value, 10);
  resetToGoal();
});
document.getElementById("randomBtn").addEventListener("click", loadRandom);
document.getElementById("resetBtn").addEventListener("click", resetToGoal);
document.getElementById("solveBtn").addEventListener("click", solvePuzzle);
document.getElementById("playBtn").addEventListener("click", playAnimation);

// ---- Init ----
resetToGoal();
