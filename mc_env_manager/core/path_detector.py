"""Windows path detection helpers for Minecraft and Lunar Client directories."""

from __future__ import annotations

from os import getenv
from pathlib import Path

from .config import MinecraftPaths


class PathDetectionError(Exception):
    """Raised when required Minecraft directories cannot be detected."""


def _resolve_windows_appdata(home: Path) -> Path:
    """Resolve the best APPDATA location for Windows environments.

    Args:
        home: Current user home path.

    Returns:
        Path to roaming appdata.
    """
    appdata_env = getenv("APPDATA")
    if appdata_env:
        return Path(appdata_env)
    return home / "AppData" / "Roaming"


def detect_minecraft_paths() -> MinecraftPaths:
    """Detect .minecraft and .lunarclient paths for a Windows user profile.

    Returns:
        MinecraftPaths: Structured paths for core directories.

    Raises:
        PathDetectionError: If required directories do not exist.
    """
    home: Path = Path.home()
    appdata: Path = _resolve_windows_appdata(home)

    minecraft_dir: Path = appdata / ".minecraft"
    lunar_dir: Path = home / ".lunarclient"
    saves_dir: Path = minecraft_dir / "saves"
    logs_dir: Path = minecraft_dir / "logs"

    missing: list[Path] = [
        path for path in (minecraft_dir, lunar_dir, saves_dir, logs_dir) if not path.exists()
    ]

    if missing:
        missing_str: str = ", ".join(str(path) for path in missing)
        raise PathDetectionError(f"Missing required directories: {missing_str}")

    return MinecraftPaths(
        minecraft_dir=minecraft_dir,
        lunar_dir=lunar_dir,
        saves_dir=saves_dir,
        logs_dir=logs_dir,
    )
