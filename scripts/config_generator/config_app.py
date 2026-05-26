import sys
import logging
from pathlib import Path
from typing import Set, List, Dict, Optional, Any

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTreeWidget, QTreeWidgetItem, QPushButton, 
                             QLineEdit, QLabel, QComboBox, QMessageBox, QFileDialog, QInputDialog)
from PyQt6.QtCore import Qt

from data_loader import DataLoader
from exporter import export_config

# Configure application logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from ui_components import SignalComboBox


class ConfigApp(QMainWindow):
    """Main Application Window for Telemetry Config Generator."""
    
    def __init__(self, data_loader: DataLoader) -> None:
        super().__init__()
        self.data_loader: DataLoader = data_loader
        self.init_ui()

    def init_ui(self) -> None:
        """Initializes the UI layout and components."""
        self.setWindowTitle("Telemetry Config Generator")
        self.resize(900, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Header layout setup
        self.header_layout = QHBoxLayout()
        
        self.browse_btn = QPushButton("Browse Pool Signal...")
        self.browse_btn.clicked.connect(self.browse_file)
        
        self.trace_label = QLabel("Trace Name:")
        self.trace_input = QLineEdit()
        self.trace_input.setPlaceholderText("e.g. TraceLiftDrive")
        
        self.add_group_btn = QPushButton("Add Group")
        self.add_group_btn.clicked.connect(self.add_group)
        
        self.export_btn = QPushButton("Export Config")
        self.export_btn.clicked.connect(self.export_data)
        
        self.header_layout.addWidget(self.browse_btn)
        self.header_layout.addWidget(self.trace_label)
        self.header_layout.addWidget(self.trace_input)
        self.header_layout.addWidget(self.add_group_btn)
        self.header_layout.addWidget(self.export_btn)
        self.layout.addLayout(self.header_layout)
        
        self.file_label = QLabel(f"Current Pool File: {self.data_loader.file_path}")
        self.layout.addWidget(self.file_label)
        
        # Tree Widget setup
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Item", "Signal / Group Name", "Metric / Actions"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 350)
        self.layout.addWidget(self.tree)
        
    def browse_file(self) -> None:
        """Opens a file dialog to select a new JSON pool signal file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Pool Signal JSON", "", "JSON Files (*.json)")
        if file_path:
            reply = QMessageBox.question(
                self, 'Confirm Reload', 
                "Changing the pool signal file will clear the current tree. Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                logger.info(f"Reloading pool signal file from {file_path}")
                self.data_loader = DataLoader(file_path)
                self.file_label.setText(f"Current Pool File: {file_path}")
                self.tree.clear()
        
    def remove_group(self, group_item: QTreeWidgetItem) -> None:
        """Removes a group after confirming if it contains signal rows."""
        if group_item.childCount() > 0:
            reply = QMessageBox.question(
                self, 'Confirm Removal', 
                f"Group '{group_item.text(1)}' contains {group_item.childCount()} signals.\nAre you sure you want to remove it and release these signals?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        index = self.tree.indexOfTopLevelItem(group_item)
        if index >= 0:
            self.tree.takeTopLevelItem(index)
            logger.info(f"Removed group: {group_item.text(1)}")

    def add_group(self) -> None:
        """Prompts the user for a group name and adds it to the tree."""
        group_name, ok = QInputDialog.getText(self, "Add Group", "Group Name (e.g. transA):")
        if ok and group_name.strip():
            group_name = group_name.strip()
            
            group_item = QTreeWidgetItem(self.tree)
            group_item.setText(0, "Group")
            group_item.setText(1, group_name)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            add_signal_btn = QPushButton("Add Signal Row")
            add_signal_btn.clicked.connect(lambda: self.add_signal_row(group_item, group_name))
            
            remove_group_btn = QPushButton("Remove")
            remove_group_btn.clicked.connect(lambda: self.remove_group(group_item))
            
            actions_layout.addWidget(add_signal_btn)
            actions_layout.addWidget(remove_group_btn)
            
            self.tree.setItemWidget(group_item, 2, actions_widget)
            group_item.setExpanded(True)
            logger.info(f"Added new group: {group_name}")

    def get_selected_signals(self, ignore_combo: Optional[SignalComboBox] = None) -> Set[str]:
        """
        Gathers all currently selected signal names across the entire tree UI.
        
        Args:
            ignore_combo: A combobox to exclude from the gathering (usually the one being updated).
            
        Returns:
            A set of selected signal names.
        """
        selected: Set[str] = set()
        for i in range(self.tree.topLevelItemCount()):
            group_item = self.tree.topLevelItem(i)
            for j in range(group_item.childCount()):
                signal_item = group_item.child(j)
                combo = self.tree.itemWidget(signal_item, 1)
                
                if isinstance(combo, SignalComboBox) and combo != ignore_combo:
                    data: Optional[Dict[str, str]] = combo.currentData()
                    if data and "name" in data:
                        selected.add(data["name"])
        return selected

    def get_available_signals(self, group_name: str, combo: Optional[SignalComboBox] = None) -> List[Dict[str, str]]:
        """
        Filters signals by group name and excludes globally selected signals.
        
        Args:
            group_name: The group name to filter signals by.
            combo: The combobox requesting the signals (to ignore its own selection).
            
        Returns:
            A list of available signal dictionaries.
        """
        filtered = self.data_loader.get_signals_by_group(group_name)
        selected = self.get_selected_signals(ignore_combo=combo)
        return [s for s in filtered if s["name"] not in selected]

    def add_signal_row(self, group_item: QTreeWidgetItem, group_name: str) -> None:
        """
        Adds a new signal row under the specified group item.
        
        Args:
            group_item: The parent QTreeWidgetItem representing the group.
            group_name: The string name of the group for signal filtering.
        """
        signal_item = QTreeWidgetItem(group_item)
        signal_item.setText(0, "Signal")
        
        signal_combo = SignalComboBox(group_name, self)
        
        # Initial population of the combobox
        available = self.get_available_signals(group_name)
        if not available:
            signal_combo.addItem("No available signals")
        else:
            signal_combo.addItem(available[0]["name"], userData=available[0])
            
        self.tree.setItemWidget(signal_item, 1, signal_combo)
        
        # Actions layout for the Metric combobox and Remove button
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        metric_combo = QComboBox()
        metric_combo.addItems(self.data_loader.get_metrics())
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: group_item.removeChild(signal_item))
        
        actions_layout.addWidget(metric_combo)
        actions_layout.addWidget(remove_btn)
        
        self.tree.setItemWidget(signal_item, 2, actions_widget)

    def export_data(self) -> None:
        """Gathers configuration data from the UI and triggers the export."""
        trace_name = self.trace_input.text().strip()
        if not trace_name:
            QMessageBox.warning(self, "Error", "Please enter a Trace Name.")
            return
            
        signals_data: List[Dict[str, str]] = []
        for i in range(self.tree.topLevelItemCount()):
            group_item = self.tree.topLevelItem(i)
            for j in range(group_item.childCount()):
                signal_item = group_item.child(j)
                
                signal_combo = self.tree.itemWidget(signal_item, 1)
                actions_widget = self.tree.itemWidget(signal_item, 2)
                
                metric_combo = None
                if actions_widget and actions_widget.layout():
                    metric_combo = actions_widget.layout().itemAt(0).widget()
                
                if isinstance(signal_combo, SignalComboBox) and isinstance(metric_combo, QComboBox):
                    sig_data = signal_combo.currentData()
                    if sig_data: 
                        metric = metric_combo.currentText()
                        signals_data.append({
                            "name": sig_data["name"],
                            "path": sig_data["path"],
                            "metric": metric
                        })
                    
        if not signals_data:
            QMessageBox.warning(self, "Warning", "No valid signals added to export.")
            return
            
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if export_dir:
            file_path = export_config(trace_name, signals_data, export_dir)
            if file_path:
                QMessageBox.information(self, "Success", f"Exported to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export configuration. Check logs.")

def main() -> None:
    """Entry point for the application."""
    app = QApplication(sys.argv)
    
    # Load default data from active_signals.json, fallback to mock if unavailable
    data_file_path = Path(r"C:\local\opencode\codesys\exports\pool_signals\active_signals.json")
    if not data_file_path.exists():
        data_file_path = Path("mock_pool_signals.json")
        logger.info(f"Default signal file not found, falling back to {data_file_path}")
        
    loader = DataLoader(str(data_file_path))
    window = ConfigApp(loader)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
