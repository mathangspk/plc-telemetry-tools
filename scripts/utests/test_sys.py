import json
import socket
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect(("10.2.3.4", 49870))


def read_until(marker):
    data = b""
    while marker not in data:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            break
    return data.decode("utf-8", errors="ignore")


def execute(cmd):
    sock.sendall((cmd + "\n").encode("utf-8"))
    raw = read_until(b"|>")
    try:
        si = raw.find("{")
        ei = raw.rfind("}")
        if si == -1 and raw.find("[") != -1:
            si = raw.find("[")
            ei = raw.rfind("]")
        if si != -1 and ei != -1:
            return json.loads(raw[si : ei + 1])
    except:
        pass
    return raw.strip()


read_until(b">")
print("[+] Connected")

# System describe -children
print("[*] System describe -children...")
r = execute("System describe -children")
if isinstance(r, dict):
    op = r.get("op-children", [])
    nop = r.get("nop-children", [])
    print("  op-children: %d, nop-children: %d" % (len(op), len(nop)))
    for c in op:
        if isinstance(c, dict):
            name = c.get("identity", "").split(".")[-1]
            t = c.get("type", "?")
            print("  OP: %s (type=%s)" % (name, t))
    for c in nop:
        if isinstance(c, dict):
            name = c.get("identity", "").split(".")[-1]
            t = c.get("type", "?")
            print("  NOP: %s (type=%s)" % (name, t))

sock.close()
print("[+] Done")
