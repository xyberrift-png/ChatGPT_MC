"""Minecraft cleaner analysis-only feature."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, TypedDict

from mc_env_manager.utils.size_formatter import format_size


@dataclass(frozen=True)
class FileReport:
    """Represents metadata for a scanned file."""

    path: str
    size_bytes: int
    size_human: str
    category: str


class CleanerReport(TypedDict):
    """Typed structure for cleaner analysis output."""

    safe_to_delete: list[dict[str, str | int]]
    large_files: list[dict[str, str | int]]
    important: list[dict[str, str | int]]


def iter_files(directory: Path) -> Iterator[Path]:
    """Yield files recursively when a directory exists."""
    if not directory.is_dir():
        return
    for path in directory.rglob("*"):
        if path.is_file():
            yield path


def analyze_cleaner(minecraft_dir: Path, report_dir: Path) -> CleanerReport:
    """Analyze removable and important files without deleting anything.

    Args:
        minecraft_dir: Root .minecraft directory.
        report_dir: Directory for generated JSON report.

    Returns:
        CleanerReport classification mapping for scanned files.
    """
    scan_targets: dict[str, str] = {
        "logs": "safe_to_delete",
        "crash-reports": "safe_to_delete",
        "shadercache": "safe_to_delete",
        "assets/objects": "important",
    }

    safe_to_delete: list[FileReport] = []
    large_files: list[FileReport] = []
    important: list[FileReport] = []

    for relative, category in scan_targets.items():
        for file_path in iter_files(minecraft_dir / Path(relative)):
            size = file_path.stat().st_size
            report = FileReport(
                path=str(file_path),
                size_bytes=size,
                size_human=format_size(size),
                category=category,
            )

            if category == "important":
                important.append(report)
            else:
                safe_to_delete.append(report)

            if size >= 100 * 1024 * 1024:
                large_files.append(report)

    result: CleanerReport = {
        "safe_to_delete": [asdict(item) for item in safe_to_delete],
        "large_files": [asdict(item) for item in large_files],
        "important": [asdict(item) for item in important],
    }

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "clean_report.json"
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result
