import logging
from typing import Dict, List, Optional, Set

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from data_loader import DataLoader
from ui_components import SignalComboBox

logger = logging.getLogger(__name__)


class ConfigTreeManager:
    """Manages the UI Tree that displays the hierarchy of Groups and their Signals.

    Args:
        parent_widget (QWidget): The parent widget holding this tree.
        data_loader (DataLoader): The data source to provide metrics and signals.
    """

    def __init__(self, parent_widget: QWidget, data_loader: DataLoader) -> None:
        self.parent_widget: QWidget = parent_widget
        self.data_loader: DataLoader = data_loader

        self.tree: QTreeWidget = QTreeWidget()
        self.tree.setHeaderLabels(["Item Type", "Name / Signal", "Metric / Action"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 350)

    def get_widget(self) -> QTreeWidget:
        """Returns the actual Qt widget for placement in a layout.

        Returns:
            QTreeWidget: The tree widget instance.
        """
        return self.tree

    def clear(self) -> None:
        """Clears all data from the tree."""
        self.tree.clear()

    def update_data_loader(self, new_data_loader: DataLoader) -> None:
        """Updates the underlying data source.

        Args:
            new_data_loader (DataLoader): The new DataLoader instance.
        """
        self.data_loader = new_data_loader
        self.clear()

    def prompt_add_group(self) -> None:
        """Opens a dialog to ask for a group name, then adds it to the tree."""
        group_name, is_ok = QInputDialog.getText(
            self.parent_widget, "Add Group", "Group Name (e.g. transA):"
        )

        if is_ok and group_name.strip():
            self._create_group_node(group_name.strip())

    def _create_group_node(self, group_name: str) -> None:
        """Creates the UI row for a new group.

        Args:
            group_name (str): The name of the group to add.
        """
        group_node: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        group_node.setText(0, "Group")
        group_node.setText(1, group_name)

        actions_container: QWidget = QWidget()
        layout: QHBoxLayout = QHBoxLayout(actions_container)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_add_signal: QPushButton = QPushButton("Add Signal Row")
        btn_add_signal.clicked.connect(
            lambda: self._create_signal_node(group_node, group_name)
        )

        btn_remove_group: QPushButton = QPushButton("Remove")
        btn_remove_group.clicked.connect(lambda: self._remove_group_node(group_node))

        layout.addWidget(btn_add_signal)
        layout.addWidget(btn_remove_group)

        self.tree.setItemWidget(group_node, 2, actions_container)
        group_node.setExpanded(True)
        logger.info(f"Added group: {group_name}")

    def _remove_group_node(self, group_node: QTreeWidgetItem) -> None:
        """Removes a group row, prompting for confirmation if it has children.

        Args:
            group_node (QTreeWidgetItem): The group tree item to remove.
        """
        if group_node.childCount() > 0:
            reply = QMessageBox.question(
                self.parent_widget,
                "Confirm Removal",
                f"Group '{group_node.text(1)}' contains signals. Remove it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        index: int = self.tree.indexOfTopLevelItem(group_node)
        if index >= 0:
            self.tree.takeTopLevelItem(index)

    def _create_signal_node(
        self, parent_group_node: QTreeWidgetItem, group_name: str
    ) -> None:
        """Creates the UI row for a signal under a specific group.

        Args:
            parent_group_node (QTreeWidgetItem): The parent group tree item.
            group_name (str): The name of the group for filtering signals.
        """
        signal_node: QTreeWidgetItem = QTreeWidgetItem(parent_group_node)
        signal_node.setText(0, "Signal")

        signal_combo: SignalComboBox = SignalComboBox(group_name, tree_manager=self)
        available_signals: List[Dict[str, str]] = self.get_available_signals(group_name)

        if not available_signals:
            signal_combo.addItem("No available signals")
        else:
            first_signal: Dict[str, str] = available_signals[0]
            signal_combo.addItem(first_signal["name"], userData=first_signal)

        self.tree.setItemWidget(signal_node, 1, signal_combo)

        actions_container: QWidget = QWidget()
        layout: QHBoxLayout = QHBoxLayout(actions_container)
        layout.setContentsMargins(0, 0, 0, 0)

        metric_combo: QComboBox = QComboBox()
        metric_combo.addItems(self.data_loader.get_metrics())

        btn_remove_signal: QPushButton = QPushButton("Remove")
        btn_remove_signal.clicked.connect(
            lambda: parent_group_node.removeChild(signal_node)
        )

        layout.addWidget(metric_combo)
        layout.addWidget(btn_remove_signal)

        self.tree.setItemWidget(signal_node, 2, actions_container)

    def get_available_signals(
        self, group_name: str, ignore_combo: Optional[SignalComboBox] = None
    ) -> List[Dict[str, str]]:
        """Finds all signals for a group that haven't been selected yet.

        Args:
            group_name (str): The name of the group.
            ignore_combo (Optional[SignalComboBox], optional): A combobox to exclude from the filter. Defaults to None.

        Returns:
            List[Dict[str, str]]: A list of available signal dictionaries.
        """
        all_group_signals: List[Dict[str, str]] = self.data_loader.get_signals_by_group(
            group_name
        )
        currently_selected_names: Set[str] = self._get_all_selected_signal_names(
            ignore_combo
        )

        return [
            sig
            for sig in all_group_signals
            if sig["name"] not in currently_selected_names
        ]

    def _get_all_selected_signal_names(
        self, ignore_combo: Optional[SignalComboBox] = None
    ) -> Set[str]:
        """Scans the entire tree to find which signal names are currently selected.

        Args:
            ignore_combo (Optional[SignalComboBox], optional): A combobox to ignore. Defaults to None.

        Returns:
            Set[str]: A set of selected signal names.
        """
        selected_names: Set[str] = set()

        for i in range(self.tree.topLevelItemCount()):
            group_node: QTreeWidgetItem = self.tree.topLevelItem(i)

            for j in range(group_node.childCount()):
                signal_node: QTreeWidgetItem = group_node.child(j)
                combo_widget: QWidget = self.tree.itemWidget(signal_node, 1)

                if (
                    isinstance(combo_widget, SignalComboBox)
                    and combo_widget != ignore_combo
                ):
                    selected_data: Optional[Dict[str, str]] = combo_widget.currentData()
                    if selected_data and "name" in selected_data:
                        selected_names.add(selected_data["name"])

        return selected_names

    def extract_configuration_data(self) -> List[Dict[str, str]]:
        """Converts the visual tree state into a clean list of dictionaries ready for export.

        Returns:
            List[Dict[str, str]]: A list of signal configurations extracted from the UI.
        """
        extracted_data: List[Dict[str, str]] = []

        for i in range(self.tree.topLevelItemCount()):
            group_node: QTreeWidgetItem = self.tree.topLevelItem(i)

            for j in range(group_node.childCount()):
                signal_node: QTreeWidgetItem = group_node.child(j)

                signal_combo: QWidget = self.tree.itemWidget(signal_node, 1)
                actions_container: QWidget = self.tree.itemWidget(signal_node, 2)

                metric_combo: Optional[QWidget] = None
                if actions_container and actions_container.layout():
                    metric_combo = actions_container.layout().itemAt(0).widget()

                if isinstance(signal_combo, SignalComboBox) and isinstance(
                    metric_combo, QComboBox
                ):
                    signal_data: Optional[Dict[str, str]] = signal_combo.currentData()
                    if signal_data:
                        metric_name: str = metric_combo.currentText()
                        extracted_data.append(
                            {
                                "name": signal_data["name"],
                                "path": signal_data["path"],
                                "metric": metric_name,
                            }
                        )

        return extracted_data
