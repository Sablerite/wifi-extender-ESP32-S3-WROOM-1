# Installation

## Web Installer (Easiest)

Flash directly from your browser — no tools or command line required:

**[Open Web Installer](https://martin-ger.github.io/esp32_nat_router/)**

Requires a browser with Web Serial API. Select your firmware variant (WiFi or Ethernet), click "Connect & Install", and follow the prompts. All supported chips (ESP32, ESP32-C3, ESP32-C5, ESP32-C6, ESP32-S3, WT32-ETH01) are detected automatically.

## Updating the Binaries (OTA)

Once you have installed the firmware via this flashing procedure, you can easily update the binaries directly from the web interface. Download just the latest `esp32_nat_router.bin` image for your ESP32 chip. Go to the /config page and scroll down to the OTA update section. Select the binary file and click `Update Firmware`. The router will download it, check the file, install it, and reboot. All settings will be preserved. If the reboot fails, the router will fall back to the earlier version. 

## Clearing the Configuration
Even if you upload new binaries directly via the Web Installer or via esptool, all the config settings in NVRAM will be preserved. If you really want to clear them, use `factory_reset` from the CLI, press the BOOT-button for 10 seconds, or do a `esptool.py --chip esp32 erase_flash` (choose you ESP32 type here).

## Using esptool

Get and install [esptool](https://github.com/espressif/esptool):

```
cd ~
python3 -m pip install pyserial
git clone https://github.com/espressif/esptool
cd esptool
python3 setup.py install
```

## Flashing Instructions

Go to esp32_nat_router project directory and use the prebuild binary artifacts from the `firmware_*` directories. The binaries for the C3/C5/C6 are build for the JTAG USB-interface (/dev/ttyACM0). While flashing them on an older UART board (/dev/ttyUSB0) will work, the serial console will not be accessible. If you have such a board, rebuild with options `CONFIG_ESP_CONSOLE_UART_DEFAULT=y` and `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=n`.

### ESP32

```bash
esptool.py --chip esp32 \
--before default_reset --after hard_reset write_flash \
-z --flash_mode dio --flash_freq 40m --flash_size detect \
0x1000 firmware_esp32/bootloader.bin \
0x8000 firmware_esp32/partition-table.bin \
0xf000 firmware_esp32/ota_data_initial.bin \
0x20000 firmware_esp32/esp32_nat_router.bin
```

### ESP32-C3

```bash
esptool.py --chip esp32c3 \
--before default_reset --after hard_reset write_flash \
-z --flash_size detect \
0x0 firmware_esp32c3/bootloader.bin \
0x8000 firmware_esp32c3/partition-table.bin \
0xf000 firmware_esp32c3/ota_data_initial.bin \
0x20000 firmware_esp32c3/esp32_nat_router.bin
```

### ESP32-C5

```bash
esptool.py --chip esp32c5 \
--before default_reset --after hard_reset write_flash \
-z --flash_size detect \
0x2000 firmware_esp32c5/bootloader.bin \
0x8000 firmware_esp32c5/partition-table.bin \
0xf000 firmware_esp32c5/ota_data_initial.bin \
0x20000 firmware_esp32c5/esp32_nat_router.bin
```

### ESP32-C6

```bash
esptool.py --chip esp32c6 \
--before default_reset --after hard_reset write_flash \
-z --flash_size detect \
0x0 firmware_esp32c6/bootloader.bin \
0x8000 firmware_esp32c6/partition-table.bin \
0xf000 firmware_esp32c6/ota_data_initial.bin \
0x20000 firmware_esp32c6/esp32_nat_router.bin
```

### WT32-ETH01 (Ethernet uplink)

```bash
esptool.py --chip esp32 \
--before default_reset --after hard_reset write_flash \
-z --flash_mode dio --flash_freq 40m --flash_size detect \
0x1000 firmware_wt32_eth01/bootloader.bin \
0x8000 firmware_wt32_eth01/partition-table.bin \
0xf000 firmware_wt32_eth01/ota_data_initial.bin \
0x20000 firmware_wt32_eth01/esp32_nat_router.bin
```

### ESP32-S3

If especially the ESP32s with the JTAG-USB have problems during the flash process try the --no-stub option of esptool.

```bash
esptool.py --chip esp32s3 \
--before default_reset --after hard_reset write_flash \
-z --flash_size detect \
0x0 firmware_esp32s3/bootloader.bin \
0x8000 firmware_esp32s3/partition-table.bin \
0xf000 firmware_esp32s3/ota_data_initial.bin \
0x20000 firmware_esp32s3/esp32_nat_router.bin
```

## Available Artifacts

Each `firmware_*` directory contains:

- **`bootloader.bin`** - ESP32 bootloader
- **`partition-table.bin`** - Partition table
- **`ota_data_initial.bin`** - Initial OTA data (selects first OTA partition on boot)
- **`esp32_nat_router.bin`** - Main application firmware
- **`build_info.txt`** - Build metadata (timestamp, git hash, target)

