import logging

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.data_loader import DataLoader
from ui.events_export import on_export_clicked
from ui.events_import import on_browse_clicked, on_open_config_clicked
from ui.tree.tree_base import ConfigTreeManager
from ui.tree.tree_dialogs import prompt_add_group

logger = logging.getLogger(__name__)


class ConfigApp(QMainWindow):
    """Main Application Window."""

    def __init__(self, data_loader: DataLoader) -> None:
        super().__init__()
        self.data_loader: DataLoader = data_loader
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the visual layout."""
        self.setWindowTitle("Telemetry Config Generator")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        header_layout = QHBoxLayout()

        btn_browse = QPushButton("Browse Pool...")
        btn_browse.clicked.connect(lambda: on_browse_clicked(self))

        btn_open = QPushButton("Open Config...")
        btn_open.clicked.connect(
            lambda: on_open_config_clicked(self, self.txt_trace_name, self.tree_manager)
        )

        self.txt_trace_name = QLineEdit()
        self.txt_trace_name.setPlaceholderText("e.g. TraceLiftDrive")

        btn_add_group = QPushButton("Add Group")
        btn_add_group.clicked.connect(lambda: prompt_add_group(self.tree_manager))

        btn_export = QPushButton("Export Config")
        btn_export.clicked.connect(
            lambda: on_export_clicked(self, self.txt_trace_name, self.tree_manager)
        )

        header_layout.addWidget(btn_browse)
        header_layout.addWidget(btn_open)
        header_layout.addWidget(QLabel("Trace Name:"))
        header_layout.addWidget(self.txt_trace_name)
        header_layout.addWidget(btn_add_group)
        header_layout.addWidget(btn_export)
        main_layout.addLayout(header_layout)

        self.lbl_file_path = QLabel(f"Current Pool File: {self.data_loader.file_path}")
        main_layout.addWidget(self.lbl_file_path)

        self.tree_manager = ConfigTreeManager(
            parent_widget=self, data_loader=self.data_loader
        )
        main_layout.addWidget(self.tree_manager.get_widget())
