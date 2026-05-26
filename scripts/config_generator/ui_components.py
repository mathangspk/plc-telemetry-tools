import logging
from typing import Optional, List, Dict
from PyQt6.QtWidgets import QComboBox, QWidget

logger = logging.getLogger(__name__)

class SignalComboBox(QComboBox):
    """
    A dropdown menu for selecting telemetry signals.
    It dynamically updates its list of options when clicked, ensuring 
    that a user cannot select a signal that has already been chosen elsewhere.
    """
    def __init__(self, group_name: str, tree_manager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.group_name: str = group_name
        self.tree_manager = tree_manager

    def showPopup(self) -> None:
        """
        Triggered when the user clicks the dropdown.
        We repopulate the list of signals to exclude those already selected.
        """
        # Remember what the user currently has selected, if anything
        current_selection: Optional[Dict[str, str]] = self.currentData()
        
        # Stop sending signals while we update the list
        self.blockSignals(True)
        self.clear()
        
        # Ask the tree manager for signals that are still available
        available_signals: List[Dict[str, str]] = self.tree_manager.get_available_signals(self.group_name, ignore_combo=self)
        
        if not available_signals:
            self.addItem("No available signals")
        else:
            for signal_data in available_signals:
                self.addItem(signal_data["name"], userData=signal_data)
                
                # If this item was previously selected, re-select it
                if current_selection and signal_data["name"] == current_selection.get("name"):
                    self.setCurrentIndex(self.count() - 1)
                    
        # Resume sending signals
        self.blockSignals(False)
        super().showPopup()
