import hashlib
import sys


EXPECTED_SHA256 = "bf942d07f3d95d83e83b5e2c3cf8c6512c6560040283d316e4e831729b3e30bd"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python tools/final_boss_validator.py <candidate_key>")
        return 2

    candidate = sys.argv[1].strip()
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    if digest == EXPECTED_SHA256:
        print("final_boss key accepted")
        return 0

    print("final_boss key rejected")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
