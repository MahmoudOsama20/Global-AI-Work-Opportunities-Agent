import asyncio
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

# Add backend directory to sys.path so app package is importable
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings, config_manager
from app.core.logging import app_logger
from app.database.session import init_db, SessionLocal
from app.database.repositories.source_repo import SourceRepository
from app.schemas.source import SourceCreate

cli = typer.Typer(
    name="Global AI Opportunities Intelligence Agent",
    help="Manually operated global opportunity discovery, intelligence, and matching platform.",
    add_completion=False,
)
console = Console()


@cli.command("init-db")
def init_database_command():
    """Initializes SQLite database and seeds default sources."""
    console.print("[bold cyan]Initializing database tables...[/bold cyan]")
    init_db()
    sources_seed = config_manager.get_sources()
    with SessionLocal() as session:
        repo = SourceRepository(session)
        count = 0
        for item in sources_seed:
            schema = SourceCreate(**item)
            repo.upsert(schema)
            count += 1
        session.commit()
        console.print(f"[bold green]Successfully initialized DB and seeded {count} sources![/bold green]")


@cli.command("health-check")
def health_check_command():
    """Runs health check against registered source endpoints."""
    console.print("[bold cyan]Executing health check across registered connectors...[/bold cyan]")
    from app.pipeline.runner import PipelineRunner
    runner = PipelineRunner()
    results = runner.health_check_all()
    table = Table(title="Connector Health Status")
    table.add_column("Source ID", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Response Time (ms)", justify="right")
    table.add_column("Message")
    for res in results:
        status_style = "green" if res.is_healthy else "red"
        status_text = "HEALTHY" if res.is_healthy else "UNHEALTHY"
        table.add_row(
            res.source_id,
            f"[{status_style}]{status_text}[/{status_style}]",
            f"{res.response_time_ms:.1f}",
            res.message,
        )
    console.print(table)


@cli.command("run")
def run_pipeline_command(
    source: str = typer.Option(None, "--source", "-s", help="Run only a specific source ID"),
    category: str = typer.Option(None, "--category", "-c", help="Filter by opportunity category"),
    discover_sources: bool = typer.Option(False, "--discover-sources", "-d", help="Run source discovery"),
):
    """Manually triggers the global AI opportunity collection, analysis, and reporting run."""
    console.print("[bold yellow]Starting Global AI Opportunity Search Run...[/bold yellow]")
    from app.pipeline.runner import PipelineRunner
    runner = PipelineRunner()
    summary = runner.run_manual(
        source_filter=source,
        category_filter=category,
        trigger_discovery=discover_sources,
    )
    console.print(f"[bold green]Run completed successfully! ID: {summary.get('run_id')}[/bold green]")
    console.print(f"Total Collected: {summary.get('total_collected')}")
    console.print(f"Relevant Matches: {summary.get('relevant_count')}")
    console.print(f"Duplicates Detected: {summary.get('duplicate_count')}")
    if summary.get("report_html_path"):
        console.print(f"HTML Report: [cyan]{summary.get('report_html_path')}[/cyan]")
    if summary.get("report_md_path"):
        console.print(f"Markdown Report: [cyan]{summary.get('report_md_path')}[/cyan]")


@cli.command("login-account")
def login_account_command(
    platform: str = typer.Argument("outlier", help="Platform name (e.g. outlier)"),
):
    """Opens a visible browser for safe interactive user sign-in without storing passwords."""
    if platform.lower() == "outlier":
        from app.connectors.outlier.account_outlier import OutlierAccountConnector
        connector = OutlierAccountConnector()
        console.print(f"[bold cyan]Launching interactive browser session for {platform}...[/bold cyan]")
        res = connector.login_interactive()
        console.print(f"[bold green]{res.get('message')}[/bold green]")
    else:
        console.print(f"[yellow]Platform '{platform}' interactive login not configured.[/yellow]")


@cli.command("inspect-account")
def inspect_account_command(
    platform: str = typer.Argument("outlier", help="Platform name (e.g. outlier)"),
):
    """Safely inspects authorized private project queues in read-only mode using saved browser profile."""
    if platform.lower() == "outlier":
        from app.connectors.outlier.account_outlier import OutlierAccountConnector
        connector = OutlierAccountConnector()
        console.print(f"[bold cyan]Inspecting account status for {platform}...[/bold cyan]")
        res = connector.inspect_account()
        console.print(f"Status: [bold]{res.get('status')}[/bold]")
        console.print(f"Authenticated: {res.get('is_authenticated')}")
        console.print(f"Active Project: {res.get('active_project')}")
        console.print(f"Details: {res.get('message')}")
    else:
        console.print(f"[yellow]Platform '{platform}' account inspection not configured.[/yellow]")


@cli.command("serve")
def serve_command(
    host: str = typer.Option(settings.HOST, "--host", "-h"),
    port: int = typer.Option(settings.PORT, "--port", "-p"),
    reload: bool = typer.Option(False, "--reload"),
):
    """Starts the FastAPI backend service."""
    import uvicorn
    console.print(f"[bold green]Starting backend on http://{host}:{port}[/bold green]")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload, app_dir=str(BACKEND_DIR))


if __name__ == "__main__":
    cli()
