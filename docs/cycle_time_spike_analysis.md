# Phân tích Chu kỳ Tăng CycleTime và Lỗi Giao Tiếp CAN Bus (PLC Telemetry)

Tài liệu này lưu trữ các khám phá kỹ thuật quan trọng về hệ thống điều khiển PLC và các lỗi truyền thông (CAN/TCP) được phát hiện trong quá trình Pair Programming.

---

## 1. Hiện Tượng CycleTime Tăng Vọt Mỗi 3 Phút (Trạng Thái Charging)

### Triệu chứng
Trong trạng thái `charging` (`cSystemStateCharging`), cứ khoảng 3 phút (`3 minutes`), chỉ số `cycleTime` của PLC lại nhảy vọt lên bất thường khoảng **55ms** (bình thường hoạt động ổn định ở mức **40ms**).

### Nguyên nhân gốc rễ (Root Cause)
* **File nguồn:** `services-eolus-heap-v8db.xml`
* **Thành phần chịu trách nhiệm:** POU **`ReportableChannelClientTCP`** (Function Block xử lý truyền thông TCP báo cáo trạng thái/telemetry).
* **Cấu hình định thời:** Hằng số `cCyclePeriod` được cấu hình cứng là 3 phút:
  ```pascal
  cCyclePeriod : t_time := TIME#3m0s0ms;
  ```
  Hằng số này được nạp vào timer `lCycleTimer` tại phương thức `initialize` của POU.

### Cơ chế hoạt động (Mechanism)
Cứ mỗi 3 phút khi `lCycleTimer` hết hạn (`Expired`), tiến trình thực hiện một đợt quét toàn bộ trạng thái tĩnh (Full State Dump) để gửi dữ liệu về máy chủ giám sát/Edge Device:
1. **Quét trạng thái:** Trong phương thức `operator`, vòng lặp `WHILE` chạy liên tục (với giới hạn `cCycleCount := 2` mỗi PLC cycle) để lấy các trạng thái đăng ký thông qua `lReportableStateManager.cycle()`.
2. **Tuần tự hóa JSON:** Phương thức `_reportState` tuần tự hóa (serialize) mô tả trạng thái thành chuỗi ký tự JSON thông qua `state^.describe()`. Việc chuyển đổi chuỗi JSON hàng loạt rất tốn tài nguyên xử lý của CPU PLC.
3. **TCP Burst Write:** Dữ liệu JSON tích lũy được đẩy thẳng ra cổng TCP bằng lệnh gọi socket `lClient.write()`.
4. **Tại sao xảy ra ở trạng thái Charging?** Ở trạng thái `charging` (`cSystemStateCharging`), cổng kết nối TCP Client được kích hoạt đầy đủ (`lEnabled := TRUE`), dữ liệu giám sát pin BMS cực kỳ dồn dập, dẫn đến lượng thông tin cần truyền tải qua socket lớn nhất, gây ra spike chu kỳ xử lý thêm khoảng **15ms**.

---

## 2. Lỗi "NO CAN MESS 80" trên bộ điều khiển ZAPI

### Triệu chứng
Bộ điều khiển ZAPI (Motor Controller ACE4) hiển thị mã lỗi hiển thị màn hình **"NO CAN MSG. 80"** (LED/MDI code: **67**) và bị mất kết nối CAN với PLC Master.

### Nguyên nhân
* **Đứt kết nối phần mềm (Software Timeout):** Node ID `80` tương ứng với bộ điều khiển *Multi-motor traction (slave 2) - Master MCU*. 
* Khi Edge Device gửi dồn dập các gói cấu hình dạng JSON dung lượng lớn xuống PLC thông qua socket TCP mà không có khoảng trễ (rate limit), CPU của PLC Master bị quá tải (>135ms) để xử lý dữ liệu TCP/IP và parse chuỗi JSON.
* Do CPU bị nghẽn (overload), PLC Master bỏ lỡ nhịp gửi hoặc nhận các gói tin kiểm tra sự tồn tại (Heartbeat) của CANopen (thường cấu hình Producer Time là `240ms`, Consumer Timeout là `375ms/380ms`). Khi vượt quá thời gian này, bộ điều khiển ZAPI ngay lập tức báo động lỗi mất kết nối CAN.

### Giải pháp khắc phục
1. **Rate Limiting trên Edge Device (`start_trace.py`):** Thêm độ trễ `time.sleep(0.05)` hoặc `0.1` (50ms - 100ms) vào vòng lặp gửi các lệnh cấu hình JSON xuống PLC. Điều này tạo ra "khoảng thở" cho CPU của PLC xử lý song song các tác vụ CAN Bus có độ ưu tiên cao mà không bị quá tải.
2. **Tăng Timeout trên PLC:** Tăng thông số Heartbeat Consumer Time lên cao hơn (ví dụ: `500ms`) để tăng biên độ chịu đựng trễ cho CAN Bus Task.

---

## 3. Hiện tượng Lỗi Vật Lý Mạng CAN (ErrorFrame)

### Triệu chứng
Trong log CAN raw (`can1.asc`) thu thập được tại đường dẫn `exports/CAN_message/CANBusDrive` trong trạng thái hoạt động (`Operational`), xuất hiện rất nhiều gói tin lỗi vật lý dạng `ErrorFrame` (ở các mốc thời gian chập chờn như 0.48s, 2.25s, 3.52s...).

### Nguyên nhân vật lý
* Gây ra bởi lỗi ở **Tầng vật lý (Physical Layer)** của mạng CAN:
  1. **Nhiễu điện từ (EMI):** Dây cáp tín hiệu CAN đi quá gần hoặc chạy chung máng cáp với cáp nguồn chịu dòng cao của Motor điện mà không được bọc chống nhiễu (Shielding/Grounding) đúng cách.
  2. **Thiếu/Sai điện trở đầu cuối:** Mạng CAN bus hoạt động ở tốc độ 500kbps yêu cầu hai điện trở đầu cuối `120 Ohm` song song ở hai đầu mút vật lý của đường truyền (tổng trở kháng đo được giữa chân CAN_H và CAN_L khi tắt nguồn phải đạt xấp xỉ `60 Ohm`).
  3. **Lỗi Bit vật lý:** Giắc cắm bị lỏng, oxy hóa, hoặc chập chờn tiếp xúc.

### Liên kết Nhân - Quả
* **Nguyên nhân:** Lỗi vật lý sinh ra các `ErrorFrame` làm mất mát các frame truyền nhận nhịp Heartbeat.
* **Hệ quả phần mềm:** PLC Master nhận diện sự cố và đẩy ra cổng Telemetry (port `49890`) các lỗi như `SlaveNotOp` (Slave không hoạt động), `MasterSlaveFail` (Lỗi giao tiếp Master/Slave) liên quan đến thiết bị `cWinchAngleB`.
