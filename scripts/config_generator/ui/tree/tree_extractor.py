from typing import Dict, List, Optional, Set

from PyQt6.QtWidgets import QComboBox

from ui.tree.tree_base import ConfigTreeManager
from ui.ui_components import SignalComboBox


def get_available_signals(
    manager: ConfigTreeManager,
    group_name: str,
    ignore_combo: Optional[SignalComboBox] = None,
) -> List[Dict[str, str]]:
    """Finds all signals for a group that haven't been selected yet."""
    all_sigs = manager.data_loader.get_signals_by_group(group_name)
    selected = get_all_selected_signal_names(manager, ignore_combo)
    return [sig for sig in all_sigs if sig["name"] not in selected]


def get_all_selected_signal_names(
    manager: ConfigTreeManager, ignore_combo: Optional[SignalComboBox] = None
) -> Set[str]:
    """Scans the entire tree to find which signal names are currently selected."""
    selected_names: Set[str] = set()
    for i in range(manager.tree.topLevelItemCount()):
        group_node = manager.tree.topLevelItem(i)
        for j in range(group_node.childCount()):
            signal_node = group_node.child(j)
            combo_widget = manager.tree.itemWidget(signal_node, 1)
            if (
                isinstance(combo_widget, SignalComboBox)
                and combo_widget != ignore_combo
            ):
                selected_data = combo_widget.currentData()
                if selected_data and "name" in selected_data:
                    selected_names.add(selected_data["name"])
    return selected_names


def extract_configuration_data(manager: ConfigTreeManager) -> List[Dict[str, str]]:
    """Converts the visual tree state into a clean list of dictionaries ready for export."""
    extracted_data: List[Dict[str, str]] = []
    for i in range(manager.tree.topLevelItemCount()):
        group_node = manager.tree.topLevelItem(i)
        for j in range(group_node.childCount()):
            signal_node = group_node.child(j)
            signal_combo = manager.tree.itemWidget(signal_node, 1)
            actions = manager.tree.itemWidget(signal_node, 2)
            metric_combo = (
                actions.layout().itemAt(0).widget()
                if actions and actions.layout()
                else None
            )

            if isinstance(signal_combo, SignalComboBox) and isinstance(
                metric_combo, QComboBox
            ):
                signal_data = signal_combo.currentData()
                if signal_data:
                    extracted_data.append(
                        {
                            "name": signal_data["name"],
                            "path": signal_data["path"],
                            "metric": metric_combo.currentText(),
                        }
                    )
    return extracted_data
