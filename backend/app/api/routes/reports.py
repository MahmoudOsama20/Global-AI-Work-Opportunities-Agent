from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from app.core.config import DATA_DIR

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("", response_model=List[Dict[str, Any]])
def list_reports():
    """Lists locally generated intelligence reports."""
    reports_dir = DATA_DIR / "reports"
    if not reports_dir.exists():
        return []
    
    reports = []
    for f in sorted(reports_dir.glob("report_*.html"), reverse=True):
        run_id = f.stem.replace("report_", "")
        md_file = reports_dir / f"report_{run_id}.md"
        reports.append({
            "run_id": run_id,
            "filename": f.name,
            "html_path": str(f),
            "md_path": str(md_file) if md_file.exists() else None,
            "created_at": datetime_from_mtime(f.stat().st_mtime),
        })
    return reports

def datetime_from_mtime(mtime: float) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(mtime, timezone.utc).isoformat()

@router.get("/{run_id}/html", response_class=HTMLResponse)
def get_html_report(run_id: str):
    """Serves the standalone HTML report."""
    report_file = DATA_DIR / "reports" / f"report_{run_id}.html"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="HTML report not found")
    return HTMLResponse(content=report_file.read_text(encoding="utf-8"))

@router.get("/{run_id}/markdown", response_class=PlainTextResponse)
def get_markdown_report(run_id: str):
    """Serves the raw Markdown report."""
    report_file = DATA_DIR / "reports" / f"report_{run_id}.md"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Markdown report not found")
    return PlainTextResponse(content=report_file.read_text(encoding="utf-8"))
