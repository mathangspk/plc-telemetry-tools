#!/usr/bin/env python3
import socket, json, sys, time

PLC_HOST = '10.2.3.4'
PLC_PORT = 49880
TIMEOUT = 5.0
TERMINATOR = b'|$>'

SIGNALS = [
    'CANBusDrive/cWinchA/Current',
    'CANBusDrive/cWinchB/Current',
    'CANBusDrive/cWinchC/Current',
    'CANBusDrive/cWinchD/Current',
    'CANBusDrive/cWinchA/BattVoltage',
    'CANBusDrive/cWinchA/Torque',
    'CANBusDrive/cWinchA/MotorTemp',
    'CANBusDrive/cWinchB/MotorTemp',
    'CANBusDrive/cWinchC/MotorTemp',
    'CANBusDrive/cWinchD/MotorTemp',
    'System/BMSAB/Current',
    'System/BMSAB/Voltage',
]

def recv_until(sock, terminator, timeout):
    sock.settimeout(timeout)
    buf = bytearray()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        buf.extend(chunk)
        idx = buf.find(terminator)
        if idx != -1:
            return buf[:idx].decode('utf-8', errors='replace').strip()
    raw = buf.decode('utf-8', errors='replace').strip()
    if raw.endswith('$>'):
        raw = raw[:-2].strip()
    return raw

def send_cmd(sock, cmd, timeout=TIMEOUT):
    sock.sendall((cmd + chr(13) + chr(10)).encode('ascii'))
    return recv_until(sock, TERMINATOR, timeout)

def try_describe(sock, path):
    try:
        resp = send_cmd(sock, '{} describe'.format(path), timeout=TIMEOUT)
        if not resp or resp == '$>':
            return False, '(empty response)', None
        lower = resp.lower()
        if 'unknown' in lower or 'error' in lower or 'not found' in lower or 'invalid' in lower:
            return False, resp, None
        parsed = None
        try:
            start = resp.find('{')
            end = resp.rfind('}')
            if start == -1:
                start = resp.find('[')
                end = resp.rfind(']')
            if start != -1 and end != -1 and end > start:
                parsed = json.loads(resp[start:end+1])
        except Exception:
            pass
        return True, resp, parsed
    except socket.timeout:
        return False, '(timeout)', None
    except Exception as e:
        return False, '(exception: {})'.format(e), None

def main():
    print('=' * 80)
    print('MP-01 IDENTITY CAPTURE - LIVE RE-TEST')
    print('Target: {}:{} (RO port, conservative)'.format(PLC_HOST, PLC_PORT))
    print('Time: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    print('Signals: {}'.format(len(SIGNALS)))
    print('=' * 80)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(TIMEOUT)
        sock.connect((PLC_HOST, PLC_PORT))
        print('[+] TCP connected')
    except Exception as e:
        print('[ERROR] Connection failed: {}'.format(e))
        print('[!] PLC unreachable or connection pool exhausted. ABORTING.')
        sys.exit(1)

    greeting = recv_until(sock, TERMINATOR, TIMEOUT)
    print('[+] Greeting received: {}'.format(greeting[:200] if greeting else '(empty)'))

    results = []
    for i, path in enumerate(SIGNALS, 1):
        print('[{}/{}] {}'.format(i, len(SIGNALS), path))
        success, resp, parsed = try_describe(sock, path)

        identity = 'not captured'
        sample_value = 'n/a'

        if success:
            if parsed and isinstance(parsed, dict):
                identity = parsed.get('identity', 'not captured')
                for vk in ('value', 'Value', 'current_value', 'CurrentValue', 'raw'):
                    if vk in parsed:
                        sample_value = str(parsed[vk])
                        break
                if sample_value == 'n/a':
                    for k, v in parsed.items():
                        if k != 'identity' and isinstance(v, (int, float, str, bool)):
                            sample_value = '{}={}'.format(k, v)
                            break
            else:
                sample_value = resp[:100]
                identity = 'not captured (raw value response)'
            status = 'OK'
        else:
            status = 'FAIL'
            sample_value = resp[:100] if resp else 'no response'

        results.append({
            'runtime_path': path,
            'identity': identity,
            'sample_value': sample_value,
            'outcome': status,
            'raw_response': resp[:200] if resp else '',
        })
        print('  -> {} | identity={} | sample={}'.format(status, identity, sample_value))

    print('[*] Sending close command...')
    try:
        send_cmd(sock, 'close', timeout=2.0)
    except:
        pass
    try:
        sock.shutdown(socket.SHUT_WR)
    except:
        pass
    sock.close()
    print('[+] Session closed gracefully')

    print()
    print('=' * 80)
    print('RESULTS TABLE')
    print('=' * 80)
    print('{:<40} | {:<35} | {:<20} | {}'.format(
        'runtime_path', 'exact identity', 'sample value', 'outcome'))
    print('-' * 80)
    for r in results:
        print('{:<40} | {:<35} | {:<20} | {}'.format(
            r['runtime_path'], r['identity'], r['sample_value'], r['outcome']))
    print('-' * 80)

    ok_count = sum(1 for r in results if r['outcome'] == 'OK')
    fail_count = sum(1 for r in results if r['outcome'] == 'FAIL')
    print('Total: {} tested | {} OK | {} FAIL'.format(len(results), ok_count, fail_count))

    out_path = 'C:\\local\\opencode\\codesys\\scripts\\identity_capture_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print('[+] Results saved to: {}'.format(out_path))

if __name__ == '__main__':
    main()
