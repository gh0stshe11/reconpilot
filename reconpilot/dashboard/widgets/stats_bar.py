"""Stats bar widget"""
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static


class StatsBar(Static):
    """Display scan statistics"""

    def __init__(self):
        super().__init__()
        self.started_at = datetime.now()
        self.assets_count = 0
        self.findings_count = 0
        self.critical_count = 0

    def compose(self) -> ComposeResult:
        """Compose the stats bar"""
        with Horizontal(id="stats-container"):
            yield Static("⏱️  0:00:00", id="stat-elapsed", classes="stat")
            yield Static("📦 0 Assets", id="stat-assets", classes="stat")
            yield Static("🔍 0 Findings", id="stat-findings", classes="stat")
            yield Static("🔴 0 Critical", id="stat-critical", classes="stat")

    def update_stats(
        self,
        assets_count: int = 0,
        findings_count: int = 0,
        critical_count: int = 0,
    ) -> None:
        """Update statistics"""
        self.assets_count = assets_count
        self.findings_count = findings_count
        self.critical_count = critical_count

        # Update elapsed time
        elapsed = datetime.now() - self.started_at
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # Update displays
        self.query_one("#stat-elapsed", Static).update(f"⏱️  {elapsed_str}")
        self.query_one("#stat-assets", Static).update(f"📦 {assets_count} Assets")
        self.query_one("#stat-findings", Static).update(f"🔍 {findings_count} Findings")
        self.query_one("#stat-critical", Static).update(f"🔴 {critical_count} Critical")
