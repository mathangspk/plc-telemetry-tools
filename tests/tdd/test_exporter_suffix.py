import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Cấu hình đường dẫn để có thể import từ src
sys.path.append(
    str(Path(__file__).parent.parent.parent / "scripts" / "config_generator")
)

from core.exporter import export_config


@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as d:
        yield d


@pytest.fixture
def mock_signals():
    return [{"name": "signal1", "path": "path1", "metric": "Metric50ms"}]


def test_export_new_file(temp_dir, mock_signals):
    """Trường hợp 1: File chưa tồn tại. Export bình thường không hậu tố."""
    result_path = export_config("TraceA", mock_signals, temp_dir, overwrite=False)

    assert result_path is not None
    assert Path(result_path).name == "TraceA.json"
    assert Path(result_path).exists()


def test_export_overwrite(temp_dir, mock_signals):
    """Trường hợp 2: File đã tồn tại và cho phép overwrite (ghi đè)."""
    # Lần 1: Tạo file gốc
    first_path = export_config("TraceB", mock_signals, temp_dir, overwrite=False)

    # Lần 2: Ghi đè
    second_path = export_config("TraceB", mock_signals, temp_dir, overwrite=True)

    assert second_path == first_path
    assert Path(second_path).name == "TraceB.json"


def test_export_auto_suffix(temp_dir, mock_signals):
    """Trường hợp 3: File đã tồn tại, KHÔNG cho phép ghi đè -> Tự động sinh hậu tố _01, _02."""
    # Lần 1: TraceC.json
    export_config("TraceC", mock_signals, temp_dir, overwrite=False)

    # Lần 2: Không ghi đè -> TraceC_01.json
    path_01 = export_config("TraceC", mock_signals, temp_dir, overwrite=False)
    assert Path(path_01).name == "TraceC_01.json"
    assert Path(path_01).exists()

    # Lần 3: Không ghi đè -> TraceC_02.json
    path_02 = export_config("TraceC", mock_signals, temp_dir, overwrite=False)
    assert Path(path_02).name == "TraceC_02.json"
    assert Path(path_02).exists()


def test_export_with_existing_gaps(temp_dir, mock_signals):
    """Trường hợp 4 (Edge-case): Đã có TraceD.json và TraceD_02.json, hệ thống sẽ sinh ra TraceD_01 hay TraceD_03?"""
    # Theo quy tắc thông thường, nó nên quét từ 1 trở đi và điền vào chỗ trống đầu tiên,
    # hoặc lấy số lớn nhất + 1. Trong test này, giả định ta tìm số nhỏ nhất còn trống (TraceD_01).

    # Tạo file thủ công
    base_path = Path(temp_dir) / "TraceD.json"
    base_path.write_text("{}")

    gap_path = Path(temp_dir) / "TraceD_02.json"
    gap_path.write_text("{}")

    # Export
    new_path = export_config("TraceD", mock_signals, temp_dir, overwrite=False)
    assert Path(new_path).name == "TraceD_01.json"
