import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Auto-delegate to .venv python if executed outside the virtual environment
ROOT_DIR = Path(__file__).resolve().parent
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
    result = subprocess.run([str(VENV_PYTHON), str(Path(__file__).resolve())] + sys.argv[1:], cwd=str(ROOT_DIR))
    sys.exit(result.returncode)

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


@cli.command("upload-cv")
def upload_cv_command(
    file_path: str = typer.Argument(..., help="Path to PDF, DOCX, or TXT resume file"),
    approve: bool = typer.Option(True, "--approve/--no-approve", help="Automatically approve the extracted profile for active matching"),
):
    """Parses and ingests a CV resume into the local intelligence database."""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]File not found: {file_path}[/bold red]")
        raise typer.Exit(code=1)

    with open(path, "rb") as f:
        file_bytes = f.read()

    from app.intelligence.cv_parser import CVParser
    from app.database.repositories.cv_repo import CVRepository

    console.print(f"[bold cyan]Parsing CV document: {path.name}...[/bold cyan]")
    parser = CVParser()
    try:
        parsed_data = parser.parse(file_bytes, path.name)
        if approve:
            parsed_data["approved"] = True
    except Exception as e:
        console.print(f"[bold red]Error parsing CV: {e}[/bold red]")
        raise typer.Exit(code=1)

    init_db()
    with SessionLocal() as session:
        repo = CVRepository(session)
        profile = repo.save_profile(parsed_data)
        console.print(f"[bold green]Successfully extracted and stored CV profile! ID: {profile.id}[/bold green]")
        console.print(f"Professional Headline: [bold]{profile.professional_headline}[/bold]")
        console.print(f"Seniority Level: [bold cyan]{profile.seniority_level.upper()}[/bold cyan] ({profile.years_of_experience} years)")
        console.print(f"Leadership Experience: {profile.has_leadership_experience}")
        console.print(f"Extracted Skills: {len(profile.technical_skills)} skills ({', '.join(profile.technical_skills[:8])})")
        console.print(f"Projects Extracted: {len(profile.projects)}")
        console.print(f"Approved Status: [bold]{profile.approved}[/bold]")


@cli.command("show-cv")
def show_cv_command():
    """Displays the currently active/approved CV intelligence profile."""
    from app.database.repositories.cv_repo import CVRepository
    init_db()
    with SessionLocal() as session:
        repo = CVRepository(session)
        profile = repo.get_active_profile()
        if not profile:
            console.print("[yellow]No CV profile has been uploaded yet.[/yellow]")
            return

        table = Table(title=f"Active CV Profile: {profile.filename}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        table.add_row("Profile ID", profile.id)
        table.add_row("Headline", profile.professional_headline or "N/A")
        table.add_row("Seniority", f"{profile.seniority_level.upper()} ({profile.years_of_experience} years)")
        table.add_row("Leadership", str(profile.has_leadership_experience))
        table.add_row("Skills Count", str(len(profile.technical_skills)))
        table.add_row("Top Skills", ", ".join(profile.technical_skills[:10]))
        table.add_row("Projects Count", str(len(profile.projects)))
        table.add_row("Confidence", f"{profile.extraction_confidence}%")
        table.add_row("Approved", str(profile.approved))
        console.print(table)


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
