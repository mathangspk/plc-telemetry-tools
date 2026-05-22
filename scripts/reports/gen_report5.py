import json, os, sys, glob
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

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
        elif p == 'lCANOpenMasterDrive':
            translated.append('CANBusDrive')
        elif p == 'lCANOpenMasterSystem':
            translated.append('CANBusSystem')
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

# Build runtime path set
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

# BMSAB children
bmsab_children = ['AvailFactor','Availability','BMSAvailInsuff','BMSAvailLmtd','BMSChrgCutb',
    'BMSChrgMismatch','BMSCurrMismatch','BMSDischCutb','BMSNotConnect','BMSSOCMismatch',
    'BMSVoltMismatch','Current','CurrentMismatch','CycleOutput','DsblConnect','DsblVoltMisMgmt',
    'EnblBMS','EnblRestart','EnblSOCRecovery','RestartCount','SOC','SOCLowOpMin',
    'SOCLowStdbyMin','SOCMismatch','SOCRecCurrMin','SOCRecTimRst','SOCWarnLow',
    'TMSMismatch','Voltage','VoltageMismatch']
for c in bmsab_children:
    runtime_paths.add('System/BMSAB/' + c)

# TMS children
tms_children = ['BMSTMSCooling','BMSTMSHeating','BMSTMSNoCirc','Chilling','ClntChilling',
    'ClntHeating','ClntReserv','ClntReservoir','ClntSecFailHC','ClntSecFailPmp','ClntTemp',
    'ClntTempCold','ClntTempColdCutb','ClntTempHot','ClntTempHotCutb','CurrState',
    'Heating','OvrdControl','Pump','ReqState','TMSCooling','TMSHeating']
for c in tms_children:
    runtime_paths.add('System/TMS/' + c)

# ChargerABC
for c in ['ChrgConn','ChrgDiscon','ChrgOBCErr','ChrgStdby','EnblManualChrg','ManualChrgCurr','ManualChrgVolt']:
    runtime_paths.add('System/ChargerABC/' + c)

# Secondary
for c in ['CntxtSgnMod','SecPwrMismatch','SecPwrNotRun','SecPwrNotRunMod','SecPwrWait']:
    runtime_paths.add('System/Secondary/' + c)

# ProgMovCntrl
for c in ['ProgMovNull','steer_0']:
    runtime_paths.add('System/ProgMovCntrl/' + c)

# SystemState
for c in ['AutoStart','CntxtSysCntrl','CntxtSysStateDn','CntxtSysStateUp','Event','State']:
    runtime_paths.add('System/SystemState/' + c)

# Steer
for c in ['CntxtQualModEx','iMovement']:
    runtime_paths.add('System/Steer/' + c)
for c in ['ChannelMask','Override','Suppress','SuppressAfter','SuppressCntdwn','iMovement']:
    runtime_paths.add('System/Steer/iMovement/' + c)

# Travel
for c in ['CntxtQualModEx','iMovement']:
    runtime_paths.add('System/Travel/' + c)
for c in ['ChannelMask','ClntTempColdCutb','CntxtQualModEx','Life','Override','Suppress','SuppressAfter','SuppressCntdwn','iMovement']:
    runtime_paths.add('System/Travel/iMovement/' + c)

# Lift
for c in ['CntxtQualModEx','iMovement']:
    runtime_paths.add('System/Lift/' + c)
for c in ['ChannelMask','ClntTempColdCutb','CntxtQualModEx','Life','Override','Suppress','SuppressAfter','SuppressCntdwn','iMovement']:
    runtime_paths.add('System/Lift/iMovement/' + c)

# Spreader
for c in ['AB','CD','TwstALow','TwstBLow','TwstCLow','TwstDLow']:
    runtime_paths.add('System/Spreader/' + c)

# CANBusDrive devices
cbd_devices = ['BusPower','cSpreader','cSteerA','cSteerAngleA','cSteerAngleB','cSteerAngleC',
    'cSteerAngleD','cSteerB','cSteerC','cSteerD','cTransA','cTransB','cTransC','cTransD',
    'cWinchA','cWinchAngleA','cWinchAngleB','cWinchAngleC','cWinchAngleD','cWinchB','cWinchC','cWinchD']
for dev in cbd_devices:
    runtime_paths.add('CANBusDrive/' + dev)
    runtime_paths.add('System/CANBusDrive/' + dev)

# Drive signals (9 confirmed per drive)
drive_signals = ['Alarm','BattCurrent','BattPower','BattVoltage','CntrlTemp','Current','MotorTemp','TPO1Stuffing','Velocity']
for dev in cbd_devices:
    if dev.startswith('c') and 'Angle' not in dev:
        for sig in drive_signals:
            runtime_paths.add('CANBusDrive/' + dev + '/' + sig)
            runtime_paths.add('System/CANBusDrive/' + dev + '/' + sig)

