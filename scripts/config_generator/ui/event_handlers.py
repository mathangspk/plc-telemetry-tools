import logging
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QLineEdit, QMessageBox

from core import exporter
from core.data_loader import DataLoader
from ui.tree.tree_base import ConfigTreeManager
from ui.tree.tree_dialogs import prompt_add_group
from ui.tree.tree_extractor import extract_configuration_data

logger = logging.getLogger(__name__)


def on_browse_clicked(window) -> None:
    """Handles selecting a new JSON pool file."""
    file_path, _ = QFileDialog.getOpenFileName(
        window, "Select Pool Signal JSON", "", "JSON Files (*.json)"
    )
    if not file_path:
        return

    reply = QMessageBox.question(
        window,
        "Confirm Reload",
        "Clear tree and continue?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    if reply == QMessageBox.StandardButton.Yes:
        logger.info(f"Reloading pool from {file_path}")
        window.data_loader = DataLoader(file_path)
        window.lbl_file_path.setText(f"Current Pool File: {file_path}")
        window.tree_manager.update_data_loader(window.data_loader)


def on_add_group_clicked(tree_manager: ConfigTreeManager) -> None:
    prompt_add_group(tree_manager)


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

    file_path_obj = Path(export_dir) / f"{trace_name}.json"
    overwrite = False
    if file_path_obj.exists():
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
