"""Reset the board via the CH343 port's RTS line, then capture the app log on the native USB port.

Usage: py reset_and_listen.py COM5 COM6 [seconds] [outfile]
"""
import sys
import time

import serial

uart_port, usb_port = sys.argv[1], sys.argv[2]
seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 15
outfile = sys.argv[4] if len(sys.argv) > 4 else None

u = serial.Serial(uart_port, 115200, timeout=0.2)
u.dtr = False
u.rts = True
time.sleep(0.2)
u.rts = False

# The native USB device drops off the bus during reset; retry until it's back
usb = None
deadline = time.time() + 10
while usb is None and time.time() < deadline:
    try:
        usb = serial.Serial()
        usb.port = usb_port
        usb.baudrate = 115200
        usb.timeout = 0.2
        usb.dtr = False
        usb.rts = False
        usb.open()
    except serial.SerialException:
        usb = None
        time.sleep(0.1)
print("native USB reopened:", usb is not None)

buf = bytearray()
uart = bytearray()
end = time.time() + seconds
while time.time() < end:
    if usb:
        buf += usb.read(4096)
    uart += u.read(4096)
if usb:
    usb.write(b"\r\nhelp\r\n")
    t = time.time()
    while time.time() - t < 4:
        buf += usb.read(4096)
    usb.close()
u.close()

text = buf.decode("utf-8", errors="replace")
if outfile:
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(text)
print(text)
print("---- summary ----")
print("usb bytes:", len(buf), "| uart bytes:", len(uart), "| uart resets:", uart.count(b"rst:"))
print("panics:", text.count("Guru Meditation") + text.count("abort()"))
