# Design

The app is a thin wrapper around a compiled Modelica simulation. Building the model and running it are two separate stages.

## Step 1 — Build the model (once, in OMEdit)

- `NonInteractingTanks/*.mo` → **OMCompiler backend**: DAE reduction, then C-code generation
- C code → **GCC/Clang** → `bin/TwoConnectedTanks`, a standalone executable
- The app never compiles anything. It only launches this binary.

## Step 2 — Run the app (`python main.py`)

1. Window opens, fields prefilled — `main_window.py`
2. User enters start/stop time, clicks **Execute**
3. Bounds checked: `0 <= start < stop < 5` — `validator.py`
4. `QProcess.start(binary, args)` spawns the binary as a **child process** — `models.py`
5. Child process solves the ODE system with DASSL, writes `TwoConnectedTanks_res.mat`, exits 0
6. **Signal `readyReadStandardOutput`** — fires repeatedly while solving → log panel fills live
7. **Signal `finished(exitCode)`** — fires once on exit → `read_mat()` decodes the `.mat`
8. `tank1.h` / `tank2.h` drawn on the embedded canvas — `_plot_results()`

Steps 6 and 7 are **callbacks, not return values**. The GUI never blocks waiting on the solver.

## Three things carry the weight

- **`QProcess`, not `subprocess`** — the solver runs asynchronously, so the window stays responsive and the log fills line by line instead of dumping at the end.
- **`matreader.py`** — OpenModelica's `.mat` stores names as a *transposed* character matrix and splits values across two data blocks, with `dataInfo` mapping each name onto a row and a sign. Read naively, the variable names come out as garbage.
- **Qt signals** — the process runner emits `output_received` / `finished` and knows nothing about the GUI, so either side can change alone.
