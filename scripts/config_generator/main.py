import logging
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from core.data_loader import DataLoader
from ui.config_app import ConfigApp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for the application."""
    app: QApplication = QApplication(sys.argv)

    default_path: Path = Path(
        r"C:\local\opencode\codesys\exports\pool_signals\active_signals.json"
    )
    fallback_path: Path = Path("mock_pool_signals.json")

    active_path: Path = default_path if default_path.exists() else fallback_path
    if not default_path.exists():
        logger.info(f"Default signal file not found, falling back to {fallback_path}")

    loader: DataLoader = DataLoader(str(active_path))

    window: ConfigApp = ConfigApp(loader)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
