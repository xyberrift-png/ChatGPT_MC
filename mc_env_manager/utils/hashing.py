"""File hashing utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path


def file_hash(path: Path, algorithm: str = "sha256") -> str:
    """Generate hash digest for a file.

    Args:
        path: File path to hash.
        algorithm: Hash algorithm supported by hashlib.

    Returns:
        Hex digest string.

    Raises:
        FileNotFoundError: If the path is not a file.
        ValueError: If algorithm is invalid.
    """
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    hasher = hashlib.new(algorithm)
    with path.open("rb") as file_obj:
        while chunk := file_obj.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def directory_fingerprint(directory: Path) -> str:
    """Create a stable fingerprint hash for a directory contents tree.

    Args:
        directory: Directory to fingerprint.

    Returns:
        Hex digest describing file paths, sizes, mtimes, and file contents.

    Raises:
        FileNotFoundError: If directory does not exist or is not a directory.
    """
    if not directory.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")

    hasher = hashlib.sha256()
    files = sorted(path for path in directory.rglob("*") if path.is_file())
    for file_path in files:
        relative = file_path.relative_to(directory)
        stat = file_path.stat()
        metadata = f"{relative.as_posix()}|{stat.st_size}|{int(stat.st_mtime)}"
        hasher.update(metadata.encode("utf-8"))

        with file_path.open("rb") as file_obj:
            while chunk := file_obj.read(1024 * 1024):
                hasher.update(chunk)

    return hasher.hexdigest()
