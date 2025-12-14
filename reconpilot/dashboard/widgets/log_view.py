"""Log view widget"""
from collections import deque

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static


class LogViewWidget(ScrollableContainer):
    """Display log messages"""

    def __init__(self, max_lines: int = 100):
        super().__init__()
        self.max_lines = max_lines
        self.log_lines: deque[str] = deque(maxlen=max_lines)

    def compose(self) -> ComposeResult:
        """Compose the log view"""
        yield Static("", id="log-content")

    def add_log(self, message: str, level: str = "info") -> None:
        """Add a log message"""
        # Format with color based on level
        level_colors = {
            "debug": "dim",
            "info": "cyan",
            "warning": "yellow",
            "error": "red",
            "success": "green",
        }
        color = level_colors.get(level, "white")
        
        formatted = f"[{color}]{message}[/{color}]"
        self.log_lines.append(formatted)
        
        # Update display
        log_content = self.query_one("#log-content", Static)
        log_content.update("\n".join(self.log_lines))
        
        # Auto-scroll to bottom
        self.scroll_end(animate=False)

    def clear_logs(self) -> None:
        """Clear all log messages"""
        self.log_lines.clear()
        log_content = self.query_one("#log-content", Static)
        log_content.update("")
