"""Task list widget"""
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static

from reconpilot.core.models import Task, TaskStatus


class TaskListWidget(ScrollableContainer):
    """Display list of tasks"""

    def __init__(self):
        super().__init__()
        self.tasks: list[Task] = []

    def compose(self) -> ComposeResult:
        """Compose the task list"""
        yield Static("No tasks yet...", id="tasks-empty")

    def update_tasks(self, tasks: list[Task]) -> None:
        """Update the task list"""
        self.tasks = tasks
        
        # Clear existing tasks
        self.query("Static").remove()
        
        if not tasks:
            self.mount(Static("No tasks yet...", id="tasks-empty"))
            return

        # Add task items
        for task in tasks:
            status_icon = self._get_status_icon(task.status)
            progress_bar = self._get_progress_bar(task.progress)
            
            task_text = f"{status_icon} {task.name} - {task.description}\n  {progress_bar}"
            
            self.mount(Static(task_text, classes="task-item"))

    def _get_status_icon(self, status: TaskStatus) -> str:
        """Get icon for task status"""
        icons = {
            TaskStatus.PENDING: "⏸️",
            TaskStatus.RUNNING: "▶️",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.SKIPPED: "⏭️",
        }
        return icons.get(status, "❓")

    def _get_progress_bar(self, progress: float) -> str:
        """Generate a progress bar"""
        bar_length = 20
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"[{bar}] {progress:.0f}%"
