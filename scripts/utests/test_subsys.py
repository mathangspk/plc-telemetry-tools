import socket
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect(('10.2.3.4', 49870))

def read_until(marker):
    data = b''
    while marker not in data:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            break
    return data.decode('utf-8', errors='ignore')

def execute(cmd):
    sock.sendall((cmd + '\n').encode('utf-8'))
    raw = read_until(b'|>')
    try:
        si = raw.find('{')
        ei = raw.rfind('}')
        if si == -1 and raw.find('[') != -1:
            si = raw.find('[')
            ei = raw.rfind(']')
        if si != -1 and ei != -1:
            return json.loads(raw[si:ei+1])
    except:
        pass
    return raw.strip()

def get_children(path):
    r = execute(path + ' describe -children')
    if isinstance(r, dict):
        op = r.get('op-children', [])
        nop = r.get('nop-children', [])
        names = []
        for c in op:
            if isinstance(c, dict):
                names.append(c.get('identity','').split('/')[-1].split('.')[-1])
            elif isinstance(c, str):
                names.append(c)
        for c in nop:
            if isinstance(c, dict):
                names.append(c.get('identity','').split('/')[-1].split('.')[-1])
            elif isinstance(c, str):
                names.append(c)
        return names, len(op), len(nop)
    return [], 0, 0

read_until(b'>')
print('[+] Connected')

subsystems = ['BMSAB', 'Steer', 'ChargerABC', 'Secondary', 'ProgMovCntrl',
              'TMS', 'Travel', 'Lift', 'CANBusDrive', 'CANBusSystem',
              'Spreader', 'SystemState', 'FuncModeCntrl']

for sub in subsystems:
    path = 'System.' + sub if sub not in ['CANBusDrive', 'CANBusSystem'] else sub
    names, op_c, nop_c = get_children(path)
    print('\n[%s] %s: %d op, %d nop' % (sub, path, op_c, nop_c))
    if names:
        print('  Children: %s' % ', '.join(sorted(names)))

# Also explore CANBusDrive devices
print('\n[CANBusDrive devices]')
names, op_c, nop_c = get_children('CANBusDrive')
print('  Devices: %s' % ', '.join(sorted(names)))

# Explore one drive's signals
if names:
    dev = [n for n in names if 'TransA' in n or 'SteerA' in n or 'WinchA' in n]
    if dev:
        d = dev[0]
        sigs, s_op, s_nop = get_children('CANBusDrive/' + d)
        print('\n[CANBusDrive/%s signals] %d op, %d nop' % (d, s_op, s_nop))
        print('  Signals: %s' % ', '.join(sorted(sigs)))

sock.close()
print('\n[+] Done')
