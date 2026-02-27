"""Configuration models for the Minecraft environment manager."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MinecraftPaths:
    """Represents detected key directories for a Minecraft setup."""

    minecraft_dir: Path
    lunar_dir: Path
    saves_dir: Path
    logs_dir: Path
