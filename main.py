#!/usr/bin/env python3
"""Fix Human Sleep: Funniest Patch Note — entry program.

Writes one line of patch notes announcing that human sleep has been
fixed to /output/entry.txt. The line must pass the gate: UTF-8 text of
1 to 160 characters, not only white space, a single line.

Usage:
    python3 main.py [--output PATH] [--self-test]
"""

import argparse
import os
import sys

ENTRY = (
    "Fixed: sleep no longer crashes at 3 a.m.; users will no longer "
    "wake up to replay every embarrassing thing they said in 2014."
)

# Verified by reading the written output back: 124 characters, 124 bytes,
# single line, no trailing newline; sha256 of /output/entry.txt is
# 31cef7dd24a1777cfc5696066335e7ee77614709df8f988a5c7a132816b0c021.

DEFAULT_OUTPUT = "/output/entry.txt"


def validate(text):
    """Check the entry against the competition gate. Returns a list of
    problems (empty when valid)."""
    problems = []
    if not isinstance(text, str):
        return ["entry is not text"]
    if not (1 <= len(text) <= 160):
        problems.append(
            "length %d characters, must be 1-160" % len(text))
    if not text.strip():
        problems.append("entry is only white space")
    if text != text.strip():
        problems.append("leading or trailing white space")
    if "\n" in text or "\r" in text:
        problems.append("entry must be a single line")
    if any(ord(ch) < 0x20 and ch not in "\t" for ch in text):
        problems.append("entry contains control characters")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("entry is not valid UTF-8: %s" % exc)
    return problems


def write_entry(path):
    problems = validate(ENTRY)
    if problems:
        for problem in problems:
            print("gate failure: %s" % problem, file=sys.stderr)
        return 1
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(ENTRY)
    # Read it back: a write that silently truncates or mangles the line
    # must fail loudly here, not pass the gate check on a stale file.
    with open(path, "r", encoding="utf-8", newline="") as handle:
        written = handle.read()
    if written != ENTRY:
        print("gate failure: wrote %r, read back %r"
              % (ENTRY, written), file=sys.stderr)
        return 1
    print("wrote %d characters (%d bytes) to %s"
          % (len(ENTRY), len(ENTRY.encode("utf-8")), path))
    return 0


def self_test():
    """Validate the entry text and a round-trip write/read."""
    problems = validate(ENTRY)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        probe = os.path.join(tmp, "entry.txt")
        if write_entry(probe) != 0:
            problems.append("write failed")
        else:
            with open(probe, "rb") as handle:
                raw = handle.read()
            decoded = raw.decode("utf-8")
            if decoded != ENTRY:
                problems.append("round-trip mismatch")
            if raw.endswith(b"\n"):
                problems.append("output ends with a newline")
    if problems:
        for problem in problems:
            print("self-test FAIL: %s" % problem, file=sys.stderr)
        return 1
    print("self-test OK: %d chars, %d bytes, single line, no padding"
          % (len(ENTRY), len(ENTRY.encode("utf-8"))))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="where to write the entry (default: %(default)s)")
    parser.add_argument("--self-test", action="store_true",
                        help="validate the entry against the gate and exit")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    return write_entry(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
