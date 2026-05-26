import logging
from typing import Optional, List, Dict, TYPE_CHECKING
from PyQt6.QtWidgets import QComboBox, QWidget

if TYPE_CHECKING:
    from config_app import ConfigApp

logger = logging.getLogger(__name__)

class SignalComboBox(QComboBox):
    """
    Custom QComboBox for signals that dynamically recalculates its items when clicked
    to exclude signals that are already selected in other rows.
    """
    def __init__(self, group_name: str, app_ref: 'ConfigApp', parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.group_name: str = group_name
        self.app_ref: 'ConfigApp' = app_ref

    def showPopup(self) -> None:
        """Overrides showPopup to dynamically repopulate options based on global exclusions."""
        current_data: Optional[Dict[str, str]] = self.currentData()
        self.blockSignals(True)
        self.clear()
        
        available: List[Dict[str, str]] = self.app_ref.get_available_signals(self.group_name, self)
        
        if not available:
            self.addItem("No available signals")
        else:
            for sig in available:
                self.addItem(sig["name"], userData=sig)
                if current_data and sig["name"] == current_data.get("name"):
                    self.setCurrentIndex(self.count() - 1)
                    
        self.blockSignals(False)
        super().showPopup()
