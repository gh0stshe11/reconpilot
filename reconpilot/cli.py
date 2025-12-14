"""Command-line interface for ReconPilot"""
import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from reconpilot import __version__
from reconpilot.config import CONFIG_DIR, Config, ensure_directories
from reconpilot.core.database import Database
from reconpilot.core.events import EventBus
from reconpilot.core.orchestrator import Orchestrator, ScanConfig, ScanMode
from reconpilot.reports.generator import ReportGenerator
from reconpilot.tools.registry import create_default_registry

app = typer.Typer(
    name="reconpilot",
    help="🎯 AI-Powered Reconnaissance Orchestrator for Penetration Testing",
    add_completion=False,
)
console = Console()


def print_banner():
    """Print the ReconPilot banner"""
    banner = """
[bold cyan]
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗         ║
║     ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║         ║
║     ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║         ║
║     ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║         ║
║     ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║         ║
║     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝         ║
║                                                           ║
║              [bold white]PILOT[/bold white] - AI-Powered Recon Orchestrator          ║
║                     [dim]v{version}[/dim]                            ║
╚═══════════════════════════════════════════════════════════╝
[/bold cyan]
    """.format(version=__version__)
    console.print(banner)


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target domain, IP, or URL"),
    mode: str = typer.Option("auto", help="Scan mode: auto, interactive, passive"),
    scope: Optional[list[str]] = typer.Option(None, help="In-scope domains/IPs"),
    exclude: Optional[list[str]] = typer.Option(None, help="Exclude domains/IPs"),
    passive_only: bool = typer.Option(False, help="Use only passive tools"),
    stealth: bool = typer.Option(False, help="Enable stealth mode"),
    max_parallel: int = typer.Option(3, help="Max parallel tasks"),
    timeout: int = typer.Option(300, help="Task timeout in seconds"),
    dashboard: bool = typer.Option(True, help="Show TUI dashboard"),
):
    """Start a reconnaissance scan"""
    print_banner()
    ensure_directories()

    # Create scan config
    scan_mode = ScanMode(mode.lower())
    config = ScanConfig(
        target=target,
        mode=scan_mode,
        scope=scope or [],
        exclude=exclude or [],
        max_parallel=max_parallel,
        passive_only=passive_only,
        stealth=stealth,
        timeout=timeout,
    )

    console.print(f"[bold green]🎯 Starting scan of:[/bold green] {target}")
    console.print(f"[dim]Mode: {mode} | Max parallel: {max_parallel}[/dim]\n")

    # Initialize components
    registry = create_default_registry()
    event_bus = EventBus()

    if dashboard:
        # Run with TUI dashboard
        from reconpilot.dashboard.app import ReconPilotDashboard
        
        app_instance = ReconPilotDashboard(config, registry, event_bus)
        app_instance.run()
    else:
        # Run without dashboard (CLI only)
        orchestrator = Orchestrator(config, registry, event_bus)
        
        try:
            session = asyncio.run(orchestrator.start())
            
            console.print("\n[bold green]✓ Scan completed![/bold green]")
            console.print(f"Assets discovered: {len(session.assets)}")
            console.print(f"Findings: {len(session.findings)}")
            console.print(f"Critical: {session.critical_count} | High: {session.high_count}")
            
            # Save to database
            db = Database(CONFIG_DIR / "data" / "sessions.db")
            db.save_session(session)
            console.print(f"\n[dim]Session saved: {session.id}[/dim]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠ Scan interrupted by user[/yellow]")
        except Exception as e:
            console.print(f"\n[bold red]✗ Error:[/bold red] {e}")


@app.command()
def report(
    session_id: str = typer.Argument(..., help="Session ID to generate report for"),
    format: str = typer.Option("html", help="Report format: html, md, json"),
    output: Optional[str] = typer.Option(None, help="Output file path"),
):
    """Generate a report from a scan session"""
    ensure_directories()
    
    try:
        generator = ReportGenerator(CONFIG_DIR / "data" / "sessions.db")
        output_path = generator.generate(session_id, format=format, output_file=output)
        
        console.print(f"[bold green]✓ Report generated:[/bold green] {output_path}")
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise typer.Exit(1)


# Sessions subcommands
sessions_app = typer.Typer(help="Manage scan sessions")
app.add_typer(sessions_app, name="sessions")


