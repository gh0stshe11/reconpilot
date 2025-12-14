"""Main TUI dashboard application"""
import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from reconpilot.config import CONFIG_DIR
from reconpilot.core.database import Database
from reconpilot.core.events import Event, EventBus, EventType
from reconpilot.core.orchestrator import Orchestrator, ScanConfig
from reconpilot.dashboard.widgets.findings import FindingsWidget
from reconpilot.dashboard.widgets.log_view import LogViewWidget
from reconpilot.dashboard.widgets.stats_bar import StatsBar
from reconpilot.dashboard.widgets.task_list import TaskListWidget
from reconpilot.tools.registry import ToolRegistry


class ReconPilotDashboard(App):
    """ReconPilot TUI Dashboard"""

    CSS = """
    Screen {
        background: $surface;
    }
    
    #stats-container {
        height: 3;
        background: $panel;
        border: solid $primary;
    }
    
    .stat {
        padding: 1 2;
        color: $text;
    }
    
    #main-container {
        height: 1fr;
    }
    
    #left-panel {
        width: 50%;
        border: solid $primary;
    }
    
    #right-panel {
        width: 50%;
        border: solid $primary;
    }
    
    #task-panel {
        height: 50%;
        border: solid $accent;
    }
    
    #findings-panel {
        height: 50%;
        border: solid $accent;
    }
    
    #log-panel {
        height: 100%;
        border: solid $accent;
    }
    
    .task-item {
        padding: 1;
        margin: 0 1;
    }
    
    .finding-item {
        padding: 1;
        margin: 0 1;
    }
    
    .severity-critical {
        color: $error;
    }
    
    .severity-high {
        color: $warning;
    }
    
    .severity-medium {
        color: yellow;
    }
    
    .severity-low {
        color: $primary;
    }
    
    .severity-info {
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("p", "pause", "Pause"),
        ("r", "resume", "Resume"),
        ("s", "skip", "Skip Task"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        config: ScanConfig,
        registry: ToolRegistry,
        event_bus: EventBus,
    ):
        super().__init__()
        self.config = config
        self.registry = registry
        self.event_bus = event_bus
        self.orchestrator: Orchestrator | None = None
        self.stats_bar: StatsBar | None = None
        self.task_list: TaskListWidget | None = None
        self.findings_widget: FindingsWidget | None = None
        self.log_view: LogViewWidget | None = None
        self._update_timer = None

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout"""
        yield Header(show_clock=True)
        yield StatsBar()
        
        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                with Container(id="task-panel"):
                    yield Static("📋 Tasks", classes="panel-title")
                    yield TaskListWidget()
                
                with Container(id="findings-panel"):
                    yield Static("🔍 Findings", classes="panel-title")
                    yield FindingsWidget()
            
            with Vertical(id="right-panel"):
                with Container(id="log-panel"):
                    yield Static("📝 Log", classes="panel-title")
                    yield LogViewWidget()
        
        yield Footer()

    async def on_mount(self) -> None:
        """Handle mount event"""
        self.title = "ReconPilot Dashboard"
        self.sub_title = f"Target: {self.config.target}"
        
        # Get widget references
        self.stats_bar = self.query_one(StatsBar)
        self.task_list = self.query_one(TaskListWidget)
        self.findings_widget = self.query_one(FindingsWidget)
        self.log_view = self.query_one(LogViewWidget)
        
        # Subscribe to events
        self.event_bus.subscribe(EventType.SCAN_STARTED, self._on_scan_started)
        self.event_bus.subscribe(EventType.SCAN_COMPLETED, self._on_scan_completed)
        self.event_bus.subscribe(EventType.TASK_STARTED, self._on_task_started)
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self._on_task_completed)
        self.event_bus.subscribe(EventType.TASK_FAILED, self._on_task_failed)
        self.event_bus.subscribe(EventType.ASSET_DISCOVERED, self._on_asset_discovered)
        self.event_bus.subscribe(EventType.FINDING_DISCOVERED, self._on_finding_discovered)
        self.event_bus.subscribe(EventType.LOG_MESSAGE, self._on_log_message)
        
        # Start orchestrator
        self.orchestrator = Orchestrator(self.config, self.registry, self.event_bus)
        asyncio.create_task(self._run_scan())
        
        # Start update timer
        self.set_interval(1.0, self._update_display)

    async def _run_scan(self) -> None:
        """Run the scan"""
        if self.orchestrator:
            session = await self.orchestrator.start()
            
            # Save session to database
            db = Database(CONFIG_DIR / "data" / "sessions.db")
            db.save_session(session)

    def _update_display(self) -> None:
        """Update the dashboard display"""
        if not self.orchestrator:
            return
        
        session = self.orchestrator.session
        
        # Update stats
        if self.stats_bar:
            self.stats_bar.update_stats(
                assets_count=len(session.assets),
                findings_count=len(session.findings),
                critical_count=session.critical_count,
            )
        
        # Update tasks
        if self.task_list:
            self.task_list.update_tasks(self.orchestrator.plan.all_tasks)
        
        # Update findings
        if self.findings_widget:
            self.findings_widget.update_findings(session.findings)

    async def _on_scan_started(self, event: Event) -> None:
        """Handle scan started event"""
        if self.log_view:
            self.log_view.add_log(f"Scan started: {event.data.get('target')}", "success")

    async def _on_scan_completed(self, event: Event) -> None:
        """Handle scan completed event"""
        if self.log_view:
            assets = event.data.get("assets", 0)
            findings = event.data.get("findings", 0)
            self.log_view.add_log(
                f"Scan completed! Assets: {assets}, Findings: {findings}",
                "success"
            )

    async def _on_task_started(self, event: Event) -> None:
        """Handle task started event"""
        if self.log_view:
            name = event.data.get("name", "unknown")
            self.log_view.add_log(f"Started: {name}", "info")

    async def _on_task_completed(self, event: Event) -> None:
        """Handle task completed event"""
        if self.log_view:
            name = event.data.get("name", "unknown")
            self.log_view.add_log(f"Completed: {name}", "success")

    async def _on_task_failed(self, event: Event) -> None:
        """Handle task failed event"""
        if self.log_view:
            error = event.data.get("error", "unknown error")
            self.log_view.add_log(f"Failed: {error}", "error")

    async def _on_asset_discovered(self, event: Event) -> None:
        """Handle asset discovered event"""
        if self.log_view:
            asset_type = event.data.get("type", "")
            value = event.data.get("value", "")
            self.log_view.add_log(f"Asset: {asset_type} - {value}", "info")

    async def _on_finding_discovered(self, event: Event) -> None:
        """Handle finding discovered event"""
        if self.log_view:
            severity = event.data.get("severity", "")
            title = event.data.get("title", "")
            self.log_view.add_log(f"Finding [{severity}]: {title}", "warning")

    async def _on_log_message(self, event: Event) -> None:
        """Handle log message event"""
        if self.log_view:
            message = event.data.get("message", "")
            level = event.data.get("level", "info")
            self.log_view.add_log(message, level)

    def action_pause(self) -> None:
        """Pause the scan"""
        if self.orchestrator:
            self.orchestrator.pause()
            if self.log_view:
                self.log_view.add_log("Scan paused", "warning")

    def action_resume(self) -> None:
        """Resume the scan"""
        if self.orchestrator:
            self.orchestrator.resume()
            if self.log_view:
                self.log_view.add_log("Scan resumed", "success")

    def action_skip(self) -> None:
        """Skip current task"""
        if self.log_view:
            self.log_view.add_log("Skip not implemented yet", "warning")

    def action_quit(self) -> None:
        """Quit the dashboard"""
        if self.orchestrator:
            self.orchestrator.stop()
        self.exit()
