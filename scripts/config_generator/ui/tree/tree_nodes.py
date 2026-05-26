import logging
from typing import Dict, List

import ui.tree.tree_extractor as extractor
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTreeWidgetItem,
    QWidget,
)
from ui.tree.tree_base import ConfigTreeManager
from ui.ui_components import SignalComboBox

logger = logging.getLogger(__name__)


def create_group_node(manager: ConfigTreeManager, group_name: str) -> None:
    """Creates the UI row for a new group."""
    group_node = QTreeWidgetItem(manager.tree)
    group_node.setText(0, group_name)

    actions_container = QWidget()
    layout = QHBoxLayout(actions_container)
    layout.setContentsMargins(0, 0, 0, 0)

    btn_add_signal = QPushButton("Add Signal Row")
    btn_add_signal.clicked.connect(
        lambda: create_signal_node(manager, group_node, group_name)
    )

    btn_remove_group = QPushButton("Remove")
    btn_remove_group.clicked.connect(lambda: remove_group_node(manager, group_node))

    layout.addWidget(btn_add_signal)
    layout.addWidget(btn_remove_group)
    manager.tree.setItemWidget(group_node, 1, actions_container)
    group_node.setExpanded(True)


def remove_group_node(manager: ConfigTreeManager, group_node: QTreeWidgetItem) -> None:
    """Removes a group row."""
    if group_node.childCount() > 0:
        reply = QMessageBox.question(
            manager.parent_widget,
            "Confirm Removal",
            f"Group '{group_node.text(1)}' contains signals. Remove it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
    idx = manager.tree.indexOfTopLevelItem(group_node)
    if idx >= 0:
        manager.tree.takeTopLevelItem(idx)


def create_signal_node(
    manager: ConfigTreeManager, parent_group: QTreeWidgetItem, group_name: str
) -> None:
    """Creates the UI row for a signal under a specific group."""
    signal_node = QTreeWidgetItem(parent_group)

    signal_combo = SignalComboBox(group_name, tree_manager=manager)
    avails = extractor.get_available_signals(manager, group_name)
    if not avails:
        signal_combo.addItem("No available signals")
    else:
        signal_combo.addItem(avails[0]["name"], userData=avails[0])

    manager.tree.setItemWidget(signal_node, 0, signal_combo)

    actions = QWidget()
    layout = QHBoxLayout(actions)
    layout.setContentsMargins(0, 0, 0, 0)
    btn_rm = QPushButton("Remove")
    btn_rm.clicked.connect(lambda: parent_group.removeChild(signal_node))
    layout.addWidget(btn_rm)
    manager.tree.setItemWidget(signal_node, 1, actions)

    metric_combo = QComboBox()
    metric_combo.addItems(manager.data_loader.get_metrics())
    manager.tree.setItemWidget(signal_node, 2, metric_combo)
