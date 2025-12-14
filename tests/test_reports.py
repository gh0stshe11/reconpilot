"""Tests for report generation"""
import json

from reconpilot import __version__
from reconpilot.core.database import Database
from reconpilot.reports.generator import ReportGenerator


def test_markdown_report_includes_version(sample_session, tmp_path):
    """Ensure markdown reports show the current ReconPilot version"""
    db_path = tmp_path / "sessions.db"
    Database(db_path).save_session(sample_session)

    generator = ReportGenerator(db_path)
    output_path = tmp_path / "report.md"

    report_file = generator.generate(sample_session.id, format="md", output_file=str(output_path))
    content = report_file.read_text()

    assert f"v{__version__}" in content


def test_json_report_includes_version(sample_session, tmp_path):
    """Ensure JSON reports include the current ReconPilot version"""
    db_path = tmp_path / "sessions.db"
    Database(db_path).save_session(sample_session)

    generator = ReportGenerator(db_path)
    output_path = tmp_path / "report.json"

    report_file = generator.generate(sample_session.id, format="json", output_file=str(output_path))
    data = json.loads(report_file.read_text())

    assert data["version"] == __version__
