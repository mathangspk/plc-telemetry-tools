# Travel Drive C Motor Replacement Procedure
## Quy trình Thay thế Motor Di chuyển C (transC)

| Project | Isoloader MJ35 Gantry Crane Performance & Maintenance |
| :--- | :--- |
| **Component** | Travel Drive C Motor (`transC`) / Motor Di chuyển C |
| **Author** | Antigravity AI & Maintenance Team |
| **Target Audience** | Rob, Thang Ma & Maintenance Technicians |
| **Date** | June 24, 2026 |

---

## 1. Safety Prerequisites & Isolation / Yêu cầu An toàn & Cách ly
> [!IMPORTANT]
> **Safety First / An toàn là trên hết:**
> Ensure the machine is in a completely safe state before any mechanical or electrical intervention.
> Đảm bảo thiết bị ở trạng thái an toàn tuyệt đối trước khi thực hiện bất kỳ can thiệp cơ điện nào.

*   **Machine State / Trạng thái máy:** Ensure the Isoloader MJ35 Gantry Crane is in **Standby** state.
    *   *Đảm bảo máy đang ở trạng thái **Standby**.*
*   **Emergency Stop / Nút dừng khẩn cấp:** Press the **Emergency Stop** (E-Stop) button.
    *   *Nhấn nút **Emergency Stop**.*
*   **Electrical Isolation / Cách ly nguồn điện:** Disconnect the main battery and turn off the battery isolator switch (battery turn off).
    *   *Ngắt kết nối bình ắc quy (Disconnect battery) và tắt công tắc nguồn chính.*

---

## 2. Jacking up the Chassis & Wheel Removal / Kích gầm & Tháo bánh xe
*   **Wheel Chocking / Chặn bánh xe:** Place heavy-duty wooden chocks or blocks under the other wheels to prevent any unexpected movement, especially if the machine is parked on a slope.
    *   *Đặt các khối gỗ hoặc cục chặn bánh xe chuyên dụng dưới các bánh xe còn lại để chống trượt, đặc biệt là khi máy đỗ trên bề mặt nghiêng.*
*   **Jacking Up / Kích gầm:** Use a hydraulic bottle jack ("con đội") at the designated jacking point near the Travel Drive C location to lift the chassis.
    *   *Dùng con đội thủy lực kích gầm xe lên tại điểm kích quy định gần vị trí của Motor Di chuyển C (Xem hình minh họa bên dưới).*
*   **Wheel Removal / Tháo bánh xe:** Once the wheel is clear of the ground, loosen the wheel nuts and carefully remove the wheel.
    *   *Khi bánh xe được nhấc khỏi mặt đất, tháo các đai ốc bánh xe và đưa bánh xe ra ngoài.*

### Jacking Point Reference / Hình ảnh minh họa điểm kích gầm
![Jacking Point Illustration](gantry_crane_jacking_point.png)

---

## 3. Disconnecting Power & Control Lines / Tháo các đường cáp & Phanh thủy lực
Before unmounting the motor, carefully disconnect the following electrical and hydraulic connections:
Trước khi tháo motor, hãy ngắt các kết nối điện và đường ống thủy lực sau:

1.  **Main Power Cables / Cáp nguồn động lực:** Disconnect the high-current power cables supplying the motor. Mark them clearly to ensure correct phase reconnection.
    *   *Tháo các dây cáp nguồn động lực cung cấp cho motor. Đánh dấu rõ ràng để tránh đấu nhầm pha khi lắp lại.*
2.  **Speed Sensor Cable / Cảm biến tốc độ:** Unplug the speed encoder / sensor cable.
    *   *Tháo giắc cắm/dây tín hiệu của cảm biến tốc độ.*
3.  **Temperature Sensor Cable / Cảm biến nhiệt độ:** Unplug the motor temperature sensor cable.
    *   *Tháo dây tín hiệu của cảm biến nhiệt độ.*
4.  **Hydraulic Brake Line / Đường phanh thủy lực:** Disconnect the hydraulic line for the brake.
    *   *Tháo đường ống thắng thủy lực.*
    *   > [!WARNING]
        > **Fluid Spillage & Contamination / Rò rỉ dầu & Nhiễm bẩn:**
        > Plug the disconnected hydraulic ports immediately to prevent fluid loss and to keep dirt or dust from entering the hydraulic system.
        > *Bịt kín các đầu ống phanh ngay lập tức để tránh hao hụt dầu phanh và ngăn bụi bẩn lọt vào hệ thống thủy lực.*

---

## 4. Motor Replacement / Tháo lắp & Thay thế Motor
*   **Unmounting / Tháo motor cũ:** Support the weight of the motor, remove the mounting bolts securing the Travel Drive C motor to the gearbox/chassis, and slide it out.
    *   *Đỡ trọng lượng motor, tháo các bu-lông cố định Motor C với hộp số/khung xe, sau đó rút motor cũ ra.*
*   **Mounting New Motor / Lắp motor mới:** Clean the mounting surfaces, align the splines/shaft, and slide the new motor into place. Secure it with the mounting bolts to the specified torque.
    *   *Vệ sinh bề mặt lắp ráp, căn chỉnh trục then hoa và đưa motor mới vào đúng vị trí. Siết chặt các bu-lông cố định theo lực siết quy định.*
