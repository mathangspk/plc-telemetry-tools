import json
import os
import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication, QWidget

sys.path.append(
    str(Path(__file__).parent.parent.parent / "scripts" / "config_generator")
)

from core.data_loader import DataLoader
from ui.tree.tree_base import ConfigTreeManager

# Giả định hàm tính năng mới sẽ được triển khai ở đây
from ui.tree.tree_importer import reconstruct_tree_from_config


@pytest.fixture
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_pool_file(tmp_path):
    pool_data = {
        "metrics": ["M1", "M2"],
        "signals": [
            {"name": "transA_current", "path": "p1"},
            {"name": "transA_voltage", "path": "p2"},
            {"name": "Motor_temp", "path": "p3"},
        ],
    }
    file_path = tmp_path / "pool.json"
    file_path.write_text(json.dumps(pool_data))
    return file_path


@pytest.fixture
def exported_config_file(tmp_path):
    config_data = {
        "name": "TestTrace",
        "signals": [
            {"name": "transA_current", "path": "p1", "metric": "M1"},
            {"name": "Motor_temp", "path": "p3", "metric": "M2"},
        ],
    }
    file_path = tmp_path / "config.json"
    file_path.write_text(json.dumps(config_data))
    return file_path


def test_reconstruct_tree_success(app, mock_pool_file, exported_config_file):
    """Kiểm tra xem hệ thống có tự động nhóm (group) lại các tín hiệu đã export hay không."""
    loader = DataLoader(mock_pool_file)
    parent = QWidget()
    manager = ConfigTreeManager(parent, loader)

    # Thực thi hàm import (Feature mới)
    trace_name = reconstruct_tree_from_config(manager, exported_config_file)

    assert trace_name == "TestTrace"
    assert manager.tree.topLevelItemCount() == 2  # 2 groups: transA, Motor

    # Kiểm tra Group 1 (transA)
    group1 = manager.tree.topLevelItem(0)
    assert group1.text(1) == "transA"
    assert group1.childCount() == 1

    sig1 = group1.child(0)
    combo1 = manager.tree.itemWidget(sig1, 1)
    metric_combo1 = manager.tree.itemWidget(sig1, 2).layout().itemAt(0).widget()
    assert combo1.currentText() == "transA_current"
    assert metric_combo1.currentText() == "M1"

    # Kiểm tra Group 2 (Motor)
    group2 = manager.tree.topLevelItem(1)
    assert group2.text(1) == "Motor"
    assert group2.childCount() == 1
