# OpenModelica Simulation Manager

A desktop app that runs a compiled OpenModelica model, streams its output live, and plots the results.

[View a screenshot of the running app →](docs/simulation-window.png)

---

## What it does

Runs a pre-compiled OpenModelica binary as a child process, streams its log live, then decodes the binary `.mat` result and plots the two tank levels.

- **[Design](docs/design.md)** — build pipeline, runtime steps, why `QProcess` and Qt signals
- **[The model](docs/equation.md)** — the ODEs, parameters, and resulting behaviour

---

## Tech stack

| Component | Role |
|---|---|
| **OpenModelica** | compiles the Modelica model; DASSL solver produces the `.mat` result |
| **PyQt6** | GUI, plus `QProcess` to run the solver without freezing the window |
| **Matplotlib** | plot embedded directly in the Qt widget tree |
| **SciPy / NumPy** | decode the binary `.mat` result file |

---

## Setup

**Prerequisites**

- Python 3.12+
- Linux x86-64 — the bundled `bin/TwoConnectedTanks` is a Linux binary
- OpenModelica — only if you want to rebuild the model from `NonInteractingTanks/`

```bash
git clone https://github.com/Vidit-lab/OpenModelicaApp.git
cd OpenModelicaApp

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python main.py
```

Set a start and stop time, hit **Execute Simulation**. The log fills as the solver runs and both tank levels are plotted when it finishes.

---

## Project structure

| File | Responsibility |
|---|---|
| `main.py` | entry point |
| `src/main_window.py` | GUI layout, plot rendering |
| `src/models.py` | launches the solver via `QProcess`, streams stdout/stderr |
| `src/validator.py` | input bounds checking |
| `src/matreader.py` | decodes the OpenModelica `.mat` result into named arrays |
| `NonInteractingTanks/` | the Modelica source model |
| `bin/` | compiled model and simulation output |

`src/matreader.py` and `src/validator.py` each carry a self-check — run either directly to verify it.

---

## Limitations

- **Stop time is capped below 5 s**, so the GUI can only ever show the pre-valve ramp. Every interesting dynamic happens after `t = 5`.
- **Tank 2 never overflows** — it has no outlet, so its level grows without bound.
- The compiled binary is platform-specific; there is no build step in the repo.

## Future improvements

- Raise the stop-time cap and let the valve event appear in the app
- Variable picker, so any signal in the result file can be plotted
- Export plot and result data
- Build the Modelica model from source instead of shipping a binary

---

## License

[MIT](LICENSE)
