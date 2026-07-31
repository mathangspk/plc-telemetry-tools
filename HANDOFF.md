# Handoff Report - Cabin Control QC Checklist Integration

## Summary of Changes
- Updated QC Function Test Check Sheet file: `C:\local\Apollo4\docs\qc_check_sheet\MJG-QM-WI-03-Apollo-F01-Rev.01-Function test.docx`.
- **Update 1: Added Cabin Control System Section** (Row 24 of Table 0). Added 5 standard dual-language QC inspection items covering Touchscreen HMI, Joysticks/Switches, HVAC System, Interior Lighting/Wipers, and E-Stop/Safety Interlocks.
- **Update 2: Updated CANBUS Master Logic & Multi-Controller Architecture** (Rows 2 to 5 under CANBUS Master Section):
  1. **Check Cabin HMI Login & Single Mode** (*Kiểm tra đăng nhập HMI Cabin & Chế độ Single*): Verifies Key-ON Cabin HMI login (`operator` / `123456`) and Single mode behavior for HMI and Radio Remote.
  2. **Check Dual Controller Master/Slave Mode** (*Kiểm tra chế độ Dual Controller Master/Slave*): Verifies Master/Slave assignment when both HMI Display and Radio Remote are powered on.
  3. **Check Master <--> Slave Handoff Mechanism** (*Kiểm tra cơ chế chuyển quyền điều khiển Master <--> Slave*): Tests control rights request and transfer between Master and Slave.
  4. **Check Pre-operational & Operational State Transition** (*Kiểm tra chuyển trạng thái Pre-operational & Operational*): Confirms Pre-operational state on active Master controller and 3-second Start button press for Operational state transition.
- Preserved 100% of existing document formatting, font sizes, colors (Red headers `#FF0000`, Blue Italic descriptions `#0000FF`), Pass/Fail check boxes, and Notes columns.

## Current System State
- File `MJG-QM-WI-03-Apollo-F01-Rev.01-Function test.docx` is updated and validated with total row count of 84.
- Python automation scripts successfully executed.

## Verification & Testing
- Verified docx XML node structure.
- Confirmed row positions, text styles, and cell formatting match existing document standards.

## Next Steps
- Deliver updated check sheet to QC & Commissioning team for pre-shipment testing.
