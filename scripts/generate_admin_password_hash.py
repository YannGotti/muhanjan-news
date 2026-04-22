from __future__ import annotations

import sys
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print('Usage: python scripts/generate_admin_password_hash.py "your_password"')
        return 1

    password = sys.argv[1].strip()
    print(pwd_context.hash(password))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())