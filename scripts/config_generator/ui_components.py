import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from PyQt6.QtWidgets import QComboBox, QWidget

if TYPE_CHECKING:
    from tree_manager import ConfigTreeManager

logger = logging.getLogger(__name__)


class SignalComboBox(QComboBox):
    """A dropdown menu for selecting telemetry signals dynamically.

    Args:
        group_name (str): The name of the group this combobox belongs to.
        tree_manager (ConfigTreeManager): The tree manager instance to query available signals.
        parent (Optional[QWidget], optional): The parent widget. Defaults to None.
    """

    def __init__(
        self,
        group_name: str,
        tree_manager: "ConfigTreeManager",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.group_name: str = group_name
        self.tree_manager: "ConfigTreeManager" = tree_manager

    def showPopup(self) -> None:
        """Triggered when the user clicks the dropdown.

        Repopulates the list of signals to exclude those already selected elsewhere in the tree.
        """
        current_selection: Optional[Dict[str, str]] = self.currentData()

        self.blockSignals(True)
        self.clear()

        available_signals: List[Dict[str, str]] = (
            self.tree_manager.get_available_signals(self.group_name, ignore_combo=self)
        )

        if not available_signals:
            self.addItem("No available signals")
        else:
            for signal_data in available_signals:
                self.addItem(signal_data["name"], userData=signal_data)

                if current_selection and signal_data["name"] == current_selection.get(
                    "name"
                ):
                    self.setCurrentIndex(self.count() - 1)

        self.blockSignals(False)
        super().showPopup()
