"""
Unified Command-Line Interface for the YouTube Shorts Automation Studio.
Styled with Google-grade terminal ergonomics and clean progress tracking.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import argparse
import uvicorn
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.core.config import settings
from src.core.database import get_all_shorts, count_today_uploads
from src.core.orchestrator import ShortsOrchestrator
from src.modules.research.niche_manager import NicheManager

console = Console()


def print_banner():
    console.print(
        Panel.fit(
            "[bold white]YouTube Shorts Automation Studio[/bold white]\n"
            "[dim]Powered by Gemini 2.0 Flash, Edge-TTS, and Ssemble AI Engine[/dim]",
            border_style="blue",
        )
    )


def list_niches():
    nm = NicheManager()
    table = Table(title="Configured High-RPM Niches", border_style="blue")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold white")
    table.add_column("RPM Tier", style="green")
    table.add_column("Default Voice", style="yellow")
    table.add_column("Weight", justify="right")

    for n in nm.get_all_niches():
        table.add_row(
            n.get("id"),
            n.get("name"),
            n.get("rpm_tier", "Normal"),
            n.get("default_voice", settings.default_voice),
            str(n.get("weight", 1)),
        )
    console.print(table)


def show_history(limit: int = 15):
    shorts = get_all_shorts(limit=limit)
    if not shorts:
        console.print("[dim]No shorts recorded in history yet.[/dim]")
        return

    table = Table(title=f"Recent Generation History (Last {limit})", border_style="blue")
    table.add_column("Date", style="dim", no_wrap=True)
    table.add_column("Niche", style="cyan")
    table.add_column("Title", style="bold white")
    table.add_column("Status", style="yellow")
    table.add_column("Mode", style="magenta")
    table.add_column("YouTube Link", style="blue")

    for s in shorts:
        yt_link = f"https://youtu.be/{s['youtube_video_id']}" if s.get("youtube_video_id") else "-"
        status_style = "green" if s.get("status") == "uploaded" else "yellow"
        table.add_row(
            str(s.get("created_at", ""))[:16],
            s.get("niche_id", ""),
            (s.get("title") or s.get("topic", ""))[:40],
            f"[{status_style}]{s.get('status')}[/{status_style}]",
            s.get("mode", ""),
            yt_link,
        )
    console.print(table)


def run_studio_server():
    import subprocess
    import threading
    import webbrowser
    import time
    from pathlib import Path

    web_dir = Path(__file__).resolve().parent.parent / "web"

    def run_next():
        cmd = "npm.cmd run start" if (web_dir / ".next").exists() else "npm.cmd run dev"
        subprocess.run(cmd, cwd=str(web_dir), shell=True)

    t = threading.Thread(target=run_next, daemon=True)
    t.start()

    console.print(f"[bold green]Starting Next.js Google M3 Studio on http://localhost:3000[/bold green]")
    console.print(f"[dim]Backend FastAPI service active on http://{settings.studio_host}:{settings.studio_port}[/dim]")

    def open_browser():
        time.sleep(2.5)
        webbrowser.open("http://localhost:3000")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("src.ui.server:app", host=settings.studio_host, port=settings.studio_port, reload=False)


def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation Studio CLI")
    parser.add_argument("--niche", type=str, help="Target niche ID (e.g. dark_history, psychology, wealth_finance)")
    parser.add_argument("--mode", type=str, default="local-studio", choices=["local-studio", "ssemble-ai", "ssemble-clip"], help="Assembly mode")
    parser.add_argument("--topic", type=str, help="Optional specific topic angle to cover")
    parser.add_argument("--dry-run", action="store_true", help="Generate video locally without uploading to YouTube")
    parser.add_argument("--privacy", type=str, default="unlisted", choices=["public", "unlisted", "private"], help="YouTube upload privacy")
    parser.add_argument("--list-niches", action="store_true", help="Display all configured niches")
    parser.add_argument("--history", action="store_true", help="Display generation and upload history")
    parser.add_argument("--ui", action="store_true", help="Launch the Google Material Design 3 Web Studio")

    args = parser.parse_args()

    if args.ui:
        run_studio_server()
        return

    print_banner()

    if args.list_niches:
        list_niches()
        return

    if args.history:
        show_history()
        return

    # Run Generation Pipeline
    orc = ShortsOrchestrator()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Initializing pipeline...", total=100)

        def on_progress(msg: str, pct: int):
            progress.update(task, description=f"[cyan]{msg}", completed=pct)

        try:
            result = orc.run_pipeline(
                niche_id=args.niche,
                mode=args.mode,
                topic_hint=args.topic,
                dry_run=args.dry_run,
                privacy_status=args.privacy,
                progress_callback=on_progress,
            )
        except Exception as e:
            console.print(f"\n[bold red]Pipeline Error:[/bold red] {e}")
            sys.exit(1)

    console.print("\n[bold green]Short Generation Complete![/bold green]")
    console.print(f"[bold white]Title:[/bold white] {result['script']['title']}")
    console.print(f"[bold white]Hook:[/bold white] {result['script']['hook']}")
    console.print(f"[bold white]Video Output:[/bold white] {result['video_path']}")
    if result.get("youtube"):
        console.print(f"[bold green]Published to YouTube:[/bold green] {result['youtube'].get('url')}")
    elif args.dry_run:
        console.print("[yellow]Dry-run enabled: Skipped YouTube upload.[/yellow]")


if __name__ == "__main__":
    main()
