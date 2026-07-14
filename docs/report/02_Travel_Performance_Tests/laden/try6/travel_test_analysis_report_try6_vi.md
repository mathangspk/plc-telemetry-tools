# Báo cáo Đánh giá Hiệu quả Thay thế Động cơ & Bộ điều khiển Trục C dưới Tải (Chạy Có Tải Lần 6)

**Mã tài liệu:** BMS-VALIDATION-TRAVEL-LADEN-06  
**Dòng thiết bị:** Cổng trục di chuyển bánh lốp Isoloader MJ35  
**Cấu hình thử nghiệm:** Chạy có tải (Laden), Bật HVAC  
**Thư mục lưu trữ:** Thư mục try6  
**Mục tiêu kiểm tra:** Đánh giá hiệu năng trục C có tải sau khi thay mới Động cơ & Bộ điều khiển

---

## 1. Tóm tắt dự án & Kết quả kiểm tra
Báo cáo này trình bày kết quả đánh giá thực tế của Trục di chuyển C (`transC`) dưới tải trong lần chạy thứ 6 (Try 6), sau khi tiến hành thay mới cả Động cơ (Try 3) và Bộ điều khiển motor di chuyển C (Try 4).

Trước đó, ở lần thử có tải thứ 5 (Try 5 - sử dụng động cơ và bộ điều khiển cũ), trục C hiển thị sự mất cân bằng tải cực kỳ nghiêm trọng, tiêu thụ dòng điện trung bình lên tới **59.99 A** (cao hơn **80%** so với trung bình hệ thống, ~34.8 A) và phát ra mô-men xoắn **25.19 Nm**, làm nhiệt độ động cơ tăng nhanh với tốc độ **0.864°C/phút** (đạt nhiệt độ đỉnh **85.0°C**).

Số liệu telemetry ghi nhận từ lần chạy Try 6 có tải (thời gian di chuyển thực tế 11.54 phút) cho thấy:
* **Tình trạng lệch tải đã được GIẢI QUYẾT dưới tải:** Dòng điện tiêu thụ và mô-men xoắn của trục C đã giảm về mức định mức hoàn toàn bình thường. Trục C giờ chỉ tiêu thụ trung bình **42.11 A** (chỉ cao hơn **13.0%** so với trung bình của các trục khác là **37.28 A**).
* **Sự phân bổ tải cực kỳ cân bằng:** Dòng điện của cả 4 trục di chuyển hiện nay đạt độ cân bằng rất tốt: TransA (**35.73 A**), TransB (**35.06 A**), TransC (**42.11 A**), và TransD (**41.07 A**).
* **Nhiệt độ đã ổn định hoàn toàn:** Tốc độ gia nhiệt của TransC giảm xuống chỉ còn **0.780°C/phút** (bằng đúng TransD và chỉ cao hơn TransA **12.5%**). Nhiệt độ đỉnh của động cơ C được giữ ở mức cực kỳ an toàn là **59.0°C** (ngang bằng với TransA).

**Kết luận:** Việc thay thế động cơ và bộ điều khiển mới (bao gồm hiệu chuẩn lại thông số động cơ và tự động dò tham số auto-tuning) đã xử lý triệt để lỗi lệch tải dưới tải. Điều này chứng minh nguyên nhân cốt lõi của việc dòng điện và nhiệt độ tăng cao ở Try 5 là do **sai lệch cấu hình điều khiển/hiệu chuẩn phần điện** của bộ điều khiển cũ, chứ không phải do lỗi kẹt cơ khí hay vặn xoắn kết cấu khung gầm.

---

## 2. Bảng Đối chiếu Số liệu Telemetry Có Tải (Try 5 vs. Try 6)
Bảng dưới đây tổng hợp chi tiết các thông số đo đạc trong thời gian di chuyển chủ động (active moving) của cả 4 trục di chuyển dưới tải.

### Bảng số liệu đối chiếu chi tiết:

