"""Size formatting utility helpers."""

from __future__ import annotations


def format_size(num_bytes: int) -> str:
    """Convert bytes to a human-readable string.

    Args:
        num_bytes: Raw size in bytes.

    Returns:
        Formatted size string.
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)

    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{num_bytes} B"
