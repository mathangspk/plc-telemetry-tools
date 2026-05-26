import logging
from typing import Set, List, Dict, Optional

from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QWidget, 
                             QHBoxLayout, QPushButton, QComboBox, QMessageBox, QInputDialog)

from ui_components import SignalComboBox
from data_loader import DataLoader

logger = logging.getLogger(__name__)

class ConfigTreeManager:
    """
    Manages the UI Tree that displays the hierarchy of Groups and their Signals.
    This encapsulates all the messy UI creation and data extraction loops.
    """
    
    def __init__(self, parent_widget: QWidget, data_loader: DataLoader):
        self.parent_widget = parent_widget
        self.data_loader = data_loader
        
        # Setup the physical tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Item Type", "Name / Signal", "Metric / Action"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 350)
        
    def get_widget(self) -> QTreeWidget:
        """Returns the actual Qt widget for placement in a layout."""
        return self.tree
        
    def clear(self):
        """Clears all data from the tree."""
        self.tree.clear()
        
    def update_data_loader(self, new_data_loader: DataLoader):
        """Updates the underlying data source."""
        self.data_loader = new_data_loader
        self.clear()
        
    def prompt_add_group(self):
        """Opens a dialog to ask for a group name, then adds it."""
        group_name, is_ok = QInputDialog.getText(
            self.parent_widget, 
            "Add Group", 
            "Group Name (e.g. transA):"
        )
        
        if is_ok and group_name.strip():
            self._create_group_node(group_name.strip())

    def _create_group_node(self, group_name: str):
        """Creates the UI row for a new group."""
        group_node = QTreeWidgetItem(self.tree)
        group_node.setText(0, "Group")
        group_node.setText(1, group_name)
        
        # Create buttons for the group row
        actions_container = QWidget()
        layout = QHBoxLayout(actions_container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        btn_add_signal = QPushButton("Add Signal Row")
        btn_add_signal.clicked.connect(lambda: self._create_signal_node(group_node, group_name))
        
        btn_remove_group = QPushButton("Remove")
        btn_remove_group.clicked.connect(lambda: self._remove_group_node(group_node))
        
        layout.addWidget(btn_add_signal)
        layout.addWidget(btn_remove_group)
        
        self.tree.setItemWidget(group_node, 2, actions_container)
        group_node.setExpanded(True)
        logger.info(f"Added group: {group_name}")

    def _remove_group_node(self, group_node: QTreeWidgetItem):
        """Removes a group row, prompting for confirmation if it has children."""
        if group_node.childCount() > 0:
            reply = QMessageBox.question(
                self.parent_widget, 'Confirm Removal', 
                f"Group '{group_node.text(1)}' contains signals. Remove it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        index = self.tree.indexOfTopLevelItem(group_node)
        if index >= 0:
            self.tree.takeTopLevelItem(index)

    def _create_signal_node(self, parent_group_node: QTreeWidgetItem, group_name: str):
        """Creates the UI row for a signal under a specific group."""
        signal_node = QTreeWidgetItem(parent_group_node)
        signal_node.setText(0, "Signal")
        
        # Create the smart combobox for signal selection
        signal_combo = SignalComboBox(group_name, tree_manager=self)
        available_signals = self.get_available_signals(group_name)
        
        if not available_signals:
            signal_combo.addItem("No available signals")
        else:
            first_signal = available_signals[0]
            signal_combo.addItem(first_signal["name"], userData=first_signal)
            
        self.tree.setItemWidget(signal_node, 1, signal_combo)
        
        # Create the metric combobox and remove button
        actions_container = QWidget()
        layout = QHBoxLayout(actions_container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        metric_combo = QComboBox()
        metric_combo.addItems(self.data_loader.get_metrics())
        
        btn_remove_signal = QPushButton("Remove")
        btn_remove_signal.clicked.connect(lambda: parent_group_node.removeChild(signal_node))
        
        layout.addWidget(metric_combo)
        layout.addWidget(btn_remove_signal)
        
        self.tree.setItemWidget(signal_node, 2, actions_container)

    def get_available_signals(self, group_name: str, ignore_combo: Optional[SignalComboBox] = None) -> List[Dict[str, str]]:
        """Finds all signals for a group that haven't been selected yet."""
        all_group_signals = self.data_loader.get_signals_by_group(group_name)
        currently_selected_names = self._get_all_selected_signal_names(ignore_combo)
        
        # Return only the signals that aren't in the selected list
        return [sig for sig in all_group_signals if sig["name"] not in currently_selected_names]

    def _get_all_selected_signal_names(self, ignore_combo: Optional[SignalComboBox] = None) -> Set[str]:
        """Scans the entire tree to find which signal names are currently selected."""
        selected_names: Set[str] = set()
        
        for i in range(self.tree.topLevelItemCount()):
            group_node = self.tree.topLevelItem(i)
            
            for j in range(group_node.childCount()):
                signal_node = group_node.child(j)
                combo_widget = self.tree.itemWidget(signal_node, 1)
                
                if isinstance(combo_widget, SignalComboBox) and combo_widget != ignore_combo:
                    selected_data = combo_widget.currentData()
                    if selected_data and "name" in selected_data:
                        selected_names.add(selected_data["name"])
                        
        return selected_names

    def extract_configuration_data(self) -> List[Dict[str, str]]:
        """
        The most important method: Converts the visual tree state into a clean list of dictionaries
        ready for export.
        """
        extracted_data: List[Dict[str, str]] = []
        
        for i in range(self.tree.topLevelItemCount()):
            group_node = self.tree.topLevelItem(i)
            
            for j in range(group_node.childCount()):
                signal_node = group_node.child(j)
                
                signal_combo = self.tree.itemWidget(signal_node, 1)
                actions_container = self.tree.itemWidget(signal_node, 2)
                
                metric_combo = None
                if actions_container and actions_container.layout():
                    metric_combo = actions_container.layout().itemAt(0).widget()
                
                # If the widgets exist and have valid data selected, add it to our list
                if isinstance(signal_combo, SignalComboBox) and isinstance(metric_combo, QComboBox):
                    signal_data = signal_combo.currentData()
                    if signal_data: 
                        metric_name = metric_combo.currentText()
                        extracted_data.append({
                            "name": signal_data["name"],
                            "path": signal_data["path"],
                            "metric": metric_name
                        })
                        
        return extracted_data
