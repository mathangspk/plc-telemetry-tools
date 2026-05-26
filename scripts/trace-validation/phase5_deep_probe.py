import json
import socket
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

PLC_HOST = "10.2.3.4"
RO_PORT = 49880
RW_PORT = 49870
TIMEOUT = 5.0
TERMINATOR = b"|$>"


class PLCProbe:
    def __init__(self, host=PLC_HOST, port=RO_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)
        self.sock.connect((self.host, self.port))
        # Read greeting
        self._read_until(b"$>")

    def _read_until(self, marker):
        data = b""
        deadline = time.monotonic() + TIMEOUT
        while time.monotonic() < deadline:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if marker in data:
                    return data.decode("utf-8", errors="replace")
            except socket.timeout:
                break
        return data.decode("utf-8", errors="replace")

    def describe(self, path):
        for attempt in range(2):
            try:
                if not self.sock:
                    self.connect()
                cmd = path + " describe"
                self.sock.sendall((cmd + "\r\n").encode("ascii"))
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
                            resp = buf[:idx].decode("utf-8", errors="replace").strip()
                            if (
                                resp
                                and "unknown_name" not in resp
                                and "not found" not in resp
                            ):
                                return True, resp
                            return False, resp
                    except socket.timeout:
                        break
            except Exception as e:
                time.sleep(0.5)
                try:
                    self.connect()
                except:
                    pass
        return False, "connection_failed"

    def describe_children(self, path):
        for attempt in range(2):
            try:
                if not self.sock:
                    self.connect()
                cmd = path + " describe -children"
                self.sock.sendall((cmd + "\r\n").encode("ascii"))
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
                            resp = buf[:idx].decode("utf-8", errors="replace").strip()
                            return resp
                    except socket.timeout:
                        break
            except Exception as e:
                time.sleep(0.5)
                try:
                    self.connect()
                except:
                    pass
        return "connection_failed"

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


# Define all 96 no-match signals as probe targets
# Grouped by subsystem for efficient probing

