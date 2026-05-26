import json
import re
import socket
import sys

sys.stdout.reconfigure(encoding="utf-8")


def probe_raw(path):
    s = socket.socket()
    s.settimeout(8)
    s.connect(("10.2.3.4", 49870))

    def ru(m):
        d = b""
        while m not in d:
            try:
                c = s.recv(16384)
                if not c:
                    break
                d += c
            except:
                break
        return d.decode("utf-8", errors="ignore")

    def ex(cmd):
        s.sendall((cmd + "\n").encode("utf-8"))
        r = ru(b"|>")
        return r.strip()

    ru(b">")
    r = ex(path + " describe -children")
    s.close()
    return r


for p in ["System/Steer/iMovement", "System/Travel/iMovement", "System/Lift/iMovement"]:
    r = probe_raw(p)
    count = r.count('"identity"')
    names = re.findall(r'"identity":"[^"]+/([^"]+)"', r)
    print("%s: ~%d children -> %s" % (p, count, ",".join(sorted(set(names)))))
