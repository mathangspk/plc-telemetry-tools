import json
import sys
from pathlib import Path

import pytest

sys.path.append(
    str(Path(__file__).parent.parent.parent / "scripts" / "config_generator")
)

from core.data_loader import DataLoader


@pytest.fixture
def mock_pool_file(tmp_path):
    pool_data = {
        "metrics": ["M1"],
        "signals": [
            {"name": "winchA_nodeState", "path": "p1"},
            {"name": "winchAngleA_nodeState", "path": "p2"},
            {"name": "winchAngleB_nodeState", "path": "p3"},
        ],
    }
    file_path = tmp_path / "pool.json"
    file_path.write_text(json.dumps(pool_data))
    return file_path


def test_get_signals_by_group_exact_match(mock_pool_file):
    """Kiểm tra lỗi lẫn lộn: Group 'winchA' không được chứa tín hiệu của 'winchAngleA'."""
    loader = DataLoader(mock_pool_file)

    signals_winchA = loader.get_signals_by_group("winchA")
    assert len(signals_winchA) == 1
    assert signals_winchA[0]["name"] == "winchA_nodeState"

    signals_winchAngleA = loader.get_signals_by_group("winchAngleA")
    assert len(signals_winchAngleA) == 1
    assert signals_winchAngleA[0]["name"] == "winchAngleA_nodeState"
