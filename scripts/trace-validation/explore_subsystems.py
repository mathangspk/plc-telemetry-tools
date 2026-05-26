import json
import socket
import sys

# Force UTF-8 for Windows console
sys.stdout.reconfigure(encoding="utf-8")

PLC_HOST = "10.2.3.4"
RO_PORT = 49880
TIMEOUT = 5.0
TERMINATOR = b"|$>"


def send_command(sock, cmd):
    sock.sendall((cmd + "\r\n").encode("ascii"))
    buf = bytearray()
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf.extend(chunk)
            if TERMINATOR in buf:
                idx = buf.find(TERMINATOR)
                raw = buf[:idx].decode("utf-8", errors="replace").strip()
                return raw
        except socket.timeout:
            break
    return buf.decode("utf-8", errors="replace").strip()


def explore_node(sock, node_name):
    print(f"\n{'='*50}\n[*] Đang khám phá: {node_name}\n{'='*50}")
    resp = send_command(sock, f"{node_name} describe -children")

    if "unknown_name" in resp.lower() or not resp:
        print(f"[-] Node {node_name} không tồn tại hoặc không có con.")
        return

    try:
        start = resp.find("{")
        end = resp.rfind("}")
        if start != -1 and end != -1:
            json_str = resp[start : end + 1]
            data = json.loads(json_str)

            op = data.get("op-children", [])
            nop = data.get("nop-children", [])

            print(f"[+] Tìm thấy {len(op) + len(nop)} node con:")

            if op:
                print("\n  -- Operational Children (Có giá trị) --")
                for c in op:
                    print(f"     - {c.get('identity', 'Unknown')}")

            if nop:
                print("\n  -- Non-Operational Children (Nhóm/Danh mục) --")
                for c in nop:
                    print(f"     - {c.get('identity', 'Unknown')}")
        else:
            print("[?] Phản hồi không phải JSON:", resp)
    except Exception as e:
        print(f"[-] Lỗi khi parse JSON: {e}")
        print("Raw response:", resp)


def main():
    print(f"Đang kết nối tới {PLC_HOST}:{RO_PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((PLC_HOST, RO_PORT))

        # Bỏ qua dòng greeting
        try:
            sock.recv(1024)
        except socket.timeout:
            pass

        print("[+] Kết nối thành công!")

        # Khám phá 3 hệ thống yêu cầu
        explore_node(sock, "BMS")
        explore_node(sock, "Spreader")
        explore_node(sock, "TMS")

        # Gửi lệnh close để PLC dọn dẹp session
        sock.sendall(b"close\r\n")

    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