PROBE_TARGETS = {
    "Lift_deep": [
        "Lift/Input describe",
        "Lift/InputProcessed describe",
        "Lift/Throttle describe",
        "Lift/ThrottleValue describe",
        "Lift/ScalingA describe",
        "Lift/ScalingB describe",
        "Lift/ScalingC describe",
        "Lift/ScalingD describe",
        "Lift/iMovement describe",
        "Lift/iMovement describe -children",
        "Lift/CntxtQualModEx describe -children",
    ],
    "Lift_ChargeInterlock": [
        "Lift/ChargeInterlock describe",
        "Lift/ChargeInterlock describe -children",
        "Lift/lChargeInterlock describe",
        "Lift/lChargeInterlock describe -children",
    ],
    "Lift_Interlock": [
        "Lift/Interlock describe",
        "Lift/Interlock describe -children",
        "Lift/lInterlock describe",
        "Lift/lInterlock describe -children",
    ],
    "Lift_Movement_Diagnostic": [
        "Lift/MovementA describe",
        "Lift/MovementA describe -children",
        "Lift/MovementB describe",
        "Lift/MovementB describe -children",
        "Lift/MovementC describe",
        "Lift/MovementC describe -children",
        "Lift/MovementD describe",
        "Lift/MovementD describe -children",
    ],
    "LiftInterlock_TopLevel": [
        "LiftAPositionInterlock describe",
        "LiftAPositionInterlock describe -children",
        "LiftBPositionInterlock describe",
        "LiftBPositionInterlock describe -children",
        "LiftCPositionInterlock describe",
        "LiftCPositionInterlock describe -children",
        "LiftDPositionInterlock describe",
        "LiftDPositionInterlock describe -children",
        "LiftABSynchronousInterlock describe",
        "LiftABSynchronousInterlock describe -children",
        "LiftCDSynchronousInterlock describe",
        "LiftCDSynchronousInterlock describe -children",
        "LiftSynchronousInterlock describe",
        "LiftSynchronousInterlock describe -children",
        "iLiftAPos describe -children",
        "iLiftBPos describe -children",
        "iLiftCPos describe -children",
        "iLiftDPos describe -children",
        "iLiftABSync describe -children",
        "iLiftCDSync describe -children",
        "iLiftSync describe -children",
    ],
    "Travel_deep": [
        "Travel/Input describe",
        "Travel/Input describe -children",
        "Travel/InputProcessed describe",
        "Travel/InputNulled describe",
        "Travel/InputPresentAny describe",
        "Travel/InputPresentSecondary describe",
        "Travel/InputResolved describe",
        "Travel/InputScaling describe",
        "Travel/InputSecondary describe",
        "Travel/EnableInputSecondary describe",
        "Travel/Active describe",
        "Travel/Throttle describe",
        "Travel/ThrottleValue describe",
        "Travel/CurrentFunctionSlowFactor describe",
        "Travel/CurrentOperatingModeSlowFactor describe",
        "Travel/CurrentUInterfaceSlowFactor describe",
        "Travel/SteerAdjustTimer describe",
        "Travel/SteerAdjustTimer describe -children",
        "Travel/iMovement describe -children",
        "Travel/CntxtQualModEx describe -children",
    ],
    "Travel_Movement_Diagnostic": [
        "Travel/MovementA describe",
        "Travel/MovementA describe -children",
        "Travel/MovementB describe",
        "Travel/MovementB describe -children",
        "Travel/MovementC describe",
        "Travel/MovementC describe -children",
        "Travel/MovementD describe",
        "Travel/MovementD describe -children",
    ],
    "Travel_Scaling": [
        "Travel/ScalingA describe",
        "Travel/ScalingB describe",
        "Travel/ScalingC describe",
        "Travel/ScalingD describe",
    ],
    "Steering_deep": [
        "Steer/Input describe",
        "Steer/InputProcessed describe",
        "Steer/InputPresentAny describe",
        "Steer/TargetAngle describe",
        "Steer/TargetAngle describe -children",
        "Steer/AdjustState describe",
        "Steer/SteerModeDiagnostic describe",
        "Steer/Mode describe",
        "Steer/Mode describe -children",
        "Steer/ModeChange describe",
        "Steer/RequestedAbsoluteTargetAngle describe",
        "Steer/TargetAngleIncrement describe",
        "Steer/TargetAngleIncrementDerived describe",
        "Steer/TargetAngleIncrementDerivedPost describe",
        "Steer/TargetAngleShift describe",
        "Steer/CurrentAbsDelta describe",
        "Steer/ZeroTargetAngleSwitch describe",
        "Steer/iMovement describe -children",
        "Steer/CntxtQualModEx describe -children",
    ],
    "Steering_WheelA": [
        "Steer/WheelA describe",
        "Steer/WheelA describe -children",
    ],
    "Steering_WheelB": [
        "Steer/WheelB describe",
        "Steer/WheelB describe -children",
    ],
    "Steering_WheelC": [
        "Steer/WheelC describe",
        "Steer/WheelC describe -children",
    ],
    "Steering_WheelD": [
        "Steer/WheelD describe",
        "Steer/WheelD describe -children",
    ],
    "SystemState_deep": [
        "SystemState describe -children",
        "SystemState/AllowDownTrace describe",
        "SystemState/AllowUpTrace describe",
        "SystemState/NextStateTrace describe",
        "SystemState/SystemControlTrace describe",
        "SystemState/ForceMaxTrace describe",
        "SystemState/ChargingEnabled describe",
        "SystemState/AutoStart describe",
        "SystemState/Event describe",
        "SystemState/State describe",
        "SystemState/CntxtSysCntrl describe",
        "SystemState/CntxtSysStateDn describe",
        "SystemState/CntxtSysStateUp describe",
    ],
    "TMS_deep": [
        "TMS describe -children",
        "TMS/ClntChilling describe",
        "TMS/ClntHeating describe",
        "TMS/CoolantChilling describe",
        "TMS/CoolantHeating describe",
        "TMS/CoolantPump describe",
        "TMS/ClntTempCold describe",
        "TMS/ClntTempHot describe",
        "TMS/ReqState describe",
        "TMS/CurrState describe",
        "TMS/ClntReservoir describe",
        "TMS/ClntTemp describe",
        "TMS/Chilling describe",
        "TMS/Heating describe",
        "TMS/Pump describe",
        "TMS/RequestedCoolantTemperature describe",
    ],
    "CANBusDrive_full": [
        "CANBusDrive describe -children",
        "CANBusDrive/cTransA describe -children",
        "CANBusDrive/cSteerA describe -children",
        "CANBusDrive/cWinchA describe -children",
        "CANBusDrive/cSpreader describe -children",
    ],
    "BMSAB_deep": [
        "BMSAB describe -children",
    ],
    "ChargerABC_deep": [
        "ChargerABC describe -children",
    ],
    "Secondary_deep": [
        "Secondary describe -children",
    ],
    "ProgMovCntrl_deep": [
        "ProgMovCntrl describe -children",
        "ProgMovCntrl/ProgMovNull describe -children",
        "ProgMovCntrl/steer_0 describe -children",
    ],
}


def main():
    probe = PLCProbe(port=RO_PORT)
    results = {}

    for group_name, commands in PROBE_TARGETS.items():
        print(f"\n=== Probing: {group_name} ===")
        group_results = []
        for cmd in commands:
            path = cmd.replace(" describe", "").replace(" describe -children", "")
            is_children = "-children" in cmd

            if is_children:
                resp = probe.describe_children(path)
            else:
                success, resp = probe.describe(path)

            status = (
                "FOUND"
                if (not is_children and success)
                or (
                    is_children
                    and "unknown_name" not in resp
                    and "connection_failed" not in resp
                )
                else "NOT_FOUND"
            )
            preview = resp[:200] if resp else "empty"
            group_results.append({"cmd": cmd, "status": status, "preview": preview})
            print(f"  {cmd}: {status}")
            if status == "FOUND" and len(preview) > 50:
                print(f"    -> {preview[:150]}...")

        results[group_name] = group_results
        time.sleep(0.3)  # Brief pause between groups

    probe.close()

    # Save results
    with open(
        r"C:\local\opencode\codesys\scripts\phase5_deep_probe_results.json", "w"
    ) as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n=== Results saved to phase5_deep_probe_results.json ===")


if __name__ == "__main__":
    main()