*   **Reconnection / Kết nối lại:** Reconnect the main power cables, speed sensor, temperature sensor, and hydraulic brake line.
    *   *Đấu nối lại cáp nguồn động lực, cảm biến tốc độ, cảm biến nhiệt độ và đường ống thắng thủy lực.*

---

## 5. Controller Calibration / Hiệu chuẩn Motor với Controller
> [!NOTE]
> **Responsible Person / Người thực hiện:** **Thang Ma**

After replacing the motor, the new motor must be calibrated with the Zapi controller (ACE4/FOC3) to ensure proper operation, correct scaling, and to avoid load imbalance.
Sau khi thay motor mới, bắt buộc phải tiến hành hiệu chuẩn (calibrate) motor với bộ điều khiển Zapi (ACE4/FOC3) để đảm bảo động cơ hoạt động đồng bộ, đúng tỷ lệ tốc độ và tránh hiện tượng lệch tải.

*   Reconnect the battery and turn on the main isolator.
    *   *Kết nối lại bình ắc quy và bật công tắc nguồn chính.*
*   Release the Emergency Stop.
    *   *Giải phóng nút Dừng khẩn cấp (Emergency Stop).*
*   Use the Zapi Handheld Console or diagnostic software to trigger the motor self-characterization / calibration routine.
    *   *Sử dụng tay cầm cài đặt Zapi hoặc phần mềm chẩn đoán để kích hoạt quy trình tự nhận diện/hiệu chuẩn động cơ.*
*   Verify that the feedback parameters (current, speed, torque) match the manufacturer specifications.
    *   *Xác minh các thông số phản hồi (dòng điện, tốc độ, mô-men xoắn) khớp với thông số kỹ thuật của nhà sản xuất.*

---

## 6. Hydraulic Brake System Bleeding / Xả gió hệ thống phanh
To ensure the hydraulic brake operates correctly, any air trapped in the line during disconnection must be bled.
Để đảm bảo phanh thủy lực hoạt động chính xác, bất kỳ bọt khí nào lọt vào đường ống trong quá trình tháo lắp đều phải được xả sạch.

*   **Safety Warning / Cảnh báo an toàn:**
    *   > [!CAUTION]
        > **Runaway Hazard / Nguy cơ xe tự trượt tự do:**
        > Before releasing the brake for bleeding, double-check that the wheels are securely chocked with wooden blocks. Opening the brakes on an incline without chocks will cause the machine to roll out of control.
        > *Trước khi mở thắng để xả gió, hãy kiểm tra kỹ lưỡng các bánh xe đã được chặn chắc chắn bằng các cục gỗ/chêm bánh xe chưa. Việc mở phanh trên mặt phẳng nghiêng mà không chặn bánh xe sẽ khiến thiết bị tự lăn tự do mất kiểm soát.*
*   **Bleeding Procedure / Quy trình xả gió:**
    *   Activate the manual brake release function from the controller/software to open the brake.
        *   *Kích hoạt chức năng mở thắng từ bộ điều khiển hoặc phần mềm để mở phanh.*
    *   Open the bleed valve on the brake caliper until a solid stream of hydraulic fluid flows out without air bubbles, then tighten the valve.
        *   *Mở van xả gió (bleed valve) trên cùm phanh cho đến khi dầu thủy lực chảy ra thành dòng liên tục, không còn bọt khí, sau đó siết chặt van lại.*
    *   Top up the hydraulic brake fluid reservoir if necessary.
        *   *Bổ sung thêm dầu phanh vào bình chứa nếu cần thiết.*

---

## 7. Reassembly & Lowering / Lắp lại bánh xe & Hạ kích
*   **Wheel Reinstallation / Lắp lại bánh xe:** Place the wheel back onto the hub and hand-tighten the wheel nuts.
    *   *Đưa bánh xe trở lại may-ơ và siết tạm các đai ốc bằng tay.*
*   **Lowering / Hạ con đội:** Carefully lower the hydraulic jack until the wheel touches the ground.
    *   *Hạ từ từ con đội thủy lực cho đến khi bánh xe tiếp đất.*
*   **Torquing Nuts / Siết chặt đai ốc:** Fully tighten the wheel nuts in a star pattern to the specified torque.
    *   *Siết chặt hoàn toàn các đai ốc bánh xe theo sơ đồ hình sao (đối xứng) đạt lực siết tiêu chuẩn.*
*   **Remove Chocks / Thu hồi chêm chặn:** Remove the wooden blocks/chocks from the wheels.
    *   *Tháo dỡ các tấm chêm chặn/khối gỗ dưới bánh xe.*

---

## 8. Verification & Test Run / Kiểm tra & Chạy thử
*   Perform a visual inspection to ensure no tools are left inside and all connections are tight.
    *   *Kiểm tra trực quan toàn bộ khu vực làm việc, đảm bảo không để quên dụng cụ và tất cả đầu nối đã được siết chặt.*
*   Perform a slow speed test drive (both forward and reverse) to check for abnormal noises or vibrations.
    *   *Tiến hành chạy thử tốc độ chậm (cả tiến và lùi) để kiểm tra xem có tiếng động lạ hay rung lắc bất thường nào không.*
*   Monitor telemetry data (current draw, RPM, motor temperature) for `transC` to confirm the load imbalance issue is resolved and the motor runs within normal ranges.
    *   *Theo dõi dữ liệu telemetry (dòng điện, RPM, nhiệt độ động cơ) của `transC` để đảm bảo lỗi lệch tải đã được khắc phục và động cơ chạy trong dải thông số bình thường.*
