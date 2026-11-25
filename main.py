#!/usr/bin/env python3
"""Fix Human Sleep: Funniest Patch Note.

Writes the entry — one line of patch notes announcing that human sleep
has been fixed — to /output/entry.txt.

The line has to clear the gate before anything is written: UTF-8 text,
between 1 and 160 characters, exactly one line, with no padding at
either end and no trailing newline in the file.

    python3 main.py                          writes /output/entry.txt
    python3 main.py --self-test              checks the line, writes nothing
    python3 main.py --output somewhere.txt   writes somewhere else
"""

import sys
import tempfile
from pathlib import Path

NOTE = (
    "Fixed: sleep no longer crashes at 3 a.m.; users will no longer "
    "wake up to replay every embarrassing thing they said in 2014."
)

LIMIT = 160
TARGET = Path("/output/entry.txt")


def faults(line):
    """Return every way `line` breaks the gate, or [] when it clears it."""
    bad = []
    if len(line) < 1 or len(line) > LIMIT:
        bad.append("line is %d characters; the gate allows 1-%d"
                   % (len(line), LIMIT))
    if line != line.strip():
        bad.append("line has leading or trailing whitespace")
    if not line.strip():
        bad.append("line is blank")
    if "\n" in line or "\r" in line:
        bad.append("line spans more than one line")
    for ch in line:
        if ord(ch) < 32 and ch != "\t":
            bad.append("line holds a control character")
            break
    try:
        line.encode("utf-8")
    except UnicodeEncodeError as err:
        bad.append("line is not UTF-8: %s" % err)
    return bad


def emit(path):
    """Write NOTE to `path` after it clears the gate, then read it back."""
    found = faults(NOTE)
    if found:
        for item in found:
            print("gate: %s" % item, file=sys.stderr)
        return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(NOTE, encoding="utf-8")
    again = path.read_text(encoding="utf-8")
    if again != NOTE:
        print("gate: wrote %r but read back %r" % (NOTE, again),
              file=sys.stderr)
        return 1
    print("wrote %d chars (%d bytes) -> %s"
          % (len(NOTE), len(NOTE.encode("utf-8")), path))
    return 0


def check_only():
    """Prove the line and a full write/read round trip, writing nothing."""
    found = faults(NOTE)
    with tempfile.TemporaryDirectory() as folder:
        probe = Path(folder) / "entry.txt"
        if emit(probe) != 0:
            found.append("round-trip write failed")
        elif probe.read_bytes().endswith(b"\n"):
            found.append("file ends with a newline")
    if found:
        for item in found:
            print("self-test FAIL: %s" % item, file=sys.stderr)
        return 1
    print("self-test OK: %d chars, %d bytes, one line, no padding"
          % (len(NOTE), len(NOTE.encode("utf-8"))))
    return 0


def run(argv):
    args = list(argv)
    if "--self-test" in args:
        return check_only()
    out = TARGET
    if "--output" in args:
        where = args.index("--output")
        if where + 1 >= len(args):
            print("usage: main.py [--self-test] [--output PATH]",
                  file=sys.stderr)
            return 2
        out = Path(args[where + 1])
    return emit(out)


sys.exit(run(sys.argv[1:]))
