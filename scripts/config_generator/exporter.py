import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def export_config(
    trace_name: str,
    signals_data: List[Dict[str, str]],
    export_dir: Union[str, Path] = ".",
) -> Optional[str]:
    """Exports the generated trace configuration to a JSON file.

    Args:
        trace_name (str): The name of the trace (used as the file name and internal config name).
        signals_data (List[Dict[str, str]]): The list of configured signal dictionaries (name, path, metric).
        export_dir (Union[str, Path], optional): The directory path where the JSON file will be saved. Defaults to ".".

    Returns:
        Optional[str]: The absolute path to the exported JSON file, or None if an error occurred.
    """
    if not trace_name or not signals_data:
        logger.warning("Trace name and signals data are required for export.")
        return None

    config: Dict[str, Any] = {"name": trace_name, "signals": signals_data}

    export_path: Path = Path(export_dir)

    try:
        export_path.mkdir(parents=True, exist_ok=True)
        file_path: Path = export_path / f"{trace_name}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully exported configuration to {file_path}")
        return str(file_path.absolute())

    except OSError as e:
        logger.error(
            f"OS error occurred while exporting configuration to {export_dir}: {e}"
        )
        return None
    except Exception as e:
        logger.error(f"Unexpected error exporting configuration to {export_dir}: {e}")
        return None
