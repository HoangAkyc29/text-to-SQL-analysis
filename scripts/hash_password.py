"""Print bcrypt hash for AUTH DB seed / user setup."""

from __future__ import annotations

import sys

import bcrypt


def main() -> None:
    password = sys.argv[1] if len(sys.argv) > 1 else "ChangeMe123!"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    print(hashed.decode("utf-8"))


if __name__ == "__main__":
    main()
