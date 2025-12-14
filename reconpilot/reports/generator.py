"""Report generator"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from reconpilot.config import REPORTS_DIR
from reconpilot.core.database import Database
from reconpilot.core.models import ScanSession, Severity


class ReportGenerator:
    """Generate reports from scan sessions"""

    def __init__(self, db_path: Path):
        self.db = Database(db_path)
        
        # Set up Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate(
        self,
        session_id: str,
        format: str = "html",
        output_file: Optional[str] = None,
    ) -> Path:
        """Generate a report"""
        # Load session
        session = self.db.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Prepare output path
        if output_file:
            output_path = Path(output_file)
        else:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = REPORTS_DIR / f"report_{session.target}_{timestamp}.{format}"

        # Generate report based on format
        if format == "html":
            content = self._generate_html(session)
        elif format == "md":
            content = self._generate_markdown(session)
        elif format == "json":
            content = self._generate_json(session)
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Write to file
        with open(output_path, "w") as f:
            f.write(content)

        return output_path

    def _generate_html(self, session: ScanSession) -> str:
        """Generate HTML report"""
        template = self.env.get_template("report.html.j2")
        
        context = self._prepare_context(session)
        return template.render(**context)

    def _generate_markdown(self, session: ScanSession) -> str:
        """Generate Markdown report"""
        template = self.env.get_template("report.md.j2")
        
        context = self._prepare_context(session)
        return template.render(**context)

    def _generate_json(self, session: ScanSession) -> str:
        """Generate JSON report"""
        data = {
            "session_id": session.id,
            "target": session.target,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "statistics": {
                "total_assets": len(session.assets),
                "total_findings": len(session.findings),
                "critical": session.critical_count,
                "high": session.high_count,
            },
            "assets": [
                {
                    "id": asset.id,
                    "type": asset.type,
                    "value": asset.value,
                    "discovered_by": asset.discovered_by,
                    "timestamp": asset.timestamp.isoformat(),
                    "score": asset.score,
                    "metadata": asset.metadata,
                }
                for asset in session.assets
            ],
            "findings": [
                {
                    "id": finding.id,
                    "severity": finding.severity.value,
                    "title": finding.title,
                    "host": finding.host,
                    "description": finding.description,
                    "discovered_by": finding.discovered_by,
                    "timestamp": finding.timestamp.isoformat(),
                    "evidence": finding.evidence,
                    "recommendations": finding.recommendations,
                    "metadata": finding.metadata,
                }
                for finding in session.findings
            ],
        }
        return json.dumps(data, indent=2)

    def _prepare_context(self, session: ScanSession) -> dict:
        """Prepare template context"""
        # Calculate statistics
        findings_by_severity = {sev: [] for sev in Severity}
        for finding in session.findings:
            findings_by_severity[finding.severity].append(finding)

        # Group assets by type
        assets_by_type: dict[str, list] = {}
        for asset in session.assets:
            if asset.type not in assets_by_type:
                assets_by_type[asset.type] = []
            assets_by_type[asset.type].append(asset)

        # Calculate duration
        duration = None
        if session.completed_at:
            duration = session.completed_at - session.started_at

        return {
            "session": session,
            "findings_by_severity": findings_by_severity,
            "assets_by_type": assets_by_type,
            "duration": duration,
            "generated_at": datetime.now(),
            "severity_enum": Severity,
        }
