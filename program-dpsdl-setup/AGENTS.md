**Firmware Flash (Legacy Device)**
- Target: Legacy device; follow command.png howto flow (W N: B, T, A, D, E, C).
- HEX source: Use files under `Firmware/*.hex`.

**Current State**
- BPS: Set to 115200 on ETH via `SWC24` before data transfer. Response echoes `SWCdd`.
- START DOWNLOAD: `SWNT` uses count of type-00 data lines (5 digits).
- DOWNLOAD CODE: `SWND` LENGTH `dd` is the decimal 2‑digit byte count of DATAs.
- ADDRESS: On type-04 records, send `SWNA` + upper 2‑byte address hex.
- END: Finish with `SWNE` and expect OK (`…N0Q`).
- Observed error: 2nd data line returns NG, e.g. response `SWN1D7Q` after `SWND6400…` (old logs), and after fixes still NG.

**To Verify Next**
- Confirm what `DOWNLOAD NUMBER (ddddd)` must be:
  - Currently: number of type‑00 lines.
  - Alternative: total data bytes across type‑00 lines.
- Confirm DATAs encoding expectation:
  - ASCII HEX (current) vs raw binary bytes.
- Confirm if an initial `A` (address) is required before first `D` even when no 04 record yet.
- Capture early exchange samples (T, first A/D pairs) and exact NG codes.

**Known Constants**
- `dd` in `SWNDdd…` is decimal 2 digits (data byte count).
- BPS index 4 = 115200 (LAN path).

**Runbook (Operator)**
- Select HEX (auto-picks first under `Firmware/`).
- Click “Start Firmware Upgrade” → device enters BOOT (3 tries `SWNB`).
- Click “Confirm Flash” within 10s → sends `C4`, `T`, then sequence of `A`/`D`, finally `E`.

**Open Questions**
- Exact spec for `DOWNLOAD NUMBER` on legacy device?
- Any timing constraints between packets (need inter‑record delay > 20 ms)?
- Meaning of NG code `1D7` in responses (mapping table)?