@sessions_app.command("list")
def sessions_list():
    """List all scan sessions"""
    ensure_directories()
    db = Database(CONFIG_DIR / "data" / "sessions.db")
    sessions = db.get_sessions()

    if not sessions:
        console.print("[yellow]No sessions found[/yellow]")
        return

    table = Table(title="Scan Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Target", style="green")
    table.add_column("Started", style="blue")
    table.add_column("Assets", justify="right")
    table.add_column("Findings", justify="right")

    for session in sessions:
        table.add_row(
            session.id[:8],
            session.target,
            session.started_at.strftime("%Y-%m-%d %H:%M"),
            str(len(session.assets)),
            str(len(session.findings)),
        )

    console.print(table)


@sessions_app.command("show")
def sessions_show(session_id: str = typer.Argument(..., help="Session ID")):
    """Show details of a scan session"""
    ensure_directories()
    db = Database(CONFIG_DIR / "data" / "sessions.db")
    session = db.get_session(session_id)

    if not session:
        console.print(f"[bold red]✗ Session not found:[/bold red] {session_id}")
        raise typer.Exit(1)

    console.print(f"\n[bold]Session:[/bold] {session.id}")
    console.print(f"[bold]Target:[/bold] {session.target}")
    console.print(f"[bold]Started:[/bold] {session.started_at}")
    console.print(f"[bold]Assets:[/bold] {len(session.assets)}")
    console.print(f"[bold]Findings:[/bold] {len(session.findings)}")
    console.print(f"[bold]Critical:[/bold] {session.critical_count}")
    console.print(f"[bold]High:[/bold] {session.high_count}")


@sessions_app.command("delete")
def sessions_delete(session_id: str = typer.Argument(..., help="Session ID")):
    """Delete a scan session"""
    ensure_directories()
    db = Database(CONFIG_DIR / "data" / "sessions.db")
    
    try:
        db.delete_session(session_id)
        console.print(f"[bold green]✓ Session deleted:[/bold green] {session_id}")
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise typer.Exit(1)


# Tools subcommands
tools_app = typer.Typer(help="Manage reconnaissance tools")
app.add_typer(tools_app, name="tools")


@tools_app.command("list")
def tools_list():
    """List all supported tools"""
    registry = create_default_registry()
    
    table = Table(title="Reconnaissance Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Description")

    for tool in sorted(registry.all_tools(), key=lambda t: t.config.name):
        status = "✓ Available" if tool.is_available() else "✗ Missing"
        status_style = "green" if tool.is_available() else "red"
        
        table.add_row(
            tool.config.name,
            tool.config.category.value,
            f"[{status_style}]{status}[/{status_style}]",
            tool.config.description,
        )

    console.print(table)


@tools_app.command("check")
def tools_check():
    """Check availability of all tools"""
    registry = create_default_registry()
    
    available = [t for t in registry.all_tools() if t.is_available()]
    missing = [t for t in registry.all_tools() if not t.is_available()]
    
    console.print(f"\n[bold green]✓ Available tools:[/bold green] {len(available)}/{len(registry.all_tools())}")
    
    if missing:
        console.print("\n[bold yellow]✗ Missing tools:[/bold yellow]")
        for tool in missing:
            console.print(f"  • {tool.config.name} ({tool.config.binary})")


# Config subcommands
config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")


@config_app.command("show")
def config_show():
    """Show current configuration"""
    ensure_directories()
    config = Config.load()
    
    console.print("\n[bold]Configuration:[/bold]")
    console.print(config.model_dump_json(indent=2))


@config_app.command("edit")
def config_edit():
    """Edit configuration file"""
    ensure_directories()
    config_file = CONFIG_DIR / "config.yaml"
    
    # Create default config if it doesn't exist
    if not config_file.exists():
        config = Config()
        config.save()
    
    console.print(f"[bold]Config file:[/bold] {config_file}")
    console.print("[dim]Edit this file with your preferred editor[/dim]")


@config_app.command("reset")
def config_reset():
    """Reset configuration to defaults"""
    ensure_directories()
    config = Config()
    config.save()
    
    console.print("[bold green]✓ Configuration reset to defaults[/bold green]")


@app.command()
def version():
    """Show version information"""
    console.print(f"[bold]ReconPilot[/bold] version [cyan]{__version__}[/cyan]")


if __name__ == "__main__":
    app()
