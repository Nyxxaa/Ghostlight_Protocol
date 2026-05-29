#!/usr/bin/env python3
"""Cipher helper for Ghostlight Protocol.

This helps with the mechanics. It does not choose the keys for you.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path


def vigenere(text: str, key: str, decrypt: bool) -> str:
    out: list[str] = []
    key_index = 0
    clean_key = "".join(ch.lower() for ch in key if ch.isalpha())
    if not clean_key:
        raise ValueError("Vigenere key must contain letters.")

    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            shift = ord(clean_key[key_index % len(clean_key)]) - ord("a")
            if decrypt:
                shift = -shift
            out.append(chr((ord(ch) - base + shift) % 26 + base))
            key_index += 1
        else:
            out.append(ch)
    return "".join(out)


def xor_b64(text: str, key: str, decrypt: bool) -> str:
    if not key:
        raise ValueError("XOR key must not be empty.")
    key_bytes = key.encode("utf-8")
    if decrypt:
        data = base64.b64decode(text)
    else:
        data = text.encode("utf-8")
    result = bytes(byte ^ key_bytes[index % len(key_bytes)] for index, byte in enumerate(data))
    if decrypt:
        return result.decode("utf-8")
    return base64.b64encode(result).decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ghostlight Protocol cipher helper.")
    parser.add_argument("method", choices=("vigenere", "xor-b64"))
    parser.add_argument("mode", choices=("encrypt", "decrypt"))
    parser.add_argument("key")
    parser.add_argument("text")
    args = parser.parse_args()

    text = args.text
    if text.startswith("@"):
        text = Path(text[1:]).read_text(encoding="utf-8")

    decrypt = args.mode == "decrypt"
    if args.method == "vigenere":
        print(vigenere(text, args.key, decrypt))
    else:
        print(xor_b64(text, args.key, decrypt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
