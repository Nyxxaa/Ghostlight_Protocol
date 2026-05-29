#!/usr/bin/env python3
"""Small Base64 helper for Ghostlight Protocol."""

from __future__ import annotations

import argparse
import base64


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode a Base64 signal.")
    parser.add_argument("payload", help="Base64 text to decode")
    args = parser.parse_args()

    print(base64.b64decode(args.payload).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
