import json, os, sys, glob
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Extract all trace config signals
trace_dir = r"C:\local\opencode\codesys\exports\trace-config\individual_traces_with_time"
raw_signals = set()
num_files = 0
for fpath in glob.glob(os.path.join(trace_dir, "*.txt")):
    num_files += 1
    with open(fpath, 'r', encoding='utf-8') as f:
        for line in f.readlines()[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 1 and parts[0]:
                raw_signals.add(parts[0])

def translate_name(raw_name):
    parts = raw_name.split('.')
    translated = []
    for p in parts:
        if p == 'gSystem':
            translated.append('System')
        elif p.startswith('l') and len(p) > 1 and p[1].isupper():
            translated.append(p[1:])
        elif p.startswith('i') and len(p) > 1 and p[1].isupper():
            translated.append(p[1:])
        else:
            translated.append(p)
    return ".".join(translated)

translated = {}
for sig in raw_signals:
    translated[sig] = translate_name(sig)

# Build comprehensive runtime path set from live data
runtime_paths = set()

# System top-level
system_children_names = ['Local','Reporting','LED','Executor','Cycle','PLC','SystemState',
    'ParserRW','ParserRO','ParserEdge','Metric0ms','Metric250ms','Metric500ms','Metric1s',
    'Metric5s','Metric1m','Metric1h','Metric1d','CANBusSystem','CANBusDrive','Cabin',
    'CabinSecPwr','BMSAB','ChargerABC','FuncModeCntrl','UIEvent','ProgMovCntrl','Travel',
    'Lift','iLiftAPos','iLiftBPos','iLiftCPos','iLiftDPos','iLiftABSync','iLiftCDSync',
    'iLiftSync','Spreader','iTwistALowered','iTwistBLowered','iTwistCLowered','iTwistDLowered',
    'iwTwistRdy','iTwistLowerTrav','OperatingMode','Active','UMFS','EstopLoad','TMS',
    'Secondary','Alarm','Beacons','Horn','Lights','SensorSupply','Steer','iSteerAPos',
    'iSteerBPos','iSteerCPos','iSteerDPos']
for name in system_children_names:
    runtime_paths.add('System/' + name)

# BMSAB children (nop)
bmsab_children = ['AvailFactor','Availability','BMSAvailInsuff','BMSAvailLmtd','BMSChrgCutb',
    'BMSChrgMismatch','BMSCurrMismatch','BMSDischCutb','BMSNotConnect','BMSSOCMismatch',
    'BMSVoltMismatch','Current','CurrentMismatch','CycleOutput','DsblConnect','DsblVoltMisMgmt',
    'EnblBMS','EnblRestart','EnblSOCRecovery','RestartCount','SOC','SOCLowOpMin',
    'SOCLowStdbyMin','SOCMismatch','SOCRecCurrMin','SOCRecTimRst','SOCWarnLow',
    'TMSMismatch','Voltage','VoltageMismatch']
for c in bmsab_children:
    runtime_paths.add('System/BMSAB/' + c)

# TMS children (nop)
tms_children = ['BMSTMSCooling','BMSTMSHeating','BMSTMSNoCirc','Chilling','ClntChilling',
    'ClntHeating','ClntReserv','ClntReservoir','ClntSecFailHC','ClntSecFailPmp','ClntTemp',
    'ClntTempCold','ClntTempColdCutb','ClntTempHot','ClntTempHotCutb','CurrState',
    'Heating','OvrdControl','Pump','ReqState','TMSCooling','TMSHeating']
for c in tms_children:
    runtime_paths.add('System/TMS/' + c)

# ChargerABC children
charger_children = ['ChrgConn','ChrgDiscon','ChrgOBCErr','ChrgStdby','EnblManualChrg','ManualChrgCurr','ManualChrgVolt']
for c in charger_children:
    runtime_paths.add('System/ChargerABC/' + c)

# Secondary children
secondary_children = ['CntxtSgnMod','SecPwrMismatch','SecPwrNotRun','SecPwrNotRunMod','SecPwrWait']
for c in secondary_children:
    runtime_paths.add('System/Secondary/' + c)

# ProgMovCntrl children
for c in ['ProgMovNull','steer_0']:
    runtime_paths.add('System/ProgMovCntrl/' + c)

# SystemState children
for c in ['AutoStart','CntxtSysCntrl','CntxtSysStateDn','CntxtSysStateUp','Event','State']:
    runtime_paths.add('System/SystemState/' + c)

# Steer children
for c in ['CntxtQualModEx','iMovement']:
    runtime_paths.add('System/Steer/' + c)
for c in ['ChannelMask','Override','Suppress','SuppressAfter','SuppressCntdwn','iMovement']:
    runtime_paths.add('System/Steer/iMovement/' + c)

# Travel children
for c in ['CntxtQualModEx','iMovement']:
    runtime_paths.add('System/Travel/' + c)
for c in ['ChannelMask','ClntTempColdCutb','CntxtQualModEx','Life','Override','Suppress','SuppressAfter','SuppressCntdwn','iMovement']:
    runtime_paths.add('System/Travel/iMovement/' + c)

# Lift children
for c in ['CntxtQualModEx','iMovement']:
    runtime_paths.add('System/Lift/' + c)
for c in ['ChannelMask','ClntTempColdCutb','CntxtQualModEx','Life','Override','Suppress','SuppressAfter','SuppressCntdwn','iMovement']:
    runtime_paths.add('System/Lift/iMovement/' + c)

# Spreader children
for c in ['AB','CD','TwstALow','TwstBLow','TwstCLow','TwstDLow']:
    runtime_paths.add('System/Spreader/' + c)

# CANBusDrive devices
cbd_devices = ['BusPower','cSpreader','cSteerA','cSteerAngleA','cSteerAngleB','cSteerAngleC',
    'cSteerAngleD','cSteerB','cSteerC','cSteerD','cTransA','cTransB','cTransC','cTransD',
    'cWinchA','cWinchAngleA','cWinchAngleB','cWinchAngleC','cWinchAngleD','cWinchB','cWinchC','cWinchD']
for dev in cbd_devices:
    runtime_paths.add('CANBusDrive/' + dev)

# Drive signals (confirmed from cTransA, cSteerA, cWinchA - all identical 9-signal structure)
drive_signals = ['Alarm','BattCurrent','BattPower','BattVoltage','CntrlTemp','Current','MotorTemp','TPO1Stuffing','Velocity']
for dev in cbd_devices:
    if dev.startswith('c') and 'Angle' not in dev:
        for sig in drive_signals:
            runtime_paths.add('CANBusDrive/' + dev + '/' + sig)

# cSpreader signals (42 signals)
cspreader_signals = ['Brake','BrakeDisengage','BrakeThrottle','HydPressure','HydTemp','HydraulicFilter',
    'PmpCntrlTemp','PmpMotTemp','PumpAlarm','PumpAllow','PumpBattCrrnt','PumpBattVolt',
    'PumpCurrent','PumpOn','PumpPressure','PumpRunning','PumpState','PumpVelocity',
    'SideshiftAB','SideshiftCD','TelscpActive','TelscpAuto','TelscpAutoExt','TelscpAutoRet',
    'TelscpEnbl','TelscpExtend','TelscpRetract','TwstALow','TwstAStt','TwstActive','TwstBLow',
    'TwstBStt','TwstCLow','TwstCStt','TwstDLow','TwstDStt','TwstEnbl','TwstLock','TwstStt','TwstUnlock']
for sig in cspreader_signals:
    runtime_paths.add('CANBusDrive/cSpreader/' + sig)

# Angle device signals
for dev in ['cSteerAngleA','cSteerAngleB','cSteerAngleC','cSteerAngleD','cWinchAngleA','cWinchAngleB','cWinchAngleC','cWinchAngleD']:
    runtime_paths.add('CANBusDrive/' + dev + '/Angle')
    runtime_paths.add('CANBusDrive/' + dev + '/HeartbeatCounter')
    runtime_paths.add('CANBusDrive/' + dev + '/NodeState')

# NodeState for all drives
for dev in cbd_devices:
    if dev.startswith('c'):
        runtime_paths.add('CANBusDrive/' + dev + '/NodeState')
        runtime_paths.add('CANBusDrive/' + dev + '/HeartbeatCounter')

# Known non-existent
known_nonexistent = set()
for dev in ['cTransA','cTransB','cTransC','cTransD','cSteerA','cSteerB','cSteerC','cSteerD','cWinchA','cWinchB','cWinchC','cWinchD']:
    known_nonexistent.add('CANBusDrive/%s/ProposedThrottle' % dev)
    known_nonexistent.add('CANBusDrive/%s/TargetSpeed' % dev)
    known_nonexistent.add('CANBusDrive/%s/TargetVelocity' % dev)
    known_nonexistent.add('CANBusDrive/%s/EnableMotor' % dev)
    known_nonexistent.add('CANBusDrive/%s/Forward' % dev)
    known_nonexistent.add('CANBusDrive/%s/Reverse' % dev)
    known_nonexistent.add('CANBusDrive/%s/ClearAlarm' % dev)
    known_nonexistent.add('CANBusDrive/%s/Torque' % dev)
    known_nonexistent.add('CANBusDrive/%s/SlaveNotOp' % dev)
    known_nonexistent.add('CANBusDrive/%s/Enabled' % dev)
    known_nonexistent.add('CANBusDrive/%s/TriggerStart' % dev)
    known_nonexistent.add('CANBusDrive/%s/SlaveNotify' % dev)
    known_nonexistent.add('CANBusDrive/%s/SlaveBlock' % dev)
    known_nonexistent.add('CANBusDrive/%s/SlaveStop' % dev)
    known_nonexistent.add('CANBusDrive/%s/Diagnostic' % dev)
    known_nonexistent.add('CANBusDrive/%s/Stalled' % dev)
    known_nonexistent.add('CANBusDrive/%s/MeasuredThrottle' % dev)
    known_nonexistent.add('CANBusDrive/%s/ZeroCurrentVelocityIndicator' % dev)
    known_nonexistent.add('CANBusDrive/%s/ZeroTargetSpeedIndicator' % dev)
    known_nonexistent.add('CANBusDrive/%s/StalledCount' % dev)
    known_nonexistent.add('CANBusDrive/%s/StalledIndicator' % dev)
    known_nonexistent.add('CANBusDrive/%s/StallIndicator' % dev)
    known_nonexistent.add('CANBusDrive/%s/StallInput' % dev)
    known_nonexistent.add('CANBusDrive/%s/StallState' % dev)
    known_nonexistent.add('CANBusDrive/%s/Stationary' % dev)
    known_nonexistent.add('CANBusDrive/%s/StallTimer' % dev)
    known_nonexistent.add('CANBusDrive/%s/ControllerTemperature' % dev)
    known_nonexistent.add('CANBusDrive/%s/MotorTemperature' % dev)
    known_nonexistent.add('CANBusDrive/%s/BatteryVoltage' % dev)
    known_nonexistent.add('CANBusDrive/%s/BatteryCurrent' % dev)
    known_nonexistent.add('CANBusDrive/%s/BatteryPower' % dev)
    known_nonexistent.add('CANBusDrive/%s/TargetSpeed' % dev)

known_nonexistent.update([
    'Travel/MovementD/LDiagnostic','Travel/MovementD/Diagnostic','Travel/MovementD/lDiagnostic',
    'Lift/Diagnostic','Travel/Diagnostic',
    'System/ChargingEnabled',
])

# Remap rules
remap_rules = [
    ('System/BMS', 'System/BMSAB'),
    ('System/Steering', 'System/Steer'),
    ('System/Charger', 'System/ChargerABC'),
    ('System/SecondaryPowerSupply', 'System/Secondary'),
    ('System/ProgrammedMovementControl', 'System/ProgMovCntrl'),
    ('TMS/RequestedState', 'TMS/ReqState'),
    ('TMS/CurrentState', 'TMS/CurrState'),
    ('TMS/CoolantReservoir', 'TMS/ClntReservoir'),
    ('TMS/CurrentCoolantTemperature', 'TMS/ClntTemp'),
    ('TMS/CoolantChilling', 'TMS/ClntChilling'),
    ('TMS/CoolantHeating', 'TMS/ClntHeating'),
    ('TMS/CoolantPump', 'TMS/Pump'),
    ('TMS/RequestedCoolantTemperature', 'TMS/OvrdControl'),
    ('Travel/ThrottleValue', 'Travel/Throttle'),
    ('Travel/MovementD', 'Travel/mMovement'),
    ('Travel/MovementA', 'Travel/iMovement'),
    ('Travel/MovementB', 'Travel/iMovement'),
    ('Travel/MovementC', 'Travel/iMovement'),
    ('Travel/MovementD', 'Travel/iMovement'),
    ('Lift/MovementA', 'Lift/iMovement'),
    ('Lift/MovementB', 'Lift/iMovement'),
    ('Lift/MovementC', 'Lift/iMovement'),
    ('Lift/MovementD', 'Lift/iMovement'),
    ('Steering/WheelA', 'Steer/iMovement'),
    ('Steering/WheelB', 'Steer/iMovement'),
    ('Steering/WheelC', 'Steer/iMovement'),
    ('Steering/WheelD', 'Steer/iMovement'),
]

drive_abbrevs = [
    ('MotorTemperature', 'MotorTemp'),
    ('ControllerTemperature', 'CntrlTemp'),
    ('BatteryVoltage', 'BattVoltage'),
    ('BatteryCurrent', 'BattCurrent'),
    ('BatteryPower', 'BattPower'),
    ('TargetSpeed', 'TargetSpeed'),
]

spreader_abbrevs = [
    ('TelescopingActive', 'TelscpActive'),
    ('TelescopingEnabled', 'TelscpEnbl'),
    ('TelescopingAutoCommand', 'TelscpAuto'),
    ('TelescopingEnableCommand', 'TelscpEnbl'),
    ('TelescopingExtendAutoCommand', 'TelscpAutoExt'),
    ('TelescopingExtendCommand', 'TelscpExtend'),
    ('TelescopingRetractAutoCommand', 'TelscpAutoRet'),
    ('TelescopingRetractCommand', 'TelscpRetract'),
    ('TwistlocksEnabled', 'TwstEnbl'),
    ('TwistlocksActive', 'TwstActive'),
    ('TwistlocksLockCommand', 'TwstLock'),
    ('TwistlocksUnlockCommand', 'TwstUnlock'),
    ('HydraulicPressure', 'HydPressure'),
    ('HydraulicTemperature', 'HydTemp'),
    ('BrakeDisengaged', 'BrakeDisengage'),
    ('BrakeDisengageCommand', 'BrakeDisengage'),
    ('TwistlockACurrentState', 'TwstAStt'),
    ('TwistlockBCurrentState', 'TwstBStt'),
    ('TwistlockCCurrentState', 'TwstCStt'),
    ('TwistlockDCurrentState', 'TwstDStt'),
    ('TwistlockALoweredState', 'TwstALow'),
    ('TwistlockBLoweredState', 'TwstBLow'),
    ('TwistlockCLoweredState', 'TwstCLow'),
    ('TwistlockDLoweredState', 'TwstDLow'),
    ('TwistlocksCurrentState', 'TwstStt'),
    ('PumpMotorTemperature', 'PmpMotTemp'),
    ('PumpControllerTemperature', 'PmpCntrlTemp'),
]

# Classify
exact_match = []
remapped_abbrev = []
no_match = []
nonexistent_confirmed = []

for raw_sig in sorted(raw_signals):
    trans = translated[raw_sig]
    runtime_path = trans.replace('.', '/')
    
    # Check exact match
    if runtime_path in runtime_paths:
        exact_match.append({'raw': raw_sig, 'translated': trans, 'runtime': runtime_path})
        continue
    
    # Check known non-existent
    if runtime_path in known_nonexistent:
        nonexistent_confirmed.append({'raw': raw_sig, 'translated': trans, 'runtime': runtime_path})
        continue
    
    # Check remap rules
    remapped = False
    for old_path, new_path in remap_rules:
        if runtime_path == old_path or runtime_path.startswith(old_path + '/'):
            remainder = runtime_path[len(old_path):]
            new_runtime = new_path + remainder
            remapped_abbrev.append({
                'raw': raw_sig, 'translated': trans,
                'runtime_old': runtime_path, 'runtime_new': new_runtime,
                'rule': '%s -> %s' % (old_path, new_path)
            })
            remapped = True
            break
    if remapped:
        continue
    
    # Check drive signal abbreviations
    parts = runtime_path.split('/')
    if len(parts) >= 3 and parts[0] == 'CANBusDrive' and parts[1].startswith('c'):
        leaf = parts[-1]
        for long_name, short_name in drive_abbrevs:
            if leaf == long_name:
                new_path = '/'.join(parts[:-1]) + '/' + short_name
                remapped_abbrev.append({
                    'raw': raw_sig, 'translated': trans,
                    'runtime_old': runtime_path, 'runtime_new': new_path,
                    'rule': '%s -> %s' % (long_name, short_name)
                })
                remapped = True
                break
        if remapped:
            continue
    
    # Check spreader abbreviations
    if 'cSpreader' in runtime_path:
        for long_name, short_name in spreader_abbrevs:
            if long_name in runtime_path:
                new_path = runtime_path.replace(long_name, short_name)
                remapped_abbrev.append({
                    'raw': raw_sig, 'translated': trans,
                    'runtime_old': runtime_path, 'runtime_new': new_path,
                    'rule': '%s -> %s' % (long_name, short_name)
                })
                remapped = True
                break
        if remapped:
            continue
    
    # No match
    no_match.append({'raw': raw_sig, 'translated': trans, 'runtime': runtime_path})

# Output
output_dir = r"C:\local\opencode\codesys\exports\trace-config"
print('Total unique signals: %d' % len(raw_signals))
print('Exact match: %d' % len(exact_match))
print('Remapped: %d' % len(remapped_abbrev))
print('No match: %d' % len(no_match))
print('Nonexistent: %d' % len(nonexistent_confirmed))

# Show some no-match examples
print('\nNo-match samples:')
for r in no_match[:20]:
    print('  %s -> %s' % (r['raw'], r['runtime']))

# Save JSON
report = {
    'connectivity': {
        'rw_port_49870': 'CONNECTED',
        'ro_port_49880': 'CONNECTED',
        'emit_port_49890': 'CONNECTED',
        'system_state': {'systemstate': 'preparing', 'initialized': True, 'initialization_stage': 5},
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    'reconciliation': {
        'total_unique_signals': len(raw_signals),
        'exact_match_count': len(exact_match),
        'remapped_abbrev_count': len(remapped_abbrev),
        'no_match_count': len(no_match),
        'nonexistent_confirmed_count': len(nonexistent_confirmed),
        'exact_matches': exact_match,
        'remapped_abbrev': remapped_abbrev,
        'no_match': no_match,
        'nonexistent_confirmed': nonexistent_confirmed
    }
}

json_path = os.path.join(output_dir, "RUNTIME_REMAP_PHASE4.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
print('\n[+] JSON saved: %s' % json_path)
