import logging
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QLineEdit, QMessageBox

from core import exporter
from ui.tree.tree_base import ConfigTreeManager
from ui.tree.tree_extractor import extract_configuration_data

logger = logging.getLogger(__name__)


def on_export_clicked(
    window, txt_trace_name: QLineEdit, tree_manager: ConfigTreeManager
) -> None:
    """Extracts data and delegates exporting to the Exporter, checking overwrite."""
    trace_name = txt_trace_name.text().strip()
    if not trace_name:
        QMessageBox.warning(window, "Error", "Please enter a Trace Name.")
        return

    signals_data = extract_configuration_data(tree_manager)
    if not signals_data:
        QMessageBox.warning(window, "Warning", "No valid signals added to export.")
        return

    export_dir = QFileDialog.getExistingDirectory(window, "Select Export Directory")
    if not export_dir:
        return

    file_path = Path(export_dir) / f"{trace_name}.json"
    overwrite = False
    if file_path.exists():
        r = QMessageBox.question(
            window,
            "File Exists",
            f"{trace_name}.json exists. Overwrite?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        overwrite = r == QMessageBox.StandardButton.Yes

    result = exporter.export_config(
        trace_name, signals_data, export_dir, overwrite=overwrite
    )
    if result:
        QMessageBox.information(window, "Success", f"Exported to:\n{result}")
    else:
        QMessageBox.critical(window, "Error", "Failed to export. Check logs.")
