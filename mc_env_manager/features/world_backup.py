"""World backup feature module."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
from typing import Iterator

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeRemainingColumn

from mc_env_manager.utils.hashing import directory_fingerprint
from mc_env_manager.utils.size_formatter import format_size


class BackupError(Exception):
    """Raised when world backup cannot be completed."""


def _directory_size(directory: Path) -> int:
    """Calculate cumulative size of all files in a directory tree."""
    return sum(path.stat().st_size for path in directory.rglob("*") if path.is_file())


def _iter_worlds(saves_dir: Path) -> Iterator[Path]:
    """Yield world directories from saves folder."""
    for path in saves_dir.iterdir():
        if path.is_dir():
            yield path


def backup_worlds(saves_dir: Path, backup_dir: Path, console: Console | None = None) -> None:
    """Backup world folders with timestamped directories and change detection.

    This function never overwrites existing backups and skips unchanged worlds.

    Args:
        saves_dir: Minecraft saves directory.
        backup_dir: Root backup destination directory.
        console: Optional Rich console for CLI rendering.

    Raises:
        BackupError: If save directory is invalid or copy operation fails.
    """
    out = console or Console()

    if not saves_dir.is_dir():
        raise BackupError(f"Invalid saves directory: {saves_dir}")

    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_root: Path = backup_dir / f"backup_{timestamp}"
    target_root.mkdir(parents=True, exist_ok=False)

    worlds = list(_iter_worlds(saves_dir))
    if not worlds:
        out.print("[yellow]No worlds found to backup.[/yellow]")
        return

    total_bytes = 0
    copied_count = 0

    with Progress(
        TextColumn("[bold blue]Backing up worlds"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=out,
    ) as progress:
        task = progress.add_task("backup", total=len(worlds))
        for world in worlds:
            world_hash = directory_fingerprint(world)
            world_backup_base = backup_dir / world.name
            world_backup_base.mkdir(parents=True, exist_ok=True)
            hash_record = world_backup_base / ".last_hash"

            previous_hash = hash_record.read_text(encoding="utf-8").strip() if hash_record.exists() else ""
            if previous_hash == world_hash:
                out.print(f"[cyan]Skipping unchanged world:[/cyan] {world.name}")
                progress.advance(task)
                continue

            destination = target_root / world.name
            if destination.exists():
                raise BackupError(f"Refusing to overwrite backup destination: {destination}")

            try:
                shutil.copytree(world, destination)
            except OSError as exc:
                raise BackupError(f"Failed to backup world '{world.name}': {exc}") from exc

            hash_record.write_text(world_hash, encoding="utf-8")
            world_size = _directory_size(destination)
            total_bytes += world_size
            copied_count += 1
            out.print(f"[green]Backed up[/green] {world.name}: {format_size(world_size)}")
            progress.advance(task)

    out.print(f"[bold]Copied worlds:[/bold] {copied_count}")
    out.print(f"[bold]Backup size:[/bold] {format_size(total_bytes)}")