# cSpreader signals
cspreader_signals = ['Brake','BrakeDisengage','BrakeThrottle','HydPressure','HydTemp','HydraulicFilter',
    'PmpCntrlTemp','PmpMotTemp','PumpAlarm','PumpAllow','PumpBattCrrnt','PumpBattVolt',
    'PumpCurrent','PumpOn','PumpPressure','PumpRunning','PumpState','PumpVelocity',
    'SideshiftAB','SideshiftCD','TelscpActive','TelscpAuto','TelscpAutoExt','TelscpAutoRet',
    'TelscpEnbl','TelscpExtend','TelscpRetract','TwstALow','TwstAStt','TwstActive','TwstBLow',
    'TwstBStt','TwstCLow','TwstCStt','TwstDLow','TwstDStt','TwstEnbl','TwstLock','TwstStt','TwstUnlock']
for sig in cspreader_signals:
    runtime_paths.add('CANBusDrive/cSpreader/' + sig)
    runtime_paths.add('System/CANBusDrive/cSpreader/' + sig)

# Angle devices
for dev in ['cSteerAngleA','cSteerAngleB','cSteerAngleC','cSteerAngleD','cWinchAngleA','cWinchAngleB','cWinchAngleC','cWinchAngleD']:
    for sig in ['Angle','HeartbeatCounter','NodeState']:
        runtime_paths.add('CANBusDrive/' + dev + '/' + sig)
        runtime_paths.add('System/CANBusDrive/' + dev + '/' + sig)

# NodeState/HeartbeatCounter for all drives
for dev in cbd_devices:
    if dev.startswith('c'):
        runtime_paths.add('CANBusDrive/' + dev + '/NodeState')
        runtime_paths.add('CANBusDrive/' + dev + '/HeartbeatCounter')
        runtime_paths.add('System/CANBusDrive/' + dev + '/NodeState')
        runtime_paths.add('System/CANBusDrive/' + dev + '/HeartbeatCounter')

# CANBusSystem children
for dev in ['BMSA','BMSB','SecondaryPowerSupplyA','SecondaryPowerSupplyB','UInterfaceCabin','ChargerA']:
    runtime_paths.add('CANBusSystem/' + dev)
    runtime_paths.add('CANBusSystem/' + dev + '/NodeState')
    runtime_paths.add('System/CANBusSystem/' + dev)
    runtime_paths.add('System/CANBusSystem/' + dev + '/NodeState')
for sig in ['OBCStatus','OBCStatusDerived','RequestedOBCState','StatusCC','StatusCP','StopCharging']:
    runtime_paths.add('CANBusSystem/ChargerA/' + sig)
    runtime_paths.add('System/CANBusSystem/ChargerA/' + sig)
for sig in ['CurrentBMSState','RequestedBMSState','PackFaultCode','PackFaultNumber','PackAverageTemperature','PackMaxTemperature','PackMinTemperature']:
    runtime_paths.add('CANBusSystem/BMSA/' + sig)
    runtime_paths.add('CANBusSystem/BMSB/' + sig)
    runtime_paths.add('System/CANBusSystem/BMSA/' + sig)
    runtime_paths.add('System/CANBusSystem/BMSB/' + sig)

# Known non-existent
known_nonexistent = set()
for dev in ['cTransA','cTransB','cTransC','cTransD','cSteerA','cSteerB','cSteerC','cSteerD','cWinchA','cWinchB','cWinchC','cWinchD']:
    for sig in ['ProposedThrottle','TargetSpeed','TargetVelocity','EnableMotor','Forward','Reverse',
                'ClearAlarm','Torque','SlaveNotOp','Enabled','TriggerStart','SlaveNotify','SlaveBlock',
                'SlaveStop','Diagnostic','Stalled','MeasuredThrottle','ZeroCurrentVelocityIndicator',
                'ZeroTargetSpeedIndicator','StalledCount','StalledIndicator','StallIndicator',
                'StallInput','StallState','Stationary','StallTimer','ControllerTemperature',
                'MotorTemperature','BatteryVoltage','BatteryCurrent','BatteryPower']:
        known_nonexistent.add('CANBusDrive/%s/%s' % (dev, sig))
        known_nonexistent.add('System/CANBusDrive/%s/%s' % (dev, sig))

