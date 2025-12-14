"""Main orchestration engine for ReconPilot"""
import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from reconpilot.core.events import Event, EventBus, EventType
from reconpilot.core.models import Asset, Finding, ScanSession, Task, TaskStatus
from reconpilot.core.rules import RulesEngine
from reconpilot.core.scoring import ScoringEngine
from reconpilot.tools.registry import ToolRegistry


class ScanMode(Enum):
    """Scan execution modes"""
    AUTO = "auto"
    INTERACTIVE = "interactive"
    PASSIVE = "passive"


@dataclass
class ScanConfig:
    """Configuration for a scan"""
    target: str
    mode: ScanMode = ScanMode.AUTO
    scope: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    max_parallel: int = 3
    passive_only: bool = False
    stealth: bool = False
    timeout: int = 300


class ReconPlan:
    """Manages the reconnaissance task queue"""

    def __init__(self):
        self.pending: deque[Task] = deque()
        self.running: list[Task] = []
        self.completed: list[Task] = []
        self.failed: list[Task] = []
        self.skipped: list[Task] = []

    def add_task(self, task: Task, priority: bool = False) -> None:
        """Add a task to the queue"""
        if priority:
            self.pending.appendleft(task)
        else:
            self.pending.append(task)

    def get_next_task(self) -> Optional[Task]:
        """Get the next task from the queue"""
        if self.pending:
            return self.pending.popleft()
        return None

    def mark_running(self, task: Task) -> None:
        """Mark a task as running"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        if task not in self.running:
            self.running.append(task)

    def mark_completed(self, task: Task) -> None:
        """Mark a task as completed"""
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.progress = 100.0
        if task in self.running:
            self.running.remove(task)
        self.completed.append(task)

    def mark_failed(self, task: Task, error: str) -> None:
        """Mark a task as failed"""
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now()
        task.error = error
        if task in self.running:
            self.running.remove(task)
        self.failed.append(task)

    def mark_skipped(self, task: Task) -> None:
        """Mark a task as skipped"""
        task.status = TaskStatus.SKIPPED
        task.completed_at = datetime.now()
        if task in self.running:
            self.running.remove(task)
        self.skipped.append(task)

    @property
    def all_tasks(self) -> list[Task]:
        """Get all tasks"""
        return (
            list(self.pending)
            + self.running
            + self.completed
            + self.failed
            + self.skipped
        )


class Orchestrator:
    """Main orchestration engine"""

    def __init__(
        self,
        config: ScanConfig,
        tool_registry: ToolRegistry,
        event_bus: EventBus,
    ):
        self.config = config
        self.registry = tool_registry
        self.event_bus = event_bus
        self.session = ScanSession(target=config.target)
        self.plan = ReconPlan()
        self.rules_engine = RulesEngine()
        self.scoring_engine = ScoringEngine()
        self._paused = False
        self._stopped = False
        self._seen_assets: set[str] = set()

    async def start(self) -> ScanSession:
        """Start the reconnaissance scan"""
        await self.event_bus.publish(
            Event(
                type=EventType.SCAN_STARTED,
                data={"target": self.config.target, "session_id": self.session.id},
                source="orchestrator",
            )
        )

        # Initialize with first task based on target type
        initial_task = self._create_initial_task()
        self.plan.add_task(initial_task)
        self.session.tasks.append(initial_task)

        # Main orchestration loop
        try:
            await self._orchestration_loop()
        except Exception as e:
            await self.event_bus.publish(
                Event(
                    type=EventType.LOG_MESSAGE,
                    data={"level": "error", "message": f"Orchestration error: {e}"},
                    source="orchestrator",
                )
            )

        self.session.completed_at = datetime.now()
        await self.event_bus.publish(
            Event(
                type=EventType.SCAN_COMPLETED,
                data={
                    "session_id": self.session.id,
                    "assets": len(self.session.assets),
                    "findings": len(self.session.findings),
                },
                source="orchestrator",
            )
        )

        return self.session

    def _create_initial_task(self) -> Task:
        """Create the initial task based on target"""
        from reconpilot.utils.helpers import is_valid_ip, is_valid_url
        
        target = self.config.target
        
        # Determine if target is URL, IP, or domain
        if is_valid_url(target):
            tool_name = "httpx"
            description = f"Probe HTTP service: {target}"
        elif is_valid_ip(target):
            tool_name = "nmap"
            description = f"Port scan: {target}"
        else:
            # Assume domain
            tool_name = "subfinder"
            description = f"Find subdomains for: {target}"

        return Task(
            name=tool_name,
            description=description,
            metadata={"target": target},
        )

    async def _orchestration_loop(self) -> None:
        """Main orchestration loop"""
        while not self._stopped:
            # Check if paused
            if self._paused:
                await asyncio.sleep(1)
                continue

            # Check if we can run more tasks
            if len(self.plan.running) >= self.config.max_parallel:
                await asyncio.sleep(1)
                continue

            # Get next task
            task = self.plan.get_next_task()
            if not task:
                # No more pending tasks, wait for running tasks to complete
                if not self.plan.running:
                    break
                await asyncio.sleep(1)
                continue

            # Execute task
            asyncio.create_task(self._execute_task(task))

    async def _execute_task(self, task: Task) -> None:
        """Execute a single task"""
        tool = self.registry.get(task.name)
        if not tool:
            self.plan.mark_failed(task, f"Tool not found: {task.name}")
            return

        if not tool.is_available():
            self.plan.mark_failed(task, f"Tool not available: {task.name}")
            return

        self.plan.mark_running(task)
        await self.event_bus.publish(
            Event(
                type=EventType.TASK_STARTED,
                data={"task_id": task.id, "name": task.name},
                source="orchestrator",
            )
        )

        try:
            target = task.metadata.get("target", self.config.target)
            
            async for result in tool.execute(target):
                if result.success:
                    # Process discovered assets
                    for asset in result.assets:
                        await self._handle_asset(asset)

                    # Process findings
                    for finding in result.findings:
                        await self._handle_finding(finding)

                    # Update task progress
                    task.progress = result.metadata.get("progress", 50.0)
                    await self.event_bus.publish(
                        Event(
                            type=EventType.TASK_PROGRESS,
                            data={"task_id": task.id, "progress": task.progress},
                            source="orchestrator",
                        )
                    )

            self.plan.mark_completed(task)
            await self.event_bus.publish(
                Event(
                    type=EventType.TASK_COMPLETED,
                    data={"task_id": task.id, "name": task.name},
                    source="orchestrator",
                )
            )

        except Exception as e:
            self.plan.mark_failed(task, str(e))
            await self.event_bus.publish(
                Event(
                    type=EventType.TASK_FAILED,
                    data={"task_id": task.id, "error": str(e)},
                    source="orchestrator",
                )
            )

    async def _handle_asset(self, asset: Asset) -> None:
        """Handle a discovered asset"""
        # Deduplicate assets
        asset_key = f"{asset.type}:{asset.value}"
        if asset_key in self._seen_assets:
            return
        self._seen_assets.add(asset_key)

        # Score the asset
        asset.score = self.scoring_engine.score_asset(asset)

        # Add to session
        self.session.assets.append(asset)

        # Publish event
        await self.event_bus.publish(
            Event(
                type=EventType.ASSET_DISCOVERED,
                data={"asset_id": asset.id, "type": asset.type, "value": asset.value},
                source="orchestrator",
            )
        )

        # Chain next tasks based on rules
        if self.config.mode == ScanMode.AUTO:
            next_tools = self.rules_engine.get_next_tools(asset)
            for tool_name, reason, priority in next_tools:
                # Check if tool is available
                tool = self.registry.get(tool_name)
                if not tool or not tool.is_available():
                    continue

                # Create task
                task = Task(
                    name=tool_name,
                    description=f"{reason}: {asset.value}",
                    metadata={"target": asset.value, "asset_id": asset.id},
                )
                self.plan.add_task(task, priority=priority > 8)
                self.session.tasks.append(task)

    async def _handle_finding(self, finding: Finding) -> None:
        """Handle a discovered finding"""
        # Add to session
        self.session.findings.append(finding)

        # Publish event
        await self.event_bus.publish(
            Event(
                type=EventType.FINDING_DISCOVERED,
                data={
                    "finding_id": finding.id,
                    "severity": finding.severity.value,
                    "title": finding.title,
                },
                source="orchestrator",
            )
        )

    def pause(self) -> None:
        """Pause the orchestration"""
        self._paused = True

    def resume(self) -> None:
        """Resume the orchestration"""
        self._paused = False

    def stop(self) -> None:
        """Stop the orchestration"""
        self._stopped = True
