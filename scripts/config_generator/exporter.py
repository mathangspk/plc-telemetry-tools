import json
import os

def export_config(trace_name, signals_data, export_dir="."):
    """
    trace_name: string
    signals_data: list of dicts like {"name": "...", "path": "...", "metric": "..."}
    """
    config = {
        "name": trace_name,
        "signals": signals_data
    }
    
    # Ensure export directory exists
    os.makedirs(export_dir, exist_ok=True)
    
    file_path = os.path.join(export_dir, f"{trace_name}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        
    return file_path
