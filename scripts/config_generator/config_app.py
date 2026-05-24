import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTreeWidget, QTreeWidgetItem, QPushButton, 
                             QLineEdit, QLabel, QComboBox, QMessageBox, QFileDialog, QInputDialog)
from PyQt6.QtCore import Qt
from data_loader import DataLoader
from exporter import export_config

class ConfigApp(QMainWindow):
    def __init__(self, data_loader):
        super().__init__()
        self.data_loader = data_loader
        self.setWindowTitle("Telemetry Config Generator")
        self.resize(800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Header layout
        self.header_layout = QHBoxLayout()
        self.trace_label = QLabel("Trace Name:")
        self.trace_input = QLineEdit()
        self.trace_input.setPlaceholderText("e.g. TraceLiftDrive")
        
        self.add_group_btn = QPushButton("Add Group")
        self.add_group_btn.clicked.connect(self.add_group)
        
        self.export_btn = QPushButton("Export Config")
        self.export_btn.clicked.connect(self.export_data)
        
        self.header_layout.addWidget(self.trace_label)
        self.header_layout.addWidget(self.trace_input)
        self.header_layout.addWidget(self.add_group_btn)
        self.header_layout.addWidget(self.export_btn)
        self.layout.addLayout(self.header_layout)
        
        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Item", "Signal / Group Name", "Metric / Actions"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 350)
        self.layout.addWidget(self.tree)
        
    def add_group(self):
        group_name, ok = QInputDialog.getText(self, "Add Group", "Group Name (e.g. transA):")
        if ok and group_name.strip():
            group_name = group_name.strip()
            group_item = QTreeWidgetItem(self.tree)
            group_item.setText(0, "Group")
            group_item.setText(1, group_name)
            
            # Action to add signal to this group
            add_signal_btn = QPushButton("Add Signal Row")
            add_signal_btn.clicked.connect(lambda: self.add_signal_row(group_item, group_name))
            
            self.tree.setItemWidget(group_item, 2, add_signal_btn)
            group_item.setExpanded(True)

    def add_signal_row(self, group_item, group_name):
        signal_item = QTreeWidgetItem(group_item)
        signal_item.setText(0, "Signal")
        
        # Signal Combobox
        signal_combo = QComboBox()
        filtered_signals = self.data_loader.get_signals_by_group(group_name)
        
        if not filtered_signals:
            signal_combo.addItem("No signals found for this group")
        else:
            for sig in filtered_signals:
                signal_combo.addItem(sig["name"], userData=sig) # Store whole dict
                
        self.tree.setItemWidget(signal_item, 1, signal_combo)
        
        # Metric Combobox
        metric_combo = QComboBox()
        metric_combo.addItems(self.data_loader.get_metrics())
        self.tree.setItemWidget(signal_item, 2, metric_combo)

    def export_data(self):
        trace_name = self.trace_input.text().strip()
        if not trace_name:
            QMessageBox.warning(self, "Error", "Please enter a Trace Name.")
            return
            
        signals_data = []
        for i in range(self.tree.topLevelItemCount()):
            group_item = self.tree.topLevelItem(i)
            for j in range(group_item.childCount()):
                signal_item = group_item.child(j)
                
                signal_combo = self.tree.itemWidget(signal_item, 1)
                metric_combo = self.tree.itemWidget(signal_item, 2)
                
                sig_data = signal_combo.currentData()
                if sig_data: # If it's a valid selection
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
            QMessageBox.information(self, "Success", f"Exported to:\n{file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load data from the exported active_signals.json
    data_file = r"C:\local\opencode\codesys\exports\pool_signals\active_signals.json"
    if not os.path.exists(data_file):
        data_file = "mock_pool_signals.json"
        
    loader = DataLoader(data_file)
    window = ConfigApp(loader)
    window.show()
    sys.exit(app.exec())
