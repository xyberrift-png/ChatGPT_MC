"""CLI entrypoint for Minecraft environment manager."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.table import Table

from mc_env_manager.core.path_detector import PathDetectionError, detect_minecraft_paths
from mc_env_manager.features.cleaner import CleanerReport, analyze_cleaner, iter_files
from mc_env_manager.features.region_analyzer import RegionReport, analyze_region
from mc_env_manager.features.world_backup import BackupError, backup_worlds
from mc_env_manager.utils.size_formatter import format_size


def _directory_size(directory: Path) -> int:
    """Calculate cumulative size of all files within a directory."""
    return sum(path.stat().st_size for path in directory.rglob("*") if path.is_file())


def _count_region_files(saves_dir: Path) -> int:
    """Count all region files within worlds in the saves directory."""
    return sum(1 for path in saves_dir.rglob("*.mca") if path.is_file())


def _latest_played_world(saves_dir: Path) -> str:
    """Find latest modified world directory name."""
    latest_name = "N/A"
    latest_mtime = -1.0

    for world in saves_dir.iterdir():
        if not world.is_dir():
            continue
        mtime = world.stat().st_mtime
        if mtime > latest_mtime:
            latest_mtime = mtime
            latest_name = world.name

    return latest_name


def show_environment_summary(console: Console) -> None:
    """Print a summary of the local Minecraft environment."""
    try:
        paths = detect_minecraft_paths()
    except PathDetectionError as exc:
        console.print(f"[red]Path detection error:[/red] {exc}")
        return

    total_worlds = sum(1 for path in paths.saves_dir.iterdir() if path.is_dir())
    total_size = _directory_size(paths.saves_dir)
    latest_world = _latest_played_world(paths.saves_dir)
    total_regions = _count_region_files(paths.saves_dir)

    table = Table(title="Environment Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Minecraft dir", str(paths.minecraft_dir))
    table.add_row("Lunar dir", str(paths.lunar_dir))
    table.add_row("Total worlds", str(total_worlds))
    table.add_row("Total size", format_size(total_size))
    table.add_row("Latest world", latest_world)
    table.add_row("Region files", str(total_regions))
    console.print(table)


def run_backup(console: Console) -> None:
    """Run world backup workflow."""
    try:
        paths = detect_minecraft_paths()
    except PathDetectionError as exc:
        console.print(f"[red]Path detection error:[/red] {exc}")
        return

    backup_dir = paths.minecraft_dir / "backups"
    try:
        backup_worlds(paths.saves_dir, backup_dir, console=console)
    except BackupError as exc:
        console.print(f"[red]Backup error:[/red] {exc}")


def run_cleaner_analysis(console: Console) -> None:
    """Run analyze-only cleaner workflow and write JSON report."""
    try:
        paths = detect_minecraft_paths()
    except PathDetectionError as exc:
        console.print(f"[red]Path detection error:[/red] {exc}")
        return

    scan_targets = [
        paths.minecraft_dir / "logs",
        paths.minecraft_dir / "crash-reports",
        paths.minecraft_dir / "shadercache",
        paths.minecraft_dir / "assets" / "objects",
    ]

    with Progress(
        TextColumn("[bold blue]Scanning directories"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("scan", total=len(scan_targets))
        for target in scan_targets:
            _ = sum(1 for _ in iter_files(target))
            progress.advance(task)

    report: CleanerReport = analyze_cleaner(paths.minecraft_dir, Path(__file__).resolve().parent / "reports")

    table = Table(title="Cleaner Analysis (Analyze Only)")
    table.add_column("Category", style="cyan")
    table.add_column("File Count", style="green")
    table.add_row("Safe to delete", str(len(report["safe_to_delete"])))
    table.add_row("Large files", str(len(report["large_files"])))
    table.add_row("Important", str(len(report["important"])))
    console.print(table)
    console.print("[bold]Report:[/bold] mc_env_manager/reports/clean_report.json")


def run_region_analysis(console: Console) -> None:
    """Prompt for region directory and analyze region files."""
    region_input = console.input("Enter full path to region directory: ").strip().strip('"')
    if not region_input:
        console.print("[yellow]No path provided.[/yellow]")
        return

    region_path = Path(region_input)
    try:
        report: RegionReport = analyze_region(region_path)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        return

    summary = Table(title="Region Analysis")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", style="green")
    summary.add_row("Total region files", str(report["total_region_files"]))
    summary.add_row("Total size", report["total_size_human"])
    summary.add_row("Abnormal files (>50MB)", str(len(report["abnormal_files"])))
    console.print(summary)

    largest_table = Table(title="Top 5 Largest Region Files")
    largest_table.add_column("Path", style="magenta")
    largest_table.add_column("Size", style="green")
    for item in report["top_5_largest"]:
        largest_table.add_row(item["path"], item["size_human"])
    console.print(largest_table)


def main() -> None:
    """CLI loop."""
    console = Console()

    while True:
        console.print(
            Panel.fit(
                "[bold]Minecraft Environment Manager[/bold]\n"
                "1. Show environment summary\n"
                "2. Backup worlds\n"
                "3. Analyze Minecraft cleaner\n"
                "4. Analyze region\n"
                "5. Exit",
                border_style="blue",
            )
        )

        choice = console.input("Select an option: ").strip()

        if choice == "1":
            show_environment_summary(console)
        elif choice == "2":
            run_backup(console)
        elif choice == "3":
            run_cleaner_analysis(console)
        elif choice == "4":
            run_region_analysis(console)
        elif choice == "5":
            console.print("[bold green]Goodbye.[/bold green]")
            break
        else:
            console.print("[yellow]Invalid selection. Please choose 1-5.[/yellow]")


if __name__ == "__main__":
    main()
