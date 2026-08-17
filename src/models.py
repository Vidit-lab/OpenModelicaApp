"""Process execution and management layer using Qt's asynchronous event loop."""

import os
from PyQt6.QtCore import QObject, QProcess, pyqtSignal


class SimulationRunner(QObject):
    """Executes the external OpenModelica compiled executable safely."""

    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self._process = QProcess()
        self._process.readyReadStandardOutput.connect(self._handle_stdout)
        self._process.readyReadStandardError.connect(self._handle_stderr)
        self._process.finished.connect(self._handle_finished)

    def run_simulation(self, exe_path: str, start_time: int, stop_time: int) -> None:
        if not os.path.exists(exe_path):
            self.error_received.emit(f"Executable not found at path: {exe_path}")
            return

        work_dir = os.path.dirname(os.path.abspath(exe_path))
        self._process.setWorkingDirectory(work_dir)

        # Calculate step size explicitly to prevent OMC recalculation warning
        intervals = 500
        step_size = (stop_time - start_time) / intervals

        arguments = [
            f"-startTime={start_time}",
            f"-stopTime={stop_time}",
            f"-stepSize={step_size}",
            "-s=dassl",
        ]

        self.output_received.emit(
            f"Launching: {exe_path} with arguments: {' '.join(arguments)}\n"
        )
        self._process.start(exe_path, arguments)

    def _handle_stdout(self) -> None:
        data = self._process.readAllStandardOutput().data().decode("utf-8")
        self.output_received.emit(data)

    def _handle_stderr(self) -> None:
        data = self._process.readAllStandardError().data().decode("utf-8")
        self.error_received.emit(data)

    def _handle_finished(self, exit_code: int) -> None:
        self.finished.emit(exit_code)