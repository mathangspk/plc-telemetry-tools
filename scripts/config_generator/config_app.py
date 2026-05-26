import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLineEdit, QLabel, QMessageBox, QFileDialog)

from data_loader import DataLoader
from tree_manager import ConfigTreeManager
import exporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigApp(QMainWindow):
    """
    Main Application Window.
    This class is now extremely lean. It acts as the Controller: 
    setting up the layout and wiring buttons to the TreeManager and Exporter.
    """
    
    def __init__(self, data_loader: DataLoader) -> None:
        super().__init__()
        self.data_loader = data_loader
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the visual layout of the main window."""
        self.setWindowTitle("Telemetry Config Generator")
        self.resize(900, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Top Header Area ---
        header_layout = QHBoxLayout()
        
        btn_browse = QPushButton("Browse Pool Signal...")
        btn_browse.clicked.connect(self.on_browse_clicked)
        
        lbl_trace = QLabel("Trace Name:")
        self.txt_trace_name = QLineEdit()
        self.txt_trace_name.setPlaceholderText("e.g. TraceLiftDrive")
        
        btn_add_group = QPushButton("Add Group")
        btn_add_group.clicked.connect(self.on_add_group_clicked)
        
        btn_export = QPushButton("Export Config")
        btn_export.clicked.connect(self.on_export_clicked)
        
        header_layout.addWidget(btn_browse)
        header_layout.addWidget(lbl_trace)
        header_layout.addWidget(self.txt_trace_name)
        header_layout.addWidget(btn_add_group)
        header_layout.addWidget(btn_export)
        
        main_layout.addLayout(header_layout)
        
        # --- File Path Label ---
        self.lbl_file_path = QLabel(f"Current Pool File: {self.data_loader.file_path}")
        main_layout.addWidget(self.lbl_file_path)
        
        # --- Main Data Tree ---
        self.tree_manager = ConfigTreeManager(parent_widget=self, data_loader=self.data_loader)
        main_layout.addWidget(self.tree_manager.get_widget())

    # --- Event Handlers ---

    def on_browse_clicked(self) -> None:
        """Handles selecting a new JSON pool file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Pool Signal JSON", "", "JSON Files (*.json)")
        if not file_path:
            return
            
        reply = QMessageBox.question(
            self, 'Confirm Reload', 
            "Changing the pool signal file will clear the current tree. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
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
        trace_name = self.txt_trace_name.text().strip()
        if not trace_name:
            QMessageBox.warning(self, "Error", "Please enter a Trace Name.")
            return
            
        # 1. Get clean data from the tree
        signals_data = self.tree_manager.extract_configuration_data()
        
        if not signals_data:
            QMessageBox.warning(self, "Warning", "No valid signals added to export.")
            return
            
        # 2. Ask user where to save
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
            
        # 3. Export
        file_path = exporter.export_config(trace_name, signals_data, export_dir)
        
        if file_path:
            QMessageBox.information(self, "Success", f"Exported successfully to:\n{file_path}")
        else:
            QMessageBox.critical(self, "Error", "Failed to export configuration. Check logs.")


def main() -> None:
    app = QApplication(sys.argv)
    
    # Setup initial data loader
    default_path = Path(r"C:\local\opencode\codesys\exports\pool_signals\active_signals.json")
    fallback_path = Path("mock_pool_signals.json")
    
    active_path = default_path if default_path.exists() else fallback_path
    if not default_path.exists():
        logger.info(f"Default signal file not found, falling back to {fallback_path}")
        
    loader = DataLoader(str(active_path))
    
    window = ConfigApp(loader)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
