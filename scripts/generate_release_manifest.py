#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

CONTROL_FILES = {"MANIFEST.txt", "CHECKSUMS.sha256"}
EXCLUDED_DIRS = {".git", ".ai", ".tmp", "Doc", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"}
EXCLUDED_TOP_LEVEL = {"artifacts", "browser-evidence", "dist"}
SECRET_BASENAMES = {".env", ".env.local", ".env.production", ".env.staging", "auth.json", "credentials.json"}
SECRET_NAME_RE = re.compile(r"(?:secret|token|password|credential|private[_-]?key)", re.I)

@dataclass(frozen=True)
class Report:
    mode: str
    files: int
    checksums: int
    errors: tuple[str, ...]


def _is_secret_path(rel: Path) -> bool:
    name = rel.name
    if name in SECRET_BASENAMES:
        return True
    if name.startswith(".env.") and name != ".env.example":
        return True
    return bool(SECRET_NAME_RE.search(name))


def _excluded(rel: Path) -> bool:
    parts = set(rel.parts)
    if parts & EXCLUDED_DIRS:
        return True
    if rel.parts and rel.parts[0] in EXCLUDED_TOP_LEVEL:
        return True
    if rel.suffix in {".pyc", ".pyo", ".swp", ".swo", ".tmp", ".log"}:
        return True
    if rel.name in {".DS_Store"}:
        return True
    return False


def release_files(root: Path) -> tuple[list[Path], list[str]]:
    errors: list[str] = []
    files: list[Path] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if _excluded(rel) or rel.name in CONTROL_FILES:
            continue
        if path.is_symlink():
            errors.append(f"symlink not allowed: {rel.as_posix()}")
            continue
        if not path.is_file():
            continue
        if _is_secret_path(rel):
            continue
        files.append(rel)
    return sorted(files, key=lambda p: p.as_posix()), errors


def manifest_paths(root: Path, files: list[Path]) -> list[str]:
    paths = [p.as_posix() for p in files]
    for control in sorted(CONTROL_FILES):
        if (root / control).exists() or control in {"MANIFEST.txt", "CHECKSUMS.sha256"}:
            paths.append(control)
    return sorted(set(paths))


def checksum_text(root: Path, files: list[Path]) -> str:
    rows = []
    for rel in files:
        digest = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        rows.append(f"{digest}  ./{rel.as_posix()}")
    return "\n".join(rows) + ("\n" if rows else "")


def expected_manifest(root: Path) -> tuple[str, str, list[str]]:
    files, errors = release_files(root)
    paths = manifest_paths(root, files)
    return "\n".join(paths) + "\n", checksum_text(root, files), errors


def generate_manifest(root: Path, mode: Literal["write", "check"]) -> Report:
    manifest, checksums, errors = expected_manifest(root)
    manifest_path = root / "MANIFEST.txt"
    checksum_path = root / "CHECKSUMS.sha256"
    if mode == "write":
        if errors:
            return Report(mode, 0, 0, tuple(errors))
        manifest_path.write_text(manifest, encoding="utf-8")
        checksum_path.write_text(checksums, encoding="utf-8")
        return Report(mode, len(manifest.splitlines()), len(checksums.splitlines()), ())

    actual_manifest = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else ""
    actual_checksums = checksum_path.read_text(encoding="utf-8") if checksum_path.exists() else ""
    if actual_manifest != manifest:
        errors.append("MANIFEST.txt drift or missing entries")
    if actual_checksums != checksums:
        errors.append("CHECKSUMS.sha256 drift or hash mismatch")
    expected = set(manifest.splitlines())
    actual = {line.strip() for line in actual_manifest.splitlines() if line.strip()}
    unexpected = sorted(actual - expected)
    if unexpected:
        errors.extend(f"unexpected manifest entry: {item}" for item in unexpected)
    return Report(mode, len(manifest.splitlines()), len(checksums.splitlines()), tuple(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one of --write or --check")
    mode = "write" if args.write else "check"
    report = generate_manifest(Path(__file__).resolve().parents[1], mode)
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.errors:
        print(f"FAIL: {len(report.errors)} manifest issue(s)")
        return 2
    print(f"Release manifest {mode}: files={report.files} checksums={report.checksums} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
