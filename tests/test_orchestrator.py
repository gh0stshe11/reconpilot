"""Tests for orchestrator"""
import pytest

from reconpilot.core.events import EventBus
from reconpilot.core.orchestrator import ScanConfig, ScanMode
from reconpilot.tools.registry import create_default_registry


def test_scan_config_creation():
    """Test creating a scan configuration"""
    config = ScanConfig(
        target="example.com",
        mode=ScanMode.AUTO,
        max_parallel=3,
    )
    assert config.target == "example.com"
    assert config.mode == ScanMode.AUTO
    assert config.max_parallel == 3


def test_scan_config_with_scope():
    """Test scan config with scope"""
    # These are test data patterns, not actual URL sanitization
    scope_pattern = "*.example.com"
    exclude_pattern = "dev.example.com"
    
    config = ScanConfig(
        target="example.com",
        scope=[scope_pattern],
        exclude=[exclude_pattern],
    )
    assert scope_pattern in config.scope
    assert exclude_pattern in config.exclude


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    from reconpilot.core.orchestrator import Orchestrator
    
    config = ScanConfig(target="example.com")
    registry = create_default_registry()
    event_bus = EventBus()
    
    orchestrator = Orchestrator(config, registry, event_bus)
    
    assert orchestrator.config.target == "example.com"
    assert orchestrator.session.target == "example.com"
    assert len(orchestrator.plan.all_tasks) == 0


def test_orchestrator_pause_resume():
    """Test pause and resume functionality"""
    from reconpilot.core.orchestrator import Orchestrator
    
    config = ScanConfig(target="example.com")
    registry = create_default_registry()
    event_bus = EventBus()
    
    orchestrator = Orchestrator(config, registry, event_bus)
    
    # Test pause
    orchestrator.pause()
    assert orchestrator._paused is True
    
    # Test resume
    orchestrator.resume()
    assert orchestrator._paused is False
    
    # Test stop
    orchestrator.stop()
    assert orchestrator._stopped is True
