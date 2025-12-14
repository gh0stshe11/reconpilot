"""Findings widget"""
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static

from reconpilot.core.models import Finding, Severity


class FindingsWidget(ScrollableContainer):
    """Display security findings"""

    def __init__(self):
        super().__init__()
        self.findings: list[Finding] = []

    def compose(self) -> ComposeResult:
        """Compose the findings list"""
        yield Static("No findings yet...", id="findings-empty")

    def update_findings(self, findings: list[Finding]) -> None:
        """Update the findings list"""
        self.findings = findings
        
        # Clear existing findings
        self.query("Static").remove()
        
        if not findings:
            self.mount(Static("No findings yet...", id="findings-empty"))
            return

        # Sort by severity
        sorted_findings = sorted(
            findings,
            key=lambda f: list(Severity).index(f.severity)
        )

        # Add finding items
        for finding in sorted_findings:
            severity_icon = finding.severity.icon
            severity_text = finding.severity.value.upper()
            
            finding_text = f"{severity_icon} [{severity_text}] {finding.title}\n  Host: {finding.host}\n  {finding.description}"
            
            self.mount(Static(finding_text, classes=f"finding-item severity-{finding.severity.value}"))

    def get_severity_counts(self) -> dict[Severity, int]:
        """Get counts by severity"""
        counts = {sev: 0 for sev in Severity}
        for finding in self.findings:
            counts[finding.severity] += 1
        return counts