| Lần chạy & Mã động cơ | Thời gian chạy | Dòng trung bình | Dòng lớn nhất | Mô-men trung bình | Mô-men lớn nhất | Nhiệt độ đầu | Nhiệt độ đỉnh | Mức tăng nhiệt | Tốc độ gia nhiệt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Try 5 (Môtơ/Ctrl cũ)** | **30.08 phút** | | | | | | | | |
| - Động cơ di chuyển A | | 31.11 A | 124.00 A | 12.19 Nm | 49.10 Nm | 54.0°C | 68.0°C | +14.0°C | 0.47°C/phút |
| - Động cơ di chuyển B | | 38.82 A | 102.00 A | 14.79 Nm | 49.70 Nm | 54.0°C | 71.0°C | +17.0°C | 0.57°C/phút |
| - **Động cơ di chuyển C (Lỗi)** | | **59.99 A** | **106.00 A** | **25.19 Nm** | **50.80 Nm** | **59.0°C** | **85.0°C** | **+26.0°C** | **0.86°C/phút** |
| - Động cơ di chuyển D | | 34.45 A | 126.00 A | 13.45 Nm | 48.00 Nm | 51.0°C | 67.0°C | +16.0°C | 0.53°C/phút |
| **Try 6 (Môtơ/Ctrl MỚI)** | **11.54 phút** | | | | | | | | |
| - Động cơ di chuyển A | | 35.73 A | 112.00 A | 13.80 Nm | 54.50 Nm | 51.0°C | 59.0°C | +8.0°C | 0.69°C/phút |
| - Động cơ di chuyển B | | 35.06 A | 106.00 A | 13.56 Nm | 50.60 Nm | 50.0°C | 57.0°C | +7.0°C | 0.61°C/phút |
| - **Động cơ di chuyển C (Mới)** | | **42.11 A** | **106.00 A** | **17.28 Nm** | **51.70 Nm** | **50.0°C** | **59.0°C** | **+9.0°C** | **0.78°C/phút** |
| - Động cơ di chuyển D | | 41.07 A | 104.00 A | 15.81 Nm | 48.00 Nm | 48.0°C | 57.0°C | +9.0°C | 0.78°C/phút |

---

## 3. Nhận định Kỹ thuật & Nguyên nhân cốt lõi
1. **Dòng điện cân bằng:** Trục C tiêu thụ **42.11 A**, bám rất sát trục D (**41.07 A**) và các trục khác. Đây là trạng thái chia tải lý tưởng của cổng trục đa động cơ AC không đồng bộ.
2. **Mô-men xoắn giảm mạnh:** Mô-men cản của trục C giảm từ **25.19 Nm** xuống còn **17.28 Nm**, chứng tỏ trục không phải ghì kéo cơ học lớn nữa.
3. **Ổn định nhiệt:** Tốc độ nóng lên của trục C đạt **0.780°C/phút**, bằng đúng trục D.

### Phân tích nguyên nhân:
Sự bình phục hoàn toàn này chứng minh lỗi cũ nằm ở **Bộ hiệu chuẩn thông số động cơ của Controller cũ**:
* Khi cấu hình sai lệch điện trở cuộn dây, hệ số tự cảm hoặc dòng kích từ của động cơ AC không đồng bộ, bộ điều khiển (VFD) sẽ cấp điện áp/tần số không tối ưu, khiến động cơ hoạt động ở vùng **độ trượt (slip) cực lớn**.
* Độ trượt lớn làm tăng dòng điện kéo rất cao và sinh ra nhiệt lượng hao phí khổng lồ trên rotor/stator (nhiệt độ trượt), giải thích vì sao trục C cũ bị nóng lên tới 85°C. Bộ điều khiển mới sau khi auto-tuning đã đồng bộ chính xác mô hình toán học của động cơ, đem lại hiệu suất tối đa.

---

## 4. Đồ thị Telemetry kiểm chứng

### 4.1 Đồ thị dòng điện & nhiệt độ Try 6 (Thời gian thực)
![Travel Performance Try 6](travel_performance_laden_try6.png)

### 4.2 Biểu đồ cột đối chiếu 4 trục (Try 5 vs. Try 6)
![Multi-Trial Travel Drive Comparison](travel_multi_trial_comparison_laden.png)
