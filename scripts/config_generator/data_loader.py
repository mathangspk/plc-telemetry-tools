import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """Represents a single telemetry signal configuration.

    Args:
        name (str): The name of the signal.
        path (str): The path to the signal in the PLC.
    """

    name: str
    path: str


class DataLoader:
    """Loads and manages telemetry pool signals and metrics from a JSON file.

    Args:
        file_path (Union[str, Path]): The absolute or relative path to the JSON pool file.
    """

    def __init__(self, file_path: Union[str, Path]) -> None:
        self.file_path: Path = Path(file_path)
        self.metrics: List[str] = []
        self.signals: List[Dict[str, str]] = []
        self.load_data()

    def load_data(self) -> None:
        """Reads the JSON file and extracts metrics and signals.

        Raises:
            ValueError: If the JSON root is not a dictionary.
        """
        if not self.file_path.exists() or not self.file_path.is_file():
            logger.warning(
                f"File {self.file_path} not found or is not a file. Starting with empty data."
            )
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data: Any = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("JSON root must be a dictionary")
                self.metrics = data.get("metrics", [])
                self.signals = data.get("signals", [])
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {self.file_path}: {e}")
        except ValueError as e:
            logger.error(f"Invalid data format in {self.file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading data from {self.file_path}: {e}")

    def get_metrics(self) -> List[str]:
        """Returns the list of available metrics.

        Returns:
            List[str]: A list of metric names.
        """
        return self.metrics

    def get_signals_by_group(self, group_name: str) -> List[Dict[str, str]]:
        """Filters and returns signals matching the given group name (case-insensitive).

        Args:
            group_name (str): The group string to filter signals by.

        Returns:
            List[Dict[str, str]]: A list of signal dictionaries matching the group name.
        """
        if not group_name:
            return []
        group_name_lower: str = group_name.lower()
        return [
            s for s in self.signals if group_name_lower in s.get("name", "").lower()
        ]
