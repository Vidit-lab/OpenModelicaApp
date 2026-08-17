"""GUI View Layer using PyQt6 with Matplotlib Visualization."""

from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from src.matreader import read_mat
from src.models import SimulationRunner
from src.validator import ValidationError, validate_times


class MainWindow(QMainWindow):
    """Main Application Window."""

    #: Result variables drawn after a run, in legend order.
    PLOT_VARIABLES = ("tank1.h", "tank2.h")

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OpenModelica Simulation Manager")
        self.resize(800, 750)

        # Base directories relative to OpenModelicaApp/
        self.project_root = Path(__file__).resolve().parent.parent
        self.bin_dir = self.project_root / "bin"

        self._runner = SimulationRunner()
        self._runner.output_received.connect(self._append_log)
        self._runner.error_received.connect(self._append_log)
        self._runner.finished.connect(self._on_simulation_finished)

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        form_layout = QFormLayout()

        # Input 1: Application selector
        self.exe_path_input = QLineEdit()
        default_binary = str(self.bin_dir / "TwoConnectedTanks")
        self.exe_path_input.setText(default_binary)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_executable)

        exe_layout = QHBoxLayout()
        exe_layout.addWidget(self.exe_path_input)
        exe_layout.addWidget(browse_btn)

        # Input 2: Start Time
        self.start_time_input = QLineEdit()
        self.start_time_input.setText("0")

        # Input 3: Stop Time
        self.stop_time_input = QLineEdit()
        self.stop_time_input.setText("4")

        form_layout.addRow("Application to launch:", exe_layout)
        form_layout.addRow("Start Time (Integer):", self.start_time_input)
        form_layout.addRow("Stop Time (Integer):", self.stop_time_input)

        layout.addLayout(form_layout)

        # Action Button
        self.run_button = QPushButton("Execute Simulation")
        self.run_button.setFixedHeight(40)
        self.run_button.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.run_button.clicked.connect(self._execute_simulation)
        layout.addWidget(self.run_button)

        # Console Output Log
        self.log_output = QTextEdit()
        self.log_output.setFixedHeight(150)
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: monospace;")
        layout.addWidget(self.log_output)

        # Matplotlib Plot Area
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self._init_plot_canvas()

    def _init_plot_canvas(self) -> None:
        self.ax.clear()
        self.ax.set_title("Simulation Results", fontsize=11, fontweight='bold')
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Value")
        self.ax.grid(True, linestyle="--", alpha=0.6)
        self.figure.tight_layout()
        self.canvas.draw()

    def _browse_executable(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select OpenModelica Executable",
            str(self.bin_dir),
            "Executables (*);;All Files (*)",
        )
        if file_path:
            self.exe_path_input.setText(file_path)

    def _execute_simulation(self) -> None:
        exe_path = self.exe_path_input.text().strip()
        start_str = self.start_time_input.text().strip()
        stop_str = self.stop_time_input.text().strip()

        if not exe_path:
            QMessageBox.critical(self, "Validation Error", "Please select an executable binary.")
            return

        try:
            start_time, stop_time = validate_times(start_str, stop_str)
        except ValidationError as err:
            QMessageBox.warning(self, "Input Boundary Error", str(err))
            return

        self.log_output.clear()
        self.run_button.setEnabled(False)
        self.run_button.setText("Simulating...")

        self._runner.run_simulation(exe_path, start_time, stop_time)

    def _append_log(self, text: str) -> None:
        self.log_output.moveCursor(self.log_output.textCursor().MoveOperation.End)
        self.log_output.insertPlainText(text)

    def _on_simulation_finished(self, exit_code: int) -> None:
        self.run_button.setEnabled(True)
        self.run_button.setText("Execute Simulation")
        if exit_code == 0:
            self._append_log("\n[SUCCESS] Simulation completed successfully.\n")
            self._plot_results()
        else:
            self._append_log(f"\n[FAILURE] Simulation process exited with code: {exit_code}\n")

    def _plot_results(self) -> None:
        """Plots the tank levels from TwoConnectedTanks_res.mat."""
        mat_file = self.bin_dir / "TwoConnectedTanks_res.mat"

        if not mat_file.exists():
            self._append_log(f"[WARN] Result file not found at: {mat_file}\n")
            return

        try:
            results = read_mat(mat_file)
            time_vals = results["time"]

            self.ax.clear()
            for var_name in self.PLOT_VARIABLES:
                self.ax.plot(time_vals, results[var_name], label=var_name, linewidth=2)

            self.ax.set_title("Two Connected Tanks - Liquid Levels", fontsize=11, fontweight='bold')
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Level")
            self.ax.grid(True, linestyle="--", alpha=0.6)
            self.ax.legend(loc="upper right")
            self.figure.tight_layout()
            self.canvas.draw()

            self._append_log("[INFO] Plot rendered successfully.\n")

        except Exception as err:
            self._append_log(f"[ERROR] Failed to plot results: {str(err)}\n")