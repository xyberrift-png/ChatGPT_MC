"""Region file analysis feature."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from mc_env_manager.utils.size_formatter import format_size


class RegionFileInfo(TypedDict):
    """Typed structure for individual region file details."""

    path: str
    size_bytes: int
    size_human: str


class RegionReport(TypedDict):
    """Typed structure for region analysis result."""

    total_region_files: int
    top_5_largest: list[RegionFileInfo]
    total_size_bytes: int
    total_size_human: str
    abnormal_files: list[RegionFileInfo]


def analyze_region(region_path: Path) -> RegionReport:
    """Analyze a region directory and summarize region file metrics.

    Args:
        region_path: Path to a `region` directory.

    Returns:
        RegionReport containing file count, top largest files, total size, and abnormalities.
    """
    if not region_path.is_dir():
        raise FileNotFoundError(f"Region path not found: {region_path}")

    file_sizes: list[tuple[Path, int]] = []
    total_size = 0

    for path in region_path.glob("*.mca"):
        if not path.is_file():
            continue
        size = path.stat().st_size
        total_size += size
        file_sizes.append((path, size))

    file_sizes.sort(key=lambda item: item[1], reverse=True)

    top_5: list[RegionFileInfo] = [
        {"path": str(path), "size_bytes": size, "size_human": format_size(size)}
        for path, size in file_sizes[:5]
    ]

    abnormal: list[RegionFileInfo] = [
        {"path": str(path), "size_bytes": size, "size_human": format_size(size)}
        for path, size in file_sizes
        if size > 50 * 1024 * 1024
    ]

    return {
        "total_region_files": len(file_sizes),
        "top_5_largest": top_5,
        "total_size_bytes": total_size,
        "total_size_human": format_size(total_size),
        "abnormal_files": abnormal,
    }
