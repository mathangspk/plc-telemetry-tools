# Live Telemetry Value Report: Secondary & ChargerABC

- **Captured At:** 2026-05-25 13:33:53
- **PLC Host:** 10.2.3.4

## ⚙️ Secondary Subsystem (5 Verified Signals)

| Signal Name | PLC Path | Live Value | Type |
| --- | --- | :---: | --- |
| `secondary_cntxtSgnMod` | `System/Secondary/CntxtSgnMod` | **ERROR** | `Unknown` |
| `secondary_secPwrMismatch` | `System/Secondary/SecPwrMismatch` | **N/A** | `EscAlarm` |
| `secondary_secPwrNotRun` | `System/Secondary/SecPwrNotRun` | **N/A** | `EscAlarm` |
| `secondary_secPwrNotRunMod` | `System/Secondary/SecPwrNotRunMod` | **N/A** | `SgnMod` |
| `secondary_secPwrWait` | `System/Secondary/SecPwrWait` | **N/A** | `AlarmAllowUp` |

## 🔋 ChargerABC Subsystem (7 Verified Signals)

| Signal Name | PLC Path | Live Value | Type |
| --- | --- | :---: | --- |
| `charger_chrgConn` | `System/ChargerABC/ChrgConn` | **N/A** | `SysCntrl` |
| `charger_chrgDiscon` | `System/ChargerABC/ChrgDiscon` | **N/A** | `Causal` |
| `charger_chrgOBCErr` | `System/ChargerABC/ChrgOBCErr` | **N/A** | `SysCntrl` |
| `charger_chrgStdby` | `System/ChargerABC/ChrgStdby` | **N/A** | `SysCntrl` |
| `charger_enblManualChrg` | `System/ChargerABC/EnblManualChrg` | **0** | `ValRefBool` |
| `charger_manualChrgCurr` | `System/ChargerABC/ManualChrgCurr` | **5.0** | `ValRefReal` |
| `charger_manualChrgVolt` | `System/ChargerABC/ManualChrgVolt` | **130.0** | `ValRefReal` |
