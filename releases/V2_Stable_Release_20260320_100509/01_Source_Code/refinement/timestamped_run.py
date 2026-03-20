"""Shared TimestampedRun class for Sprint 6 data preservation."""
import json
import os
import shutil
from datetime import datetime


class TimestampedRun:
    """Manages timestamped file outputs and run manifests for reproducibility."""

    def __init__(self, output_dir: str):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = output_dir
        self.run_dir = os.path.join(output_dir, "runs", self.timestamp)
        os.makedirs(self.run_dir, exist_ok=True)
        self.files_written = []
        self.files_read = []

    def output_path(self, filename: str) -> str:
        """Returns timestamped path and registers it."""
        name, ext = os.path.splitext(filename)
        ts_name = f"{name}_{self.timestamp}{ext}"
        ts_path = os.path.join(self.output_dir, ts_name)
        self.files_written.append(ts_path)
        return ts_path

    def stable_pointer(self, filename: str, timestamped_path: str):
        """Creates a stable-name copy pointing to the timestamped version."""
        stable = os.path.join(self.output_dir, filename)
        shutil.copy2(timestamped_path, stable)
        self.files_written.append(stable)

    def record_read(self, filepath: str):
        """Register an input file for the manifest."""
        self.files_read.append(filepath)

    def write_manifest(self, module_name: str, config: dict = None, cost: float = None):
        """Write run manifest and snapshot outputs to run directory."""
        manifest = {
            "timestamp": self.timestamp,
            "module": module_name,
            "inputs_read": self.files_read,
            "outputs_written": self.files_written,
            "config": config or {},
            "cost_usd": cost or 0.0,
        }
        manifest_path = os.path.join(self.run_dir, f"_run_manifest_{self.timestamp}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        # Copy all timestamped outputs to the run snapshot directory
        for fp in self.files_written:
            if os.path.exists(fp) and os.path.abspath(fp) != os.path.abspath(manifest_path):
                dest = os.path.join(self.run_dir, os.path.basename(fp))
                if os.path.abspath(fp) != os.path.abspath(dest):
                    shutil.copy2(fp, dest)
