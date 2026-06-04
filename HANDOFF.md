# Project Handoff

## Summary of Changes
- **Nghiên cứu & Chẩn đoán Spike CycleTime 3 phút:** Đã phát hiện chính xác nguyên nhân chu kỳ 3 phút tăng cycleTime vọt lên ~55ms trong trạng thái `charging`. Vấn đề nằm ở POU `ReportableChannelClientTCP` với timer chu kỳ `cCyclePeriod := TIME#3m0s0ms` thực hiện Full State Dump qua TCP socket.
- **Tài liệu hóa hệ thống:** Tạo tệp tài liệu bộ nhớ dự án toàn diện tại [cycle_time_spike_analysis.md](file:///c:/local/opencode/codesys/docs/cycle_time_spike_analysis.md) tổng hợp toàn bộ các phát hiện về mạng CAN, nhiễu vật lý, lỗi quá tải CPU dẫn đến sập Heartbeat ảo (ZAPI "NO CAN MESS 80") và spike TCP Client.
- **CAN Interface for Apollo 4:** Đã tạo tệp tài liệu `Apollo 4.xlsx` (dựa trên `MJConnect_CANInterfaceV6.xlsx`) để đặc tả dữ liệu CAN interface riêng cho BMSA và BMSB (tách thành 2 sheet riêng biệt). Đã đính chính lại mapping: Nhiệt độ BMS là kiểu USINT (1 byte), và đã xác nhận+cập nhật Node ID (BMSA=2, BMSB=3) cùng Start/End Address (dải COB-ID) chuẩn xác dựa trên file cấu hình XML của dự án.
- **Phân tích Cơ chế Đồng bộ Nâng hạ (Lift Synchronous Interlock):** Đã tài liệu hóa cấu trúc đồng bộ đa cấp (cascaded synchronization) giữa các cụm tời (A, B, C, D) bao gồm `lLiftABSynchronousInterlock`, `lLiftCDSynchronousInterlock`, và `lLiftSynchronousInterlock` vào [lift_synchronous_interlock_mechanisms.md](file:///c:/local/opencode/codesys/docs/lift_synchronous_interlock_mechanisms.md).

## Current System State
- **Telemetry & Diagnostics:** Toàn bộ thông tin phân tích và các khuyến nghị tối ưu cấu hình (Rate Limiting 50-100ms trên Edge Device, điện trở đầu cuối CAN 60 Ohm, bọc chống nhiễu cáp nguồn) được lưu trữ đầy đủ trong thư mục `docs/`.
- **Hệ thống điều khiển:** Đang hoạt động bình thường theo logic hiện tại.

## Verification & Testing
- Đã xác thực tĩnh và phân tích logic luồng chạy của POU `ReportableChannelClientTCP` và POU `BMSAB` từ codebase XML (`services-eolus-heap-v8db.xml` và `primary - eolus - v2d.xml`).

## Next Steps
- Lập trình viên xem xét cấu hình lại độ ưu tiên Task Telemetry/Network thấp hơn Task điều khiển chính trong CODESYS để tránh spike CycleTime ảnh hưởng tới các chu kỳ điều khiển thời gian thực.
- Rà soát kiểm tra điện trở đầu cuối CAN bus (đạt 60 Ohm) và bọc chống nhiễu cáp nguồn motor để triệt tiêu lỗi `ErrorFrame` chập chờn.
- Cập nhật logic khởi tạo cho các encoder (winchAngle và steerAngle) trong `CANOpenMasterDriveApollo` và `CANOpenMasterDriveBuild`: Gán `lStartSystemStateScope := cSystemStatePreparing;` để các encoder này được đưa lên trạng thái OPERATIONAL sớm từ bước Preparing mà không ảnh hưởng đến các thành phần CANOpen khác.
