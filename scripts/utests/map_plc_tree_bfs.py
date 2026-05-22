import socket
import json
import time
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

PLC_HOST = '10.2.3.4'
RO_PORT = 49880
TIMEOUT = 2.0
TERMINATOR = b'|$>'
STATE_FILE = r"C:\local\opencode\codesys\scripts\explorer_state.json"
FINAL_OUTPUT = r"C:\Users\technician\.gemini\antigravity\brain\221ed255-22b9-4c08-88a2-5f870ade149f\artifacts\plc_true_map.json"

# Known leaf/primitive types that do not have children
LEAF_TYPES = {
    'ValRefBool', 'ValRefFloat', 'ValRefInt', 'ValRefString',
    'iwScaled', 'iSynch', 'iwPosOnly', 'iwTwistRdy', 'iwLockout'
}

def is_leaf_type(type_name):
    if not type_name:
        return False
    if type_name in LEAF_TYPES:
        return True
    if type_name.startswith('ValRef') or type_name.startswith('ValObj'):
        return True
    if type_name.lower() in {'bool', 'float', 'int', 'string', 'double', 'real', 'word', 'dword', 'byte', 'uint', 'usint', 'udint', 'sint', 'dint', 'lreal'}:
        return True
    return False

class RobustPLCExplorer:
    def __init__(self, host=PLC_HOST, port=RO_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.close()
        print(f"[*] Đang kết nối tới {self.host}:{self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)
        self.sock.connect((self.host, self.port))
        # Nhận lời chào ban đầu nếu có
        try:
            self.sock.recv(1024)
        except:
            pass
        print("[+] Kết nối thành công.")

    def send_cmd(self, cmd):
        for attempt in range(3):
            try:
                if not self.sock:
                    self.connect()
                self.sock.sendall((cmd + '\r\n').encode('ascii'))
                buf = bytearray()
                deadline = time.monotonic() + TIMEOUT
                while time.monotonic() < deadline:
                    try:
                        chunk = self.sock.recv(4096)
                        if not chunk:
                            break
                        buf.extend(chunk)
                        if TERMINATOR in buf:
                            idx = buf.find(TERMINATOR)
                            return buf[:idx].decode('utf-8', errors='replace').strip()
                    except socket.timeout:
                        break
                # Trả về những gì nhận được nếu quá thời gian
                return buf.decode('utf-8', errors='replace').strip()
            except Exception as e:
                print(f"[!] Lỗi gửi lệnh (Lượt thử {attempt+1}/3): {e}")
                time.sleep(1.0)
                try:
                    self.connect()
                except Exception as conn_err:
                    print(f"[!] Kết nối lại thất bại: {conn_err}")
        return ""

    def close(self):
        if self.sock:
            try:
                self.sock.sendall(b"close\r\n")
            except:
                pass
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                # Chuyển list thành set cho queue và visited
                state['queue'] = list(state.get('queue', []))
                state['visited'] = set(state.get('visited', []))
                state['tree'] = state.get('tree', {})
                print(f"[+] Đã tải lại trạng thái lưu trữ: {len(state['visited'])} node đã quét, {len(state['queue'])} node trong hàng chờ.")
                return state
        except Exception as e:
            print(f"[!] Lỗi đọc file trạng thái: {e}. Bắt đầu quét mới...")
    
    # Mặc định bắt đầu từ System
    return {
        'queue': ['System'],
        'visited': set(),
        'tree': {}
    }

def save_state(state):
    try:
        serializable = {
            'queue': state['queue'],
            'visited': list(state['visited']),
            'tree': state['tree']
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Lỗi ghi file trạng thái: {e}")

def main():
    explorer = RobustPLCExplorer()
    state = load_state()
    
    try:
        explorer.connect()
    except Exception as e:
        print(f"[-] Không thể kết nối tới PLC: {e}")
        return

    save_counter = 0

    while state['queue']:
        node = state['queue'].pop(0)
        
        if node in state['visited']:
            continue
            
        print(f"[*] Đang quét node ({len(state['visited'])} đã quét, {len(state['queue'])} chờ): {node}")
        
        resp = explorer.send_cmd(f"{node} describe -children")
        
        if not resp or "unknown_name" in resp or "not found" in resp:
            state['tree'][node] = "[NO_CHILDREN]"
            state['visited'].add(node)
            continue
            
        try:
            start = resp.find('{')
            end = resp.rfind('}')
            if start != -1 and end != -1:
                data = json.loads(resp[start:end+1])
                op = data.get('op-children', [])
                nop = data.get('nop-children', [])
                all_children = op + nop
                
                node_data = {
                    "type": data.get("type", ""),
                    "subsystem": data.get("subsystem", ""),
                    "children": []
                }
                
                for c in all_children:
                    child_id = c.get("identity")
                    child_type = c.get("type", "")
                    child_sub = c.get("subsystem", "")
                    
                    if child_id:
                        # Chuẩn hóa tên đường dẫn biến
                        c_info = {
                            "identity": child_id,
                            "type": child_type,
                            "subsystem": child_sub
                        }
                        
                        # Kiểm tra xem có phải node lá không
                        # Nếu độ sâu đường dẫn >= 6 (vd: PrimaryPLC/System/BMSAB/ControllerBMSA/PackChargingCurrentTarget/Value), ta coi là lá luôn để an toàn
                        path_parts = child_id.replace('.', '/').split('/')
                        is_leaf = is_leaf_type(child_type) or len(path_parts) >= 6
                        
                        if is_leaf:
                            c_info["status"] = "[LEAF]"
                        else:
                            c_info["status"] = "[EXPANDABLE]"
                            if child_id not in state['visited'] and child_id not in state['queue']:
                                state['queue'].append(child_id)
                                
                        node_data["children"].append(c_info)
                
                state['tree'][node] = node_data
                state['visited'].add(node)
            else:
                state['tree'][node] = "[NON_JSON_RESPONSE]"
                state['visited'].add(node)
        except Exception as e:
            print(f"[!] Lỗi parse JSON cho node {node}: {e}")
            state['tree'][node] = "[PARSE_ERROR]"
            state['visited'].add(node)
            
        save_counter += 1
        if save_counter >= 10:
            save_state(state)
            save_counter = 0
            print("[*] Đã tự động lưu trạng thái quét...")
            
        # Nghỉ nhẹ tránh spam PLC
        time.sleep(0.05)

    # Đóng kết nối
    explorer.close()
    
    # Lưu kết quả cuối cùng
    save_state(state)
    
    # Tạo cấu trúc cây phân cấp đẹp đẽ từ tree phẳng
    try:
        os.makedirs(os.path.dirname(FINAL_OUTPUT), exist_ok=True)
        with open(FINAL_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(state['tree'], f, indent=2, ensure_ascii=False)
        print(f"\n[+] QUÉT THÀNH CÔNG! Bản đồ phẳng đã được lưu tại: {FINAL_OUTPUT}")
        
        # Xóa file trạng thái tạm thời
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            print("[*] Đã dọn dẹp file trạng thái tạm thời.")
    except Exception as e:
        print(f"[!] Lỗi lưu bản đồ cuối cùng: {e}")

if __name__ == "__main__":
    main()
