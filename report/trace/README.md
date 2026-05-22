# 📡 PLC Telemetry Trace & Verification Guide

Thư mục này là trung tâm điều khiển và giám sát toàn bộ các tín hiệu Telemetry trên PLC. Tại đây, cấu trúc cấu hình đã được tối ưu hóa cho phép gán riêng từng metric (tần số lấy mẫu) cho mỗi tín hiệu, đồng thời phân tách dữ liệu thành 2 nhóm trạng thái: hoạt động tốt (`pass_active`) và lỗi (`fail`).

---

## 📁 Cấu Trúc Thư Mục

```text
report/trace/
├── pass_active/         # 29 file JSON chỉ chứa các tín hiệu hoạt động tốt (PASS_ACTIVE)
├── fail/                # 29 file JSON chứa các tín hiệu bị lỗi hoặc không phản hồi dữ liệu (FAIL)
├── start_trace.py       # Script đăng ký (register) tín hiệu lên PLC
├── stop_trace.py        # Script hủy đăng ký (unregister) tín hiệu khỏi PLC
├── verify_with_clean_workflow.py  # Script kiểm thử tự động & khép kín toàn diện
└── README.md            # Tài liệu hướng dẫn sử dụng (tệp này)
```

---

## ⚙️ Cấu Hình Metric Cho Từng Tín Hiệu (Per-Signal Metric)

Mỗi tín hiệu (`signal`) trong mảng `"signals"` của file JSON đều được gán một trường `"metric"` riêng. Định dạng chuẩn như sau:

```json
{
  "name": "transA_motorTemp",
  "path": "System/CANBusDrive/cTransA/MotorTemp",
  "metric": "Metric250ms"
}
```

> [!TIP]
> Bạn có thể chủ động sửa đổi giá trị `"metric"` cho bất kỳ tín hiệu nào thành các tần số quét khác được PLC hỗ trợ (ví dụ: `"Metric100ms"`, `"Metric1s"`, `"Metric5s"`, `"Metric10s"`). Các script vận hành sẽ tự động nhận diện và đăng ký chính xác vào container tương ứng.

---

## 🚀 Cách Thức Chạy Vận Hành Các Trace

Các script đều hỗ trợ chạy từ thư mục gốc của dự án hoặc chạy trực tiếp từ bên trong thư mục này. Khuyến nghị chạy từ thư mục gốc của workspace (`c:\local\opencode\codesys`).

### 1. Kiểm tra thử nghiệm (Dry-Run)
Trước khi đăng ký trực tiếp lên PLC, hãy dùng tham số `--dry-run` để kiểm tra cú pháp lệnh sẽ gửi đi.

```powershell
# Kiểm tra dry-run đăng ký cấu hình master
python report/trace/start_trace.py TraccDriveTemperatures --dry-run

# Kiểm tra dry-run đăng ký cấu hình đã được lọc hoạt động tốt (pass_active)
python report/trace/start_trace.py TraccDriveTemperatures --trace-dir report/trace/pass_active --dry-run
```

---

### 2. Đăng ký Live Telemetry lên PLC (`start_trace.py`)
Khi kết nối trực tiếp với PLC, script sẽ đăng ký tuần tự tất cả các tín hiệu được cấu hình trong file JSON.

```powershell
# Đăng ký các tín hiệu hoạt động tốt của trace TraccDriveTemperatures lên PLC mặc định (10.2.3.4)
python report/trace/start_trace.py TraccDriveTemperatures --trace-dir report/trace/pass_active

# Chỉ định IP PLC cụ thể bằng tham số -H
python report/trace/start_trace.py TraccDriveTemperatures --trace-dir report/trace/pass_active -H 10.2.3.99
```

---

### 3. Hủy đăng ký Telemetry trên PLC (`stop_trace.py`)
Hủy đăng ký để giải phóng tài nguyên trên PLC sau khi thu thập xong dữ liệu.

```powershell
# Hủy đăng ký các tín hiệu hoạt động tốt của trace TraccDriveTemperatures
python report/trace/stop_trace.py TraccDriveTemperatures --trace-dir report/trace/pass_active

# Chỉ định IP PLC cụ thể
python report/trace/stop_trace.py TraccDriveTemperatures --trace-dir report/trace/pass_active -H 10.2.3.99
```

---

### 4. Kiểm Thử Trọn Gói Tự Động (`verify_with_clean_workflow.py`)
Đây là script mạnh mẽ và an toàn nhất, tự động thực hiện **5 bước chuẩn hóa khép kín** đối với một trace cụ thể:
1. **Pre-Check & Clear**: Kiểm tra xem có telemetry nào đang chạy không, nếu có sẽ phát lệnh `clear` để dọn sạch.
2. **Register**: Đăng ký các tín hiệu trong cấu hình JSON lên PLC.
3. **Describe**: Truy vấn cổng Describe (49880) để xác nhận danh sách thành viên đăng ký thành công.
4. **Emit**: Lắng nghe cổng Emit (49890) trong 5 giây để thu thập dữ liệu đẩy ra thực tế.
5. **Stop & Clear**: Phát lệnh `clear` để đưa PLC về trạng thái hoàn toàn tĩnh lặng và sạch sẽ.
6. **Báo cáo**: Kết xuất một file báo cáo Markdown độc lập tại thư mục `report/trace/test_results/`.

```powershell
# Chạy quy trình kiểm thử sạch cho trace đã lọc (pass_active)
python report/trace/verify_with_clean_workflow.py -t TraccDriveTemperatures --trace-dir report/trace/pass_active

# Chạy quy trình kiểm thử sạch cho trace lỗi (fail) để chẩn đoán
python report/trace/verify_with_clean_workflow.py -t TraccDriveTemperatures --trace-dir report/trace/fail

# Chạy kiểm thử trên PLC với IP tùy chỉnh và tăng thời gian nghe dòng Emit thành 10 giây
python report/trace/verify_with_clean_workflow.py -t TraccDriveTemperatures --trace-dir report/trace/pass_active -H 10.2.3.99 -d 10
```

Báo cáo chi tiết sau khi chạy sẽ được lưu dưới dạng:
📂 `report/trace/test_results/<TraceName>_focused_report.md`

---

## 🛠️ Danh Sách Tham Số Hỗ Trợ

| Tham số | Ý nghĩa | Mặc định |
| :--- | :--- | :--- |
| `-t`, `--trace` | Tên của trace cần chạy (không kèm đuôi `.json`) | `cTransTest` |
| `--trace-dir` | Đường dẫn tới thư mục chứa các file JSON | `exports/trace-config/traces/` |
| `-H`, `--host` | Địa chỉ IP của PLC | `10.2.3.4` |
| `-P`, `--port` | Cổng RW để gửi lệnh lên PLC (chỉ áp dụng start/stop) | `49870` |
| `-d`, `--duration`| Thời gian nghe và bắt luồng Emit (giây, chỉ verify_with_clean_workflow) | `5.0` |
| `--dry-run` | Chỉ in ra danh sách lệnh giả lập, không kết nối PLC | *Không có* |

---

> [!IMPORTANT]
> **Quy tắc an toàn**: Luôn chạy `stop_trace.py` hoặc sử dụng `verify_with_clean_workflow.py` để đảm bảo PLC không bị quá tải do dòng dữ liệu telemetry đẩy ra liên tục khi không sử dụng.
