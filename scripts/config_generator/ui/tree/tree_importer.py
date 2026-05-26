import json
import logging
from pathlib import Path

from PyQt6.QtWidgets import QComboBox
from ui.tree.tree_base import ConfigTreeManager
from ui.tree.tree_nodes import create_group_node, create_signal_node
from ui.ui_components import SignalComboBox

logger = logging.getLogger(__name__)


def reconstruct_tree_from_config(
    manager: ConfigTreeManager, file_path: Path | str
) -> str:
    """Reads a JSON config and rebuilds the tree, grouping signals by underscore prefix."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    trace_name = data.get("name", "")
    manager.clear()

    group_map = {}
    for i in range(manager.tree.topLevelItemCount()):
        group_node = manager.tree.topLevelItem(i)
        group_map[group_node.text(1)] = group_node

    for sig in data.get("signals", []):
        sig_name = sig.get("name", "")
        group_name = sig_name.split("_")[0] if "_" in sig_name else "Ungrouped"

        if group_name not in group_map:
            create_group_node(manager, group_name)
            group_map[group_name] = manager.tree.topLevelItem(
                manager.tree.topLevelItemCount() - 1
            )

        group_node = group_map[group_name]
        create_signal_node(manager, group_node, group_name)

        sig_node = group_node.child(group_node.childCount() - 1)
        combo = manager.tree.itemWidget(sig_node, 1)
        if isinstance(combo, SignalComboBox):
            idx = combo.findText(sig_name)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        metric_widget = manager.tree.itemWidget(sig_node, 2)
        if metric_widget and metric_widget.layout():
            m_combo = metric_widget.layout().itemAt(0).widget()
            if isinstance(m_combo, QComboBox):
                m_idx = m_combo.findText(sig.get("metric", ""))
                if m_idx >= 0:
                    m_combo.setCurrentIndex(m_idx)

    return trace_name
