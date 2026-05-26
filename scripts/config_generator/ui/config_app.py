import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import exporter
from core.data_loader import DataLoader
from ui.tree_manager import ConfigTreeManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConfigApp(QMainWindow):
    """Main Application Window.

    This class is extremely lean. It acts as the Controller:
    setting up the layout and wiring buttons to the TreeManager and Exporter.

    Args:
        data_loader (DataLoader): The initial data loader instance.
    """

    def __init__(self, data_loader: DataLoader) -> None:
        super().__init__()
        self.data_loader: DataLoader = data_loader
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the visual layout of the main window."""
        self.setWindowTitle("Telemetry Config Generator")
        self.resize(900, 600)

        central_widget: QWidget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout: QVBoxLayout = QVBoxLayout(central_widget)

        header_layout: QHBoxLayout = QHBoxLayout()

        btn_browse: QPushButton = QPushButton("Browse Pool Signal...")
        btn_browse.clicked.connect(self.on_browse_clicked)

        lbl_trace: QLabel = QLabel("Trace Name:")
        self.txt_trace_name: QLineEdit = QLineEdit()
        self.txt_trace_name.setPlaceholderText("e.g. TraceLiftDrive")

        btn_add_group: QPushButton = QPushButton("Add Group")
        btn_add_group.clicked.connect(self.on_add_group_clicked)

        btn_export: QPushButton = QPushButton("Export Config")
        btn_export.clicked.connect(self.on_export_clicked)

        header_layout.addWidget(btn_browse)
        header_layout.addWidget(lbl_trace)
        header_layout.addWidget(self.txt_trace_name)
        header_layout.addWidget(btn_add_group)
        header_layout.addWidget(btn_export)

        main_layout.addLayout(header_layout)

        self.lbl_file_path: QLabel = QLabel(
            f"Current Pool File: {self.data_loader.file_path}"
        )
        main_layout.addWidget(self.lbl_file_path)

        self.tree_manager: ConfigTreeManager = ConfigTreeManager(
            parent_widget=self, data_loader=self.data_loader
        )
        main_layout.addWidget(self.tree_manager.get_widget())

    def on_browse_clicked(self) -> None:
        """Handles selecting a new JSON pool file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Pool Signal JSON", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Reload",
            "Changing the pool signal file will clear the current tree. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"Reloading pool signal file from {file_path}")
            self.data_loader = DataLoader(file_path)
            self.lbl_file_path.setText(f"Current Pool File: {file_path}")
            self.tree_manager.update_data_loader(self.data_loader)

    def on_add_group_clicked(self) -> None:
        """Delegates group creation to the Tree Manager."""
        self.tree_manager.prompt_add_group()

    def on_export_clicked(self) -> None:
        """Extracts data from the tree and delegates exporting to the Exporter."""
        trace_name: str = self.txt_trace_name.text().strip()
        if not trace_name:
            QMessageBox.warning(self, "Error", "Please enter a Trace Name.")
            return

        signals_data: List[Dict[str, str]] = (
            self.tree_manager.extract_configuration_data()
        )

        if not signals_data:
            QMessageBox.warning(self, "Warning", "No valid signals added to export.")
            return

        export_dir: str = QFileDialog.getExistingDirectory(
            self, "Select Export Directory"
        )
        if not export_dir:
            return

        file_path: Optional[str] = exporter.export_config(
            trace_name, signals_data, export_dir
        )

        if file_path:
            QMessageBox.information(
                self, "Success", f"Exported successfully to:\n{file_path}"
            )
        else:
            QMessageBox.critical(
                self, "Error", "Failed to export configuration. Check logs."
            )
