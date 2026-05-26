import json
import os
import subprocess
import sys
import threading
import tkinter as tk
import urllib.error
import urllib.request
from datetime import datetime
from tkinter import filedialog, messagebox

EDGE_DEVICE_IP = "10.2.4.10"
EDGE_DEVICE_PORT = 5000


class TraceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trace Telemetry Collector")
        self.root.geometry("500x380")

        # Variables
        self.json_file_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()
        self.current_remote_file = None
        self.is_recording = False

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        pad = {"padx": 10, "pady": 5}

        # --- File Selection ---
        tk.Label(self.root, text="1. Chọn file Trace JSON:").pack(anchor="w", **pad)
        frame1 = tk.Frame(self.root)
        frame1.pack(fill="x", **pad)
        tk.Entry(frame1, textvariable=self.json_file_path, state="readonly").pack(
            side="left", fill="x", expand=True
        )
        tk.Button(frame1, text="Browse", command=self.browse_json).pack(
            side="right", padx=5
        )

        # --- Folder Selection ---
        tk.Label(self.root, text="2. Chọn thư mục lưu kết quả:").pack(anchor="w", **pad)
        frame2 = tk.Frame(self.root)
        frame2.pack(fill="x", **pad)
        tk.Entry(frame2, textvariable=self.output_dir_path, state="readonly").pack(
            side="left", fill="x", expand=True
        )
        tk.Button(frame2, text="Browse", command=self.browse_output).pack(
            side="right", padx=5
        )

        # --- Status ---
        self.lbl_status = tk.Label(self.root, text="Status: Ready", fg="blue")
        self.lbl_status.pack(pady=10)

        # --- Action Buttons ---
        frame3 = tk.Frame(self.root)
        frame3.pack(fill="x", pady=10)

        self.btn_start = tk.Button(
            frame3,
            text="Start Data Collection",
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.start_collection,
        )
        self.btn_start.pack(side="left", expand=True, fill="x", padx=10)

        self.btn_stop = tk.Button(
            frame3,
            text="Stop Data Collection",
            bg="red",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.stop_collection,
            state=tk.DISABLED,
        )
        self.btn_stop.pack(side="right", expand=True, fill="x", padx=10)

        # --- Open Folder Button ---
        frame4 = tk.Frame(self.root)
        frame4.pack(fill="x", pady=10)
        tk.Button(
            frame4,
            text="Mở thư mục kết quả (Folder)",
            font=("Arial", 10),
            command=self.open_output_folder,
        ).pack(expand=True, fill="x", padx=50)

    def browse_json(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file JSON config", filetypes=[("JSON Files", "*.json")]
        )
        if file_path:
            self.json_file_path.set(file_path)

    def browse_output(self):
        dir_path = filedialog.askdirectory(title="Chọn thư mục lưu dữ liệu")
        if dir_path:
            self.output_dir_path.set(dir_path)

    def open_output_folder(self):
        dir_path = self.output_dir_path.get()
        if dir_path and os.path.exists(dir_path):
            os.startfile(dir_path)
        else:
            messagebox.showinfo("Info", "Thư mục chưa được chọn hoặc không tồn tại!")

    def log(self, msg, color="black"):
        self.lbl_status.config(text=f"Status: {msg}", fg=color)
        self.root.update()

    def start_collection(self):
        if not self.json_file_path.get():
            messagebox.showwarning("Warning", "Vui lòng chọn file Trace JSON!")
            return
        if not self.output_dir_path.get():
            messagebox.showwarning("Warning", "Vui lòng chọn thư mục lưu!")
            return

        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.is_recording = True

        # Chạy luồng nền tránh treo UI
        threading.Thread(target=self._start_task, daemon=True).start()

    def _start_task(self):
        json_path = self.json_file_path.get()
        trace_dir = os.path.dirname(json_path)
        trace_name = os.path.splitext(os.path.basename(json_path))[0]

        # 1. Chạy start_trace.py
        self.log("Đang cấu hình PLC (start_trace)...", "blue")
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        script_dir = os.path.join(base_dir, "report", "trace")
        start_script = os.path.join(script_dir, "start_trace.py")

        if os.path.exists(start_script):
            subprocess.run(
                ["python", start_script, "--trace-dir", trace_dir, trace_name],
                shell=True,
            )
        else:
            self.log(f"Không tìm thấy start_trace.py tại {start_script}", "red")

        # 2. Gửi request tới Edge Device
        self.log("Đang bắt đầu ghi dữ liệu trên Edge Device...", "blue")
        try:
            req = urllib.request.Request(
                f"http://{EDGE_DEVICE_IP}:{EDGE_DEVICE_PORT}/start", method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get("status") == "started":
                    self.current_remote_file = data.get("file")
                    self.log(
                        f"Đang ghi! (Remote file: {self.current_remote_file})", "green"
                    )
                else:
                    self.log(f"Edge Device phản hồi: {data.get('status')}", "orange")
        except Exception as e:
            self.log(f"Lỗi kết nối Edge Device: {e}", "red")

    def stop_collection(self):
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.NORMAL)
        self.is_recording = False

        threading.Thread(target=self._stop_task, daemon=True).start()

    def _stop_task(self):
        json_path = self.json_file_path.get()
        trace_dir = os.path.dirname(json_path)
        trace_name = os.path.splitext(os.path.basename(json_path))[0]

        # 1. Gửi lệnh Stop tới Edge Device
        self.log("Đang dừng ghi dữ liệu trên Edge Device...", "blue")
        try:
            req = urllib.request.Request(
                f"http://{EDGE_DEVICE_IP}:{EDGE_DEVICE_PORT}/stop", method="POST"
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            self.log(f"Lỗi ngắt Edge Device: {e}", "red")

        # 2. Tải file về
        if self.current_remote_file:
            self.log("Đang tải dữ liệu về máy...", "blue")
            out_dir = self.output_dir_path.get()

            # Format tên file: <trace_name>_<YYYYMMDD>_<HHMMSS>.jsonl
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_file = os.path.join(out_dir, f"{trace_name}_{timestamp}.jsonl")

            scp_cmd = f'scp -o StrictHostKeyChecking=no technician@{EDGE_DEVICE_IP}:{self.current_remote_file} "{local_file}"'
            subprocess.run(scp_cmd, shell=True)
            self.log(f"Đã lưu tại: {local_file}", "green")
        else:
            self.log("Không có file nào được tạo để tải về.", "orange")

        # 3. Chạy stop_trace.py
        self.log("Đang dọn dẹp PLC (stop_trace)...", "blue")
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        script_dir = os.path.join(base_dir, "report", "trace")
        stop_script = os.path.join(script_dir, "stop_trace.py")

        if os.path.exists(stop_script):
            subprocess.run(
                ["python", stop_script, "--trace-dir", trace_dir, trace_name],
                shell=True,
            )

        if self.lbl_status.cget("text").startswith("Status: Đang dọn dẹp"):
            self.log("Hoàn tất quy trình thu thập!", "green")


if __name__ == "__main__":
    root = tk.Tk()
    app = TraceApp(root)
    root.mainloop()
