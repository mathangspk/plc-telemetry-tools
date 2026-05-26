from PyQt6.QtWidgets import QInputDialog

from ui.tree.tree_base import ConfigTreeManager
from ui.tree.tree_nodes import create_group_node


def prompt_add_group(manager: ConfigTreeManager) -> None:
    """Opens a dialog to ask for a group name, then adds it to the tree."""
    group_name, is_ok = QInputDialog.getText(
        manager.parent_widget, "Add Group", "Group Name (e.g. transA):"
    )

    if is_ok and group_name.strip():
        create_group_node(manager, group_name.strip())
