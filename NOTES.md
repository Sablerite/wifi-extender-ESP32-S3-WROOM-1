# ESP32-S3 Wi-Fi extender (esp32_nat_router) — notes

**Status (2026-10-27): working.** Flashed, boots cleanly, connected to the home Wi-Fi (got 192.168.1.122) and has internet (ping 8.8.8.8: 4/4, ~25 ms). It broadcasts its own WPA2/WPA3 network.

Location: `C:\Users\Sablerite\Documents\Whimsical Oracles\wifi-extender\esp32-extender` (moved here from `C:\Users\Sablerite\esp32-extender`). All paths below are relative to this folder.

## Hardware

- ESP32-S3-WROOM-1, MON16R8. esptool reports: ESP32-S3 (QFN56) rev v0.2, 16MB quad flash (manuf. 0xc2 / dev 0x2018), 8MB embedded PSRAM, MAC 80:b5:4e:c6:17:04 (AP MAC ...:05)
- Two USB-C ports:
  - **COM5**: WCH CH343 USB-UART bridge. Used for **flashing**, and its RTS line resets the chip. It only shows ROM boot messages.
  - **COM6**: the chip's native USB (USB-Serial-JTAG, VID 303A PID 1001). This is where the **CLI and app logs** are.
  - COM3/COM4 are Bluetooth serial, not the board.

## Firmware

- Project: martin-ger/esp32_nat_router — **app version 2.4.22**, ESP-IDF v5.5.4, built 2026-10-21 (build_info git hash c618b13)
- The repo has **no GitHub Releases or tags**. Prebuilt binaries are committed in the repo under `firmware_esp32s3/`.
  Downloaded from commit `119e0a3d98a7c580a0fd119fde27d189cda25d39` ("firmware build for lastest changes", 2026-10-21) into `firmware/firmware_esp32s3/`.
- SHA-256 (first 16 hex chars): bootloader.bin `77857760DC1CF751`, partition-table.bin `D0454414B3A3C789`, ota_data_initial.bin `7D2C7AC4888BFD75`, esp32_nat_router.bin `0AD326DBE49A2903`
- Offsets come from the project's Installation wiki (`firmware/wiki-Installation.md`) and match the web-installer manifest (`firmware/manifest_esp32_wifi.json`):
  bootloader **0x0**, partition table **0x8000**, OTA data **0xF000**, app **0x20000**.
