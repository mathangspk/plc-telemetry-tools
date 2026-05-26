import json
import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_loader import DataLoader
from ui.config_app import ConfigApp


def test_functional_flow():
    app = QApplication(sys.argv)

    print("1. Testing DataLoader...")
    loader = DataLoader("mock_pool_signals.json")
    metrics = loader.get_metrics()
    assert len(metrics) > 0, "Metrics should be loaded"
    signals = loader.get_signals_by_group("transA")
    assert len(signals) == 2, "Should find 2 transA signals"
    print("-> DataLoader passed.")

    print("2. Testing UI instantiation...")
    window = ConfigApp(loader)
    print("-> UI instantiation passed.")

    print("3. Testing ConfigTreeManager group creation...")
    window.tree_manager._create_group_node("transA")
    assert window.tree_manager.tree.topLevelItemCount() == 1
    group_item = window.tree_manager.tree.topLevelItem(0)
    assert group_item.text(1) == "transA"
    print("-> Group creation passed.")

    print("4. Testing ConfigTreeManager signal row addition...")
    window.tree_manager._create_signal_node(group_item, "transA")
    assert group_item.childCount() == 1
    print("-> Signal row addition passed.")

    print("5. Testing data extraction...")
    extracted = window.tree_manager.extract_configuration_data()
    assert len(extracted) == 1
    assert extracted[0]["name"] == "transA_current"
    print("-> Data extraction passed.")

    print("6. Testing Configuration Exporter...")
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        from core.exporter import export_config

        export_path = export_config("TestTrace", extracted, tmpdir)
        assert export_path is not None
        assert os.path.exists(export_path)
        with open(export_path, "r") as f:
            data = json.load(f)
            assert data["name"] == "TestTrace"
            assert data["signals"][0]["name"] == "transA_current"
    print("-> Exporter passed.")

    print("\nALL FUNCTIONAL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_functional_flow()
