#!/usr/bin/env python3
"""Copy an existing Open WebUI data directory into Awesome WebUI.

The tool is intentionally conservative:
- it never edits the source directory;
- it backs up a non-empty target before overwriting files;
- it copies the data as-is and lets Awesome WebUI run its normal DB migrations
  on first startup.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import sqlite3
import sys
import tarfile
import time
from pathlib import Path


DEFAULT_EXCLUDES = {
    "__pycache__",
    ".DS_Store",
    "*.pyc",
    "*.pyo",
}

CACHE_EXCLUDES = {
    "cache",
    "cache/*",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate persistent Open WebUI data into an Awesome WebUI data directory."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Existing Open WebUI data directory, e.g. /app/backend/data or ./backend/data.",
    )
    parser.add_argument(
        "--target",
        default="backend/data",
        help="Awesome WebUI data directory to populate. Default: backend/data",
    )
    parser.add_argument(
        "--backup-dir",
        default=None,
        help="Directory where target backups are written. Default: parent of target.",
    )
    parser.add_argument(
        "--skip-cache",
        action="store_true",
        help="Skip cache/ files. This makes migration smaller and cache will be rebuilt.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be copied without changing anything.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not back up the existing target before copying.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting a non-empty target without a backup. Use with care.",
    )
    return parser.parse_args()


def is_empty_dir(path: Path) -> bool:
    return not path.exists() or not any(path.iterdir())


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def should_skip(relative_path: Path, excludes: set[str]) -> bool:
    value = relative_path.as_posix()
    name = relative_path.name
    return any(fnmatch.fnmatch(value, pattern) or fnmatch.fnmatch(name, pattern) for pattern in excludes)


def list_files(source: Path, excludes: set[str]) -> list[Path]:
    files = []
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if should_skip(relative, excludes):
            continue
        if path.is_file() or path.is_symlink():
            files.append(relative)
    return files


def create_backup(target: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{target.name}.awesome-migration-backup-{time.strftime('%Y%m%d%H%M%S')}.tar.gz"

    with tarfile.open(backup_path, "w:gz") as archive:
        archive.add(target, arcname=target.name)

    return backup_path


def copy_file(source_file: Path, target_file: Path) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    if source_file.is_symlink():
        if target_file.exists() or target_file.is_symlink():
            target_file.unlink()
        target_file.symlink_to(source_file.readlink())
        return
    shutil.copy2(source_file, target_file)


def sqlite_integrity_check(db_path: Path) -> str | None:
    if not db_path.exists():
        return None

    try:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            row = connection.execute("PRAGMA integrity_check").fetchone()
            return row[0] if row else "no result"
        finally:
            connection.close()
    except sqlite3.Error as exc:
        return f"failed: {exc}"


def main() -> int:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()
    backup_dir = Path(args.backup_dir).expanduser().resolve() if args.backup_dir else target.parent

    if not source.exists() or not source.is_dir():
        print(f"Source data directory does not exist: {source}", file=sys.stderr)
        return 2

    if is_relative_to(target, source):
        print("Target cannot be inside source.", file=sys.stderr)
        return 2

    if is_relative_to(source, target):
        print("Source cannot be inside target.", file=sys.stderr)
        return 2

    excludes = set(DEFAULT_EXCLUDES)
    if args.skip_cache:
        excludes.update(CACHE_EXCLUDES)

    files = list_files(source, excludes)
    if not files:
        print(f"No migratable files found in {source}", file=sys.stderr)
        return 2

    target_nonempty = not is_empty_dir(target)
    backup_path = None

    if target_nonempty and args.no_backup and not args.force:
        print(
            "Target is not empty. Remove --no-backup, or pass --force if you really want no backup.",
            file=sys.stderr,
        )
        return 2

    print("Awesome WebUI migration")
    print(f"  source: {source}")
    print(f"  target: {target}")
    print(f"  files:  {len(files)}")
    print(f"  cache:  {'skipped' if args.skip_cache else 'included'}")

    if args.dry_run:
        print("\nDry run. First files that would be copied:")
        for relative in files[:25]:
            print(f"  {relative}")
        if len(files) > 25:
            print(f"  ... and {len(files) - 25} more")
        return 0

    if target_nonempty and not args.no_backup:
        backup_path = create_backup(target, backup_dir)
        print(f"  backup: {backup_path}")

    target.mkdir(parents=True, exist_ok=True)
    for relative in files:
        copy_file(source / relative, target / relative)

    integrity = sqlite_integrity_check(target / "webui.db")
    report = {
        "source": str(source),
        "target": str(target),
        "copied_files": len(files),
        "backup": str(backup_path) if backup_path else None,
        "cache_skipped": bool(args.skip_cache),
        "sqlite_integrity_check": integrity,
        "created_at": int(time.time()),
        "next_step": "Start Awesome WebUI once so Alembic can upgrade webui.db to the Awesome WebUI schema.",
    }
    report_path = target / "awesome-webui-migration-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\nMigration copy complete.")
    if integrity:
        print(f"  webui.db integrity_check: {integrity}")
    print(f"  report: {report_path}")
    print("\nNext: start Awesome WebUI and let startup migrations finish before logging in.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