- Build config: flash mode DIO, **PSRAM not enabled** (so the octal-PSRAM / `qio_opi` panic from other projects doesn't apply, and no flash-mode workaround was needed), console = USB-Serial-JTAG.

## Tools

- Python 3.14.7 through the `py` launcher (`python` on PATH is only the Microsoft Store stub)
- `py -m pip install --upgrade --user esptool pyserial` → esptool 5.6.0, pyserial 3.5
- `tools/bootlog.py`: reset via COM5 and capture ROM output
- `tools/reset_and_listen.py COM5 COM6 [sec] [file]`: reset via COM5, capture the app log from COM6, then send `help`
- `tools/cli.py COM6 "cmd" ...`: send CLI commands. `{UPLINK_SSID}`-style placeholders are filled from `.env`, and passwords are masked in the output

## Exact flash commands used (run from `firmware/`)

```powershell
py -m esptool --chip esp32s3 -p COM5 erase-flash
py -m esptool --chip esp32s3 -p COM5 --before default-reset --after hard-reset write-flash -z --flash-size detect 0x0 firmware_esp32s3/bootloader.bin 0x8000 firmware_esp32s3/partition-table.bin 0xf000 firmware_esp32s3/ota_data_initial.bin 0x20000 firmware_esp32s3/esp32_nat_router.bin
```

Auto-reset worked (no BOOT/RESET buttons needed). All regions passed hash verification. `--flash-size detect` → 16MB.

## Final settings

| Setting | Value |
|---|---|
| Uplink (STA) SSID | `PLDTHOMEFIBR5ec30` (2.4 GHz, channel 1) |
| Uplink IP | 192.168.1.122 via DHCP, gateway 192.168.1.1 |
| Extender AP SSID | `private_banana` |
| AP security | WPA2/WPA3 (password protected, never open) |
| AP subnet | 192.168.4.1/24, DHCP for clients, NAT on |
| Web UI | enabled, port 80, reachable from AP + STA + VPN, **password protected** (`set_router_password`, same as AP password) |
| TX power / country | 20 dBm / `01` (world-safe) |
| Hostname | esp32-nat-router |

Passwords are **not** in this file. They're in `.env` (`UPLINK_PASSWORD`, `AP_PASSWORD`), which `.gitignore` excludes. The AP password was originally a 20-character random string; on 2026-10-27 it was changed to a user-chosen 8-character password.

Commands used:
```text
set_sta <UPLINK_SSID> <UPLINK_PASSWORD>
set_ap <AP_SSID> <AP_PASSWORD>
set_router_password <AP_PASSWORD>
(reset)
show status
```

## How to change settings later

- **Web UI**: join `private_banana`, open http://192.168.4.1 (or http://esp32-nat-router.local) and log in with the AP password. Because the web UI is also bound to the STA side, it's reachable from the home LAN at http://192.168.1.122 too.
  - To allow it only from the extender's own network: `web_ui bind ap`
- **Serial CLI**: plug into the native USB port (COM6), then `py tools/cli.py COM6 "show config"`, or use PuTTY at 115200 (PuTTY gets line editing; plain terminals don't).
  - If COM6 doesn't answer, reset the board first (`tools/reset_and_listen.py COM5 COM6`, or press RESET) and then send commands.
  - Useful commands: `show status`, `show config`, `scan`, `set_sta`, `set_ap`, `set_router_password`, `set_tx_power`, `set_wifi_country PH`, `restart`, `factory_reset`.
  - After `set_sta`/`set_ap`, run `restart` for the changes to take effect.

## How to re-flash

1. Run the two commands above over COM5. Settings live in NVS and **survive** a plain write-flash; `erase-flash` or `factory_reset` wipes them.
2. Or OTA: web UI → /config → OTA section → upload a newer `firmware_esp32s3/esp32_nat_router.bin`.
3. If esptool can't connect: hold BOOT, tap RESET, release BOOT, then retry.

## Problems hit

1. **No GitHub Releases** → used the prebuilt binaries committed in the repo (official source), pinned to the commit above.
2. **README only shows the classic-ESP32 command** → took the S3 offsets from the official wiki + installer manifest.
3. **`py -I` hides `--user` site-packages** → ran my own helper scripts without `-I`.
4. **CLI isn't on COM5**: the S3 build's console is native USB. Fixed by plugging into the second USB-C port (COM6).
5. **COM6 stayed silent at first** when opened while the app was already running. After a reset via COM5's RTS line, the CLI answered normally.
6. **Uplink wouldn't connect** (disconnect/retry every ~3 s): the SSID was given as `PLDTHOMEFIBER5ec30`, but `scan` showed the real network is `PLDTHOMEFIBR5ec30` (no "E"). After the fix it connected straight away.
7. `netsh wlan` scanning from the PC needs Windows Location services; I didn't change that setting.
8. No boot loops or Guru Meditation panics at any point: 0 panics across every captured log (`bootlog_com5.txt`, `bootlog_usb.txt`, `bootlog_configured.txt`).

## Notes

- The ESP32-S3 only does **2.4 GHz**. Clients on the extender get their own 192.168.4.x subnet (NAT), so it isn't a seamless mesh: devices see two separate networks.
- Expect real throughput of a few Mbps up to ~15–20 Mbps. That's fine for browsing and video, not for big downloads.

## Changes

- 2026-10-27: renamed the extender AP from `PLDTHOMEFIBER5ec30_EXT` to `private_banana` (same password). Verified after restart: uplink connected, 0 panics.

- 2026-10-27: changed the AP password and web UI password (`set_ap` + `set_router_password`) to a new user-chosen value, stored in `.env`. Verified after restart: uplink connected, 0 panics.

