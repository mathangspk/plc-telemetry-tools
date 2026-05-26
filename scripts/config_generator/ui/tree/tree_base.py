import logging

from core.data_loader import DataLoader
from PyQt6.QtWidgets import QTreeWidget, QWidget

logger = logging.getLogger(__name__)


class ConfigTreeManager:
    """Manages the UI Tree hierarchy of Groups and Signals."""

    def __init__(self, parent_widget: QWidget, data_loader: DataLoader) -> None:
        self.parent_widget: QWidget = parent_widget
        self.data_loader: DataLoader = data_loader
        self.tree: QTreeWidget = QTreeWidget()
        self.tree.setHeaderLabels(["Name / Signal", "Actions", "Metric"])
        self.tree.setColumnWidth(0, 350)
        self.tree.setColumnWidth(1, 200)

    def get_widget(self) -> QTreeWidget:
        return self.tree

    def clear(self) -> None:
        self.tree.clear()

    def update_data_loader(self, new_data_loader: DataLoader) -> None:
        self.data_loader = new_data_loader
        self.clear()
