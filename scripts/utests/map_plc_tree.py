import json
import os
import socket
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

PLC_HOST = "10.2.3.4"
RO_PORT = 49880
TIMEOUT = 3.0
TERMINATOR = b"|$>"


def send_cmd(sock, cmd):
    try:
        sock.sendall((cmd + "\r\n").encode("ascii"))
        buf = bytearray()
        deadline = time.monotonic() + TIMEOUT
        while time.monotonic() < deadline:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buf.extend(chunk)
                if TERMINATOR in buf:
                    idx = buf.find(TERMINATOR)
                    return buf[:idx].decode("utf-8", errors="replace").strip()
            except socket.timeout:
                break
        return buf.decode("utf-8", errors="replace").strip()
    except Exception as e:
        return ""


def explore(sock, identity, max_depth, current_depth=0, results_dict=None):
    if results_dict is None:
        results_dict = {}

    print(f"{'  ' * current_depth}├─ Đang quét: {identity}")

    if current_depth > max_depth:
        results_dict[identity] = "[MAX_DEPTH_REACHED]"
        return results_dict

    resp = send_cmd(sock, f"{identity} describe -children")
    if not resp or "unknown_name" in resp:
        results_dict[identity] = "[NO_CHILDREN]"
        return results_dict

    try:
        start = resp.find("{")
        end = resp.rfind("}")
        if start != -1 and end != -1:
            data = json.loads(resp[start : end + 1])
            op = data.get("op-children", [])
            nop = data.get("nop-children", [])

            node_data = {"type": data.get("type", ""), "children": {}}

            # Quét tất cả các con
            all_children = op + nop
            if not all_children:
                node_data["children"] = "[LEAF_NODE]"
            else:
                for c in all_children:
                    child_id = c.get("identity")
                    if child_id:
                        # Đệ quy xuống
                        node_data["children"][child_id] = explore(
                            sock, child_id, max_depth, current_depth + 1, {}
                        )[child_id]

            results_dict[identity] = node_data
    except Exception:
        results_dict[identity] = "[PARSE_ERROR]"

    return results_dict


def main():
    print(f"[*] Đang kết nối tới {PLC_HOST}:{RO_PORT} để lập bản đồ...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((PLC_HOST, RO_PORT))

        try:
            sock.recv(1024)
        except:
            pass

        print("[+] Kết nối thành công. Bắt đầu quét từ 'System' (Depth=4)...")

        # Bắt đầu quét từ gốc System
        tree = explore(sock, "System", max_depth=4)

        sock.sendall(b"close\r\n")

        # Lưu ra artifact
        output_path = r"C:\Users\technician\.gemini\antigravity\brain\221ed255-22b9-4c08-88a2-5f870ade149f\artifacts\plc_true_map.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)

        print(f"\n[+] Đã quét xong. Bản đồ thực tế được lưu tại: {output_path}")

    except Exception as e:
        print(f"[-] Lỗi kết nối: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
