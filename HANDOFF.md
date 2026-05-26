# Project Handoff

## Summary of Changes
- Fixed a bug where importing a config file failed to restore the `Metric` selection, leaving all dropdowns at their default (`Metric0ms`).
- The bug was a side-effect of the previous UI layout refactoring where the Metric widget was detached from its layout container.
- Updated `test_import_config.py` to use a non-primary metric (`M2`) to strictly enforce that the test catches this specific bug in the future.

## Current System State
- The UI perfectly restores both Signals and Metrics when opening a JSON config file, matching the original state exactly.

## Verification & Testing
- Validated via `pytest tests/tdd/test_import_config.py` -> Passed.
- `tree_importer.py` directly targets the `QComboBox` instead of `layout().itemAt(0)`.

## Next Steps
- Lập trình viên load lại giao diện và mở file config một lần nữa.
