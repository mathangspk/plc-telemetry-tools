import logging

from core.data_loader import DataLoader
from PyQt6.QtWidgets import QFileDialog, QLineEdit, QMessageBox
from ui.tree.tree_base import ConfigTreeManager
from ui.tree.tree_importer import reconstruct_tree_from_config

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


def on_open_config_clicked(
    window, txt_trace_name: QLineEdit, tree_manager: ConfigTreeManager
) -> None:
    """Handles opening a previously exported config file and rebuilding the tree."""
    file_path, _ = QFileDialog.getOpenFileName(
        window, "Select Config JSON", "", "JSON Files (*.json)"
    )
    if not file_path:
        return
    try:
        trace_name = reconstruct_tree_from_config(tree_manager, file_path)
        txt_trace_name.setText(trace_name)
    except Exception as e:
        QMessageBox.critical(window, "Error", f"Failed to load config: {e}")
