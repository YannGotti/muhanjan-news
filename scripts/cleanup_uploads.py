from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.core.config import settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.submission import Attachment  # noqa: E402


def collect_referenced_files() -> set[Path]:
    db = SessionLocal()
    try:
        rows = db.query(Attachment.storage_path).all()
        return {Path(row[0]).resolve() for row in rows if row and row[0]}
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Cleanup orphan files in storage/uploads")
    parser.add_argument("--delete", action="store_true", help="Delete orphan files instead of only showing them")
    args = parser.parse_args()

    uploads_dir = settings.upload_dir_path.resolve()
    referenced = collect_referenced_files()

    all_files = {path.resolve() for path in uploads_dir.iterdir() if path.is_file()}
    orphan_files = sorted(all_files - referenced)

    print(f"Uploads dir: {uploads_dir}")
    print(f"Referenced in DB: {len(referenced)}")
    print(f"Files on disk: {len(all_files)}")
    print(f"Orphans: {len(orphan_files)}")

    for path in orphan_files:
        print(path)
        if args.delete:
            try:
                path.unlink()
            except Exception as exc:
                print(f"FAILED to delete {path}: {exc}")

    if args.delete:
        print("Cleanup finished.")
    else:
        print("Dry run finished. Use --delete to remove orphan files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
