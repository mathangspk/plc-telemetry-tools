import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def _get_unique_path(base_path: Path, name: str) -> Path:
    """Finds lowest unused suffix if file exists."""
    if not (base_path / f"{name}.json").exists():
        return base_path / f"{name}.json"
    idx = 1
    while (base_path / f"{name}_{idx:02d}.json").exists():
        idx += 1
    return base_path / f"{name}_{idx:02d}.json"


def export_config(
    trace_name: str,
    signals_data: List[Dict[str, str]],
    export_dir: Union[str, Path] = ".",
    overwrite: bool = False,
) -> Optional[str]:
    """Exports trace configuration to JSON file."""
    if not trace_name or not signals_data:
        return None
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)

    file_path = export_path / f"{trace_name}.json"
    if not overwrite:
        file_path = _get_unique_path(export_path, trace_name)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                {"name": trace_name, "signals": signals_data},
                f,
                indent=2,
                ensure_ascii=False,
            )
        logger.info(f"Exported to {file_path}")
        return str(file_path.absolute())
    except Exception as e:
        logger.error(f"Error exporting config: {e}")
        return None
