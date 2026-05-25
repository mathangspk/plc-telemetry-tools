import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

def export_config(trace_name: str, signals_data: List[Dict[str, str]], export_dir: str = ".") -> Optional[str]:
    """
    Exports the generated trace configuration to a JSON file.
    
    Args:
        trace_name: The name of the trace (used as the file name and internal config name).
        signals_data: The list of configured signal dictionaries (name, path, metric).
        export_dir: The directory path where the JSON file will be saved.
        
    Returns:
        The absolute path to the exported JSON file, or None if an error occurred.
    """
    config: Dict[str, Any] = {
        "name": trace_name,
        "signals": signals_data
    }
    
    export_path = Path(export_dir)
    
    try:
        export_path.mkdir(parents=True, exist_ok=True)
        file_path = export_path / f"{trace_name}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully exported configuration to {file_path}")
        return str(file_path.absolute())
        
    except Exception as e:
        logger.error(f"Failed to export configuration to {export_dir}: {e}")
        return None
