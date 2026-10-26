"""Send commands to the esp32_nat_router serial CLI and print the replies.

Usage: py cli.py COM6 "help" ["show" ...]
Values like {UPLINK_PASSWORD} are filled in from ../.env and masked in the output.
"""
import pathlib
import sys
import time

import serial

ENV_FILE = pathlib.Path(__file__).resolve().parent.parent / ".env"


def load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def mask(text, secrets):
    for s in secrets:
        if s:
            text = text.replace(s, "********")
    return text


def read_until_quiet(s, quiet=1.0, limit=15.0):
    buf = bytearray()
    start = last = time.time()
    while time.time() - start < limit:
        chunk = s.read(4096)
        if chunk:
            buf += chunk
            last = time.time()
        elif time.time() - last > quiet:
            break
    return buf.decode("utf-8", errors="replace")


def main():
    port, commands = sys.argv[1], sys.argv[2:]
    env = load_env()
    secrets = [v for k, v in env.items() if "PASSWORD" in k]

    s = serial.Serial()
    s.port = port
    s.baudrate = 115200
    s.timeout = 0.2
    # Don't touch DTR/RTS: on USB-Serial-JTAG they can reset the chip
    s.dtr = False
    s.rts = False
    s.open()
    s.write(b"\r\n")
    read_until_quiet(s, quiet=0.5, limit=3)

    for cmd in commands:
        line = cmd.format(**env)
        s.write(line.encode() + b"\r\n")
        print(f">>> {mask(line, secrets)}")
        print(mask(read_until_quiet(s), secrets))
    s.close()


if __name__ == "__main__":
    main()
