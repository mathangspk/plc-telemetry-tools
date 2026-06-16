import sys
import os

# Winch Configuration
# Node IDs:
# Winch A: 74 (0x4A)
# Winch B: 78 (0x4E)
# Winch C: 82 (0x52)
# Winch D: 86 (0x56)

WINCHES = {
    'WinchA': {'node_id': 74, 'txpdo1': 0x1CA, 'txpdo2': 0x2CA},
    'WinchB': {'node_id': 78, 'txpdo1': 0x1CE, 'txpdo2': 0x2CE},
    'WinchC': {'node_id': 82, 'txpdo1': 0x1D2, 'txpdo2': 0x2D2},
    'WinchD': {'node_id': 86, 'txpdo1': 0x1D6, 'txpdo2': 0x2D6},
}

# Reverse lookup for COB-IDs
COB_ID_MAP = {}
for name, cfg in WINCHES.items():
    COB_ID_MAP[cfg['txpdo1']] = (name, 1)
    COB_ID_MAP[cfg['txpdo2']] = (name, 2)

# Scaling Constants (lTypeSteer = FALSE)
L_NOMINAL_CURRENT = 400.0
L_POLE_PAIRS = 3.0
L_NOMINAL_VOLTAGE = 120.0

def to_int16_le(b0, b1):
    val = (b1 << 8) | b0
    if val >= 0x8000:
        val -= 0x10000
    return val

def to_uint16_le(b0, b1):
    return (b1 << 8) | b0

def to_sint8(b):
    if b >= 0x80:
        b -= 0x100
    return b

def to_usint8(b):
    return b

def decode_txpdo1(data, winch_name):
    # Data is list of 8 ints
    if len(data) < 8:
        return {}
    
    raw_velocity = to_int16_le(data[0], data[1])
    raw_status = to_uint16_le(data[2], data[3])
    raw_current = to_usint8(data[7])
    
    velocity = raw_velocity / 30.0
    current = raw_current * 2.0
    
    return {
        'Winch': winch_name,
        'Velocity_rpm': round(velocity, 3),
        'Current_A': round(current, 1),
        'Status_raw': f"0x{raw_status:04X}"
    }

def decode_txpdo2(data, winch_name):
    # Data is list of 8 ints
    if len(data) < 8:
        return {}
    
    raw_alarm = to_uint16_le(data[0], data[1])
    raw_motor_temp = to_usint8(data[2])
    raw_cntrl_temp = to_sint8(data[3])
    raw_batt_current = to_usint8(data[5])
    raw_batt_voltage = to_uint16_le(data[6], data[7])
    
    motor_temp = raw_motor_temp - 40.0
    cntrl_temp = raw_cntrl_temp # scaling = 1.0, offset = 0
    batt_current = raw_batt_current * (400.0 / 127.0)
    batt_voltage = raw_batt_voltage * 0.12
    
    return {
        'Winch': winch_name,
        'Alarm_raw': f"0x{raw_alarm:04X}",
        'MotorTemp_C': round(motor_temp, 1),
        'ControllerTemp_C': round(cntrl_temp, 1),
        'BatteryCurrent_A': round(batt_current, 3),
        'BatteryVoltage_V': round(batt_voltage, 2)
    }

def parse_asc_line(line):
    # Standard line format: timestamp channel id Dir d dlc byte0 byte1 ...
    # Example: "  0.000000 2  4E8             Rx   d 8 00 00 82 00 00 00 7E 00"
    parts = line.split()
    if len(parts) < 7:
        return None
    
    try:
        timestamp = float(parts[0])
        channel = int(parts[1])
        cob_id = int(parts[2], 16)
        direction = parts[3]
        if parts[4] == 'd':
            dlc = int(parts[5])
            bytes_start = 6
        else:
            dlc = int(parts[4])
            bytes_start = 5
            
        data = [int(x, 16) for x in parts[bytes_start:bytes_start+dlc]]
        return {
            'timestamp': timestamp,
            'channel': channel,
            'cob_id': cob_id,
            'dir': direction,
            'dlc': dlc,
            'data': data
        }
    except Exception:
        return None

def process_asc_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: file not found: {file_path}")
        return
        
    print(f"Decoding Winch Telemetry from: {file_path}")
    print("-" * 115)
    print(f"{'Time [s]':<12} | {'Winch':<8} | {'Velocity [rpm]':<15} | {'Current [A]':<12} | {'Motor Temp [C]':<15} | {'Controller Temp [C]':<20} | {'Batt Current [A]':<18} | {'Batt Voltage [V]':<18}")
    print("-" * 115)
    
    # Keep track of last seen state for each winch to show combined logs
    winch_state = {name: {} for name in WINCHES}
    
    with open(file_path, 'r') as f:
        for line in f:
            msg = parse_asc_line(line)
            if msg and msg['cob_id'] in COB_ID_MAP:
                winch_name, pdo_num = COB_ID_MAP[msg['cob_id']]
                
                if pdo_num == 1:
                    decoded = decode_txpdo1(msg['data'], winch_name)
                    winch_state[winch_name].update(decoded)
                elif pdo_num == 2:
                    decoded = decode_txpdo2(msg['data'], winch_name)
                    winch_state[winch_name].update(decoded)
                
                # If we have both PDO fields for a winch, we can print its state
                state = winch_state[winch_name]
                if 'Velocity_rpm' in state and 'MotorTemp_C' in state:
                    print(f"{msg['timestamp']:<12.6f} | {winch_name:<8} | {state['Velocity_rpm']:<15.1f} | {state['Current_A']:<12.1f} | {state['MotorTemp_C']:<15.1f} | {state['ControllerTemp_C']:<20.1f} | {state['BatteryCurrent_A']:<18.3f} | {state['BatteryVoltage_V']:<18.2f}")
                    # Clear printed status keys to wait for next updates if desired, or keep them to carry over state
                    # Here we keep them (sample-and-hold style) and clear to prevent duplicate print
                    state.clear()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        process_asc_file(sys.argv[1])
    else:
        # Default to the sample asc in exports
        default_path = os.path.join(os.path.dirname(__file__), "..", "exports", "CAN_message", "CANBusDrive", "can1.asc")
        if os.path.exists(default_path):
            process_asc_file(default_path)
        else:
            print("Please provide the path to the CAN ASC log file.")
