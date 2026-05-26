import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from PyQt6.QtWidgets import QComboBox, QWidget

if TYPE_CHECKING:
    from ui.tree.tree_base import ConfigTreeManager

logger = logging.getLogger(__name__)


class SignalComboBox(QComboBox):
    """A dropdown menu for selecting telemetry signals dynamically."""

    def __init__(
        self,
        group_name: str,
        tree_manager: "ConfigTreeManager",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.group_name = group_name
        self.tree_manager = tree_manager

    def showPopup(self) -> None:
        """Triggered when the user clicks the dropdown. Repopulates to exclude duplicates."""
        from ui.tree.tree_extractor import get_available_signals

        current_selection = self.currentData()

        self.blockSignals(True)
        self.clear()

        avails = get_available_signals(
            self.tree_manager, self.group_name, ignore_combo=self
        )
        if not avails:
            self.addItem("No available signals")
        else:
            for sig in avails:
                self.addItem(sig["name"], userData=sig)
                if current_selection and sig["name"] == current_selection.get("name"):
                    self.setCurrentIndex(self.count() - 1)

        self.blockSignals(False)
        super().showPopup()