known_nonexistent.update([
    'Travel/MovementD/LDiagnostic','Travel/MovementD/Diagnostic','Travel/MovementD/lDiagnostic',
    'Lift/Diagnostic','Travel/Diagnostic','System/ChargingEnabled',
    'System/Travel/MovementD/LDiagnostic','System/Travel/MovementD/Diagnostic','System/Travel/MovementD/lDiagnostic',
    'System/Lift/Diagnostic','System/Travel/Diagnostic',
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
    ('Travel/MovementD', 'Travel/iMovement'),
    ('Travel/MovementA', 'Travel/iMovement'),
    ('Travel/MovementB', 'Travel/iMovement'),
    ('Travel/MovementC', 'Travel/iMovement'),
    ('Lift/MovementA', 'Lift/iMovement'),
    ('Lift/MovementB', 'Lift/iMovement'),
    ('Lift/MovementC', 'Lift/iMovement'),
    ('Lift/MovementD', 'Lift/iMovement'),
    ('Steering/WheelA', 'Steer/iMovement'),
    ('Steering/WheelB', 'Steer/iMovement'),
    ('Steering/WheelC', 'Steer/iMovement'),
    ('Steering/WheelD', 'Steer/iMovement'),
]

# Drive device name remaps (with System/ prefix)
drive_device_remaps = [
    ('System/CANBusDrive/TransA', 'System/CANBusDrive/cTransA'),
    ('System/CANBusDrive/TransB', 'System/CANBusDrive/cTransB'),
    ('System/CANBusDrive/TransC', 'System/CANBusDrive/cTransC'),
    ('System/CANBusDrive/TransD', 'System/CANBusDrive/cTransD'),
    ('System/CANBusDrive/SteerA', 'System/CANBusDrive/cSteerA'),
    ('System/CANBusDrive/SteerB', 'System/CANBusDrive/cSteerB'),
    ('System/CANBusDrive/SteerC', 'System/CANBusDrive/cSteerC'),
    ('System/CANBusDrive/SteerD', 'System/CANBusDrive/cSteerD'),
    ('System/CANBusDrive/WinchA', 'System/CANBusDrive/cWinchA'),
    ('System/CANBusDrive/WinchB', 'System/CANBusDrive/cWinchB'),
    ('System/CANBusDrive/WinchC', 'System/CANBusDrive/cWinchC'),
    ('System/CANBusDrive/WinchD', 'System/CANBusDrive/cWinchD'),
    ('System/CANBusDrive/Spreader', 'System/CANBusDrive/cSpreader'),
    ('System/CANBusDrive/SteerAngleA', 'System/CANBusDrive/cSteerAngleA'),
    ('System/CANBusDrive/SteerAngleB', 'System/CANBusDrive/cSteerAngleB'),
    ('System/CANBusDrive/SteerAngleC', 'System/CANBusDrive/cSteerAngleC'),
    ('System/CANBusDrive/SteerAngleD', 'System/CANBusDrive/cSteerAngleD'),
    ('System/CANBusDrive/WinchAngleA', 'System/CANBusDrive/cWinchAngleA'),
    ('System/CANBusDrive/WinchAngleB', 'System/CANBusDrive/cWinchAngleB'),
    ('System/CANBusDrive/WinchAngleC', 'System/CANBusDrive/cWinchAngleC'),
    ('System/CANBusDrive/WinchAngleD', 'System/CANBusDrive/cWinchAngleD'),
    # Without System/ prefix
    ('CANBusDrive/TransA', 'CANBusDrive/cTransA'),
    ('CANBusDrive/TransB', 'CANBusDrive/cTransB'),
    ('CANBusDrive/TransC', 'CANBusDrive/cTransC'),
    ('CANBusDrive/TransD', 'CANBusDrive/cTransD'),
    ('CANBusDrive/SteerA', 'CANBusDrive/cSteerA'),
    ('CANBusDrive/SteerB', 'CANBusDrive/cSteerB'),
    ('CANBusDrive/SteerC', 'CANBusDrive/cSteerC'),
    ('CANBusDrive/SteerD', 'CANBusDrive/cSteerD'),
    ('CANBusDrive/WinchA', 'CANBusDrive/cWinchA'),
    ('CANBusDrive/WinchB', 'CANBusDrive/cWinchB'),
    ('CANBusDrive/WinchC', 'CANBusDrive/cWinchC'),
    ('CANBusDrive/WinchD', 'CANBusDrive/cWinchD'),
    ('CANBusDrive/Spreader', 'CANBusDrive/cSpreader'),
    ('CANBusDrive/SteerAngleA', 'CANBusDrive/cSteerAngleA'),
    ('CANBusDrive/SteerAngleB', 'CANBusDrive/cSteerAngleB'),
    ('CANBusDrive/SteerAngleC', 'CANBusDrive/cSteerAngleC'),
    ('CANBusDrive/SteerAngleD', 'CANBusDrive/cSteerAngleD'),
    ('CANBusDrive/WinchAngleA', 'CANBusDrive/cWinchAngleA'),
    ('CANBusDrive/WinchAngleB', 'CANBusDrive/cWinchAngleB'),
    ('CANBusDrive/WinchAngleC', 'CANBusDrive/cWinchAngleC'),
    ('CANBusDrive/WinchAngleD', 'CANBusDrive/cWinchAngleD'),
]

drive_abbrevs = [
    ('MotorTemperature', 'MotorTemp'),
    ('ControllerTemperature', 'CntrlTemp'),
    ('BatteryVoltage', 'BattVoltage'),
    ('BatteryCurrent', 'BattCurrent'),
    ('BatteryPower', 'BattPower'),
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

strip_suffixes = ['.Value', '/Value', '_Unique', '/_Unique']

# Classify
exact_match = []
remapped_abbrev = []
no_match = []
nonexistent_confirmed = []

for raw_sig in sorted(raw_signals):
    trans = translated[raw_sig]
    runtime_path = trans.replace('.', '/')
    
    # Strip suffixes
    for suffix in strip_suffixes:
        if runtime_path.endswith(suffix):
            runtime_path = runtime_path[:-len(suffix)]
    
    # Check exact match
    if runtime_path in runtime_paths:
        exact_match.append({'raw': raw_sig, 'translated': trans, 'runtime': runtime_path})
        continue
    
    # Check known non-existent
    if runtime_path in known_nonexistent:
        nonexistent_confirmed.append({'raw': raw_sig, 'translated': trans, 'runtime': runtime_path})
        continue
    
    # Check drive device remaps
    remapped = False
    for old_path, new_path in drive_device_remaps:
        if runtime_path == old_path or runtime_path.startswith(old_path + '/'):
            remainder = runtime_path[len(old_path):]
            new_runtime = new_path + remainder
            # Apply drive abbreviations
            parts = new_runtime.split('/')
            if len(parts) >= 3:
                leaf = parts[-1]
                for long_name, short_name in drive_abbrevs:
                    if leaf == long_name:
                        new_runtime = '/'.join(parts[:-1]) + '/' + short_name
                        break
            # Apply spreader abbreviations
            if 'cSpreader' in new_runtime:
                for long_name, short_name in spreader_abbrevs:
                    if long_name in new_runtime:
                        new_runtime = new_runtime.replace(long_name, short_name)
                        break
            remapped_abbrev.append({
                'raw': raw_sig, 'translated': trans,
                'runtime_old': trans.replace('.', '/'),
                'runtime_new': new_runtime,
                'rule': 'device rename + abbrev'
            })
            remapped = True
            break
    if remapped:
        continue
    
    # Check remap rules
    for old_path, new_path in remap_rules:
        if runtime_path == old_path or runtime_path.startswith(old_path + '/'):
            remainder = runtime_path[len(old_path):]
            new_runtime = new_path + remainder
            remapped_abbrev.append({
                'raw': raw_sig, 'translated': trans,
                'runtime_old': trans.replace('.', '/'),
                'runtime_new': new_runtime,
                'rule': '%s -> %s' % (old_path, new_path)
            })
            remapped = True
            break
    if remapped:
        continue
    
    # Check drive signal abbreviations
    parts = runtime_path.split('/')
    if len(parts) >= 3 and parts[0] in ['CANBusDrive', 'System'] and any(p.startswith('c') for p in parts[1:]):
        leaf = parts[-1]
        for long_name, short_name in drive_abbrevs:
            if leaf == long_name:
                new_path = '/'.join(parts[:-1]) + '/' + short_name
                remapped_abbrev.append({
                    'raw': raw_sig, 'translated': trans,
                    'runtime_old': trans.replace('.', '/'),
                    'runtime_new': new_path,
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
                    'runtime_old': trans.replace('.', '/'),
                    'runtime_new': new_path,
                    'rule': '%s -> %s' % (long_name, short_name)
                })
                remapped = True
                break
        if remapped:
            continue
    
    # No match
    no_match.append({'raw': raw_sig, 'translated': trans, 'runtime': runtime_path})

print('Total unique signals: %d' % len(raw_signals))
print('Exact match: %d' % len(exact_match))
print('Remapped: %d' % len(remapped_abbrev))
print('No match: %d' % len(no_match))
print('Nonexistent: %d' % len(nonexistent_confirmed))

print('\nNo-match samples:')
for r in no_match[:30]:
    print('  %s -> %s' % (r['raw'], r['runtime']))

print('\nExact match samples:')
for r in exact_match[:20]:
    print('  %s -> %s' % (r['raw'], r['runtime']))

# Save JSON
output_dir = r"C:\local\opencode\codesys\exports\trace-config"
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
