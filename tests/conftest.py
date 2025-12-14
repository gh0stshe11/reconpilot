"""Pytest configuration and fixtures"""
import pytest

from reconpilot.core.events import EventBus
from reconpilot.core.models import Asset, Finding, ScanSession, Severity, Task, TaskStatus
from reconpilot.tools.registry import create_default_registry


@pytest.fixture
def event_bus():
    """Create an event bus instance"""
    return EventBus()


@pytest.fixture
def tool_registry():
    """Create a tool registry instance"""
    return create_default_registry()


@pytest.fixture
def sample_task():
    """Create a sample task"""
    return Task(
        name="test_tool",
        description="Test task",
        status=TaskStatus.PENDING,
    )


@pytest.fixture
def sample_asset():
    """Create a sample asset"""
    return Asset(
        type="domain",
        value="example.com",
        discovered_by="test_tool",
    )


@pytest.fixture
def sample_finding():
    """Create a sample finding"""
    return Finding(
        severity=Severity.HIGH,
        title="Test Finding",
        host="example.com",
        description="This is a test finding",
        discovered_by="test_tool",
    )


@pytest.fixture
def sample_session():
    """Create a sample scan session"""
    session = ScanSession(target="example.com")
    session.tasks.append(
        Task(
            name="test_tool",
            description="Test task",
            status=TaskStatus.COMPLETED,
        )
    )
    session.assets.append(
        Asset(
            type="domain",
            value="example.com",
            discovered_by="test_tool",
        )
    )
    session.findings.append(
        Finding(
            severity=Severity.HIGH,
            title="Test Finding",
            host="example.com",
            description="Test description",
            discovered_by="test_tool",
        )
    )
    return session
