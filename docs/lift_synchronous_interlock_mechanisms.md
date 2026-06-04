# Lift Synchronous Interlock Mechanisms

## Tổng quan
Cả hai khối `lLiftABSynchronousInterlock` và `lLiftSynchronousInterlock` đều sử dụng chung một khối chức năng (Function Block) là `SynchronousInterlock`. Đây là các module lõi tạo nên **hệ thống đồng bộ đa cấp (cascaded synchronization)** để giữ cho cả 4 góc của khung cẩu (A, B, C, D) luôn phẳng/ngang bằng nhau trong quá trình nâng hạ.

---

## 1. Cơ chế chung của khối `SynchronousInterlock`
Khối này nhận 2 tín hiệu đầu vào: `InputA` và `InputB`.
1. Tính toán độ lệch: `Delta = InputA - InputB`.
2. Tính trung bình: `Average = (InputA + InputB) / 2`.
3. Dựa trên `Delta`, nó dùng một bộ chuyển đổi hình thang (`TransformIsoscelesTrapezoid`) để xuất ra hệ số `Scaling`.
   - Nếu `Delta` nhỏ (gần 0), `Scaling` = 1.0 (cho phép chạy tốc độ tối đa).
   - Nếu `Delta` tăng lên (2 bên lệch nhau quá mức cài đặt), `Scaling` sẽ bị ép giảm dần về 0.
4. Nó tác động lệnh hãm tốc độ (`Scaling` và `Threshold`) xuống 2 biến điều khiển thông qua cấu hình nghịch dấu (`SignA = 1.0`, `SignB = -1.0`). Bên nào đang chạy nhanh hơn/đi xa hơn sẽ bị kìm tốc độ lại để chờ bên kia đuổi kịp.

---

## 2. `lLiftABSynchronousInterlock` (Đồng bộ cục bộ cụm Trái/Phải hoặc Trước/Sau)
- **Chức năng:** Giữ cân bằng giữa tời A và tời B. (Tương tự, có khối `lLiftCDSynchronousInterlock` cho cụm C và D).
- **InputA:** Vị trí hiện tại của tời A (`WinchAngleA.Position`).
- **InputB:** Vị trí hiện tại của tời B (`WinchAngleB.Position`).
- **Tác động (Client):** Kết nối trực tiếp vào bộ Interlock của `MovementA` và `MovementB`.
- **Hoạt động:** Nếu tời A chạy nhanh hơn B (chiều cao lệch nhau), hệ thống tính ra Delta. Khối này sẽ bóp tốc độ của A lại (thông qua `Scaling`) để A chậm lại và B có thể bắt kịp, giữ cho cạnh AB luôn song song với mặt đất.

---

## 3. `lLiftSynchronousInterlock` (Đồng bộ tổng thể Toàn Hệ Thống)
- **Chức năng:** Giữ cân bằng giữa cụm AB và cụm CD của hệ thống Lift.
- **InputA:** Nhận giá trị `Average` (chiều cao trung bình) từ khối `lLiftABSynchronousInterlock`.
- **InputB:** Nhận giá trị `Average` (chiều cao trung bình) từ khối `lLiftCDSynchronousInterlock`.
- **Tác động (Client):**
  - `ClientA` tác động đồng thời vào Interlock của cả A và B.
  - `ClientB` tác động đồng thời vào Interlock của cả C và D.
- **Hoạt động:** Nếu toàn bộ cụm AB đang nâng nhanh hơn cụm CD, khối này sẽ bóp tốc độ của cả cụm AB lại (can thiệp đồng thời vào cả tời A và tời B) để cụm CD đuổi kịp, từ đó giữ cho mặt phẳng của toàn bộ cụm nâng 4 góc được cân bằng.

---

## Kết luận về Kiến trúc
Hệ thống sử dụng thuật toán phân chia nhiệm vụ đồng bộ rất rõ ràng theo mô hình phân cấp:
- **Cấp 1 (Local):** `LiftABSync` lo giữ thăng bằng nội bộ trục AB; `LiftCDSync` lo giữ thăng bằng nội bộ trục CD.
- **Cấp 2 (Global):** `LiftSync` lo giữ thăng bằng lớn giữa cụm AB và cụm CD để đảm bảo mặt phẳng của toàn bộ thiết bị nâng (spreader) được cân bằng tuyệt đối.
