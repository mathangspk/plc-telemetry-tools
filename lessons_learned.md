# CoDeSys Telemetry System: Lessons Learned & Engineering Insights

This document captures the critical engineering insights, architectural lessons, and debugging discoveries made during the development and testing of the Apollo 4 telemetry and performance testing pipeline.

---

## 1. PLC Connection Management & Socket Exhaustion

### The Issue
The CoDeSys ParseServerRW TCP server running on port `49870` has a very strict resource limit:
- **Maximum of 2 concurrent TCP connections.**
- High vulnerability to connection timeouts and deadlocks if a client fails to disconnect.
- Subsequent connections are rejected, leading to command execution failure and script hanging.

### Lessons Learned
- **Strict Cleanup Blocks:** Every script must wrap socket lifecycle management inside `try...finally` blocks to guarantee that `close` is called under all exit paths (including unexpected exceptions and keyboard interrupts).
- **Dedicated Connection Strategy:** Do not hold a single connection open for long periods. Establish a connection, run a command, read the response, and close immediately.
- **Port Split Architecture:** Use port `49870` strictly for commands that write state (e.g., registrations and clears). Use port `49880` (Read-Only) for querying structure and description, relieving resource pressure on port `49870`.

---

## 2. PLC Master CPU Overload & CANopen ZAPI Dropouts

### The Issue
The PLC Master CPU (ESX-3CS) performs high-speed motor control and CAN bus processing. 
- Sending telemetry configuration commands (like `Metric250ms register object=...`) in rapid succession causes the CPU usage to spike.
- This results in the driver dropping CAN frames, triggering the critical ZAPI motor controller error: **"NO CAN MSG. 80"**.
- This error drops communication and brings down the straddle carrier's drive system.

### Lessons Learned
- **Mandatory Rate-Limiting:** Enforce a strict delay of **50ms to 100ms** between successive command packets sent to the PLC.
- **Batching & Slicing:** Avoid registering large sets of signals in one block. Chunk signal configurations and wait for PLC stability.

---

## 3. Runtime Variable Mismatches & Naming Abbreviatons

### The Issue
Variable names in the PLC source code / design documents (e.g. `BatteryVoltage`, `ControllerTemperature`) often do not match the actual symbols exposed by the live TCP API. The live API exposes abbreviated paths:
- `BatteryVoltage` -> `BattVoltage`
- `ControllerTemperature` -> `CntrlTemp`
- `TwistlocksEnabled` -> `TwstEnbl`

### Lessons Learned
- **Runtime Discovery over Static Mapping:** Do not hardcode mappings in client tools without verification.
- Use live discovery commands (e.g., `describe -children`) to query the active variable hierarchy of the running PLC application.
- Maintain a dynamic remapping translation layer to reconcile abstract signal requests with physical PLC addresses.

---

## 4. Dual-Phase Instrumentation Verification

### The Issue
A command to register a signal may return success, but telemetry data for that signal may not actually emit, or the metric configuration may be silent.

### Lessons Learned
Always implement a **two-phase verification** after instrumentation:
1. **Verification of Membership (Describe):** Run `MetricX describe` immediately after registration to ensure the path is present in the metric's members group.
2. **Verification of Emission (Emit Check):** Open a connection to port `49890` (Emit) and read the active stream for a short duration. Parse the packets to confirm that active telemetry data for the registered signal is streaming.

---

## 5. Structured CSV Telemetry Design

### The Issue
Telemetry frames from the PLC arrive as nested JSON packets detailing groups of signal values at specific points in time. Recording them raw makes data validation and balancing analysis extremely difficult.

### Lessons Learned
- **Unified CSV Schema:** Flatten and group variables by mechanism (e.g. `trans_a`, `trans_b`) and write structured rows.
- **Standardized Timestamping:** Convert raw timestamps to relative milliseconds from the start of the test run to simplify transient and steady-state alignment.
- **Automated Validation:** Incorporate auto-validation (calculating current and torque deviations between motors) directly into the test execution tool to immediately verify system calibration status.
