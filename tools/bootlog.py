"""Reset the ESP32-S3 via RTS and capture boot output from a serial port.

Usage: py -I bootlog.py COM5 [seconds] [outfile]
"""
import sys
import time

import serial

port = sys.argv[1]
seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 15
outfile = sys.argv[3] if len(sys.argv) > 3 else None

s = serial.Serial(port, 115200, timeout=0.2)
# DTR high-level = IO0 high (normal boot); pulse RTS to pull EN low -> reset
s.dtr = False
s.rts = True
time.sleep(0.2)
s.rts = False

buf = bytearray()
end = time.time() + seconds
while time.time() < end:
    buf += s.read(4096)
s.close()

text = buf.decode("utf-8", errors="replace")
if outfile:
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(text)
print(text)
print("---- summary ----")
print("bytes:", len(buf))
print("resets (rst:):", text.count("rst:"))
print("panics:", text.count("Guru Meditation") + text.count("abort()"))
