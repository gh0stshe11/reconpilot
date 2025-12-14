"""Tests for CLI commands"""
from typer.testing import CliRunner

from reconpilot import __version__
from reconpilot.cli import app

runner = CliRunner()


def test_version():
    """Test version command"""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_help():
    """Test help command"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ReconPilot" in result.stdout or "reconnaissance" in result.stdout.lower()


def test_tools_list():
    """Test tools list command"""
    result = runner.invoke(app, ["tools", "list"])
    assert result.exit_code == 0
    # Should show at least some tools
    assert "nmap" in result.stdout.lower() or "subfinder" in result.stdout.lower()


def test_tools_check():
    """Test tools check command"""
    result = runner.invoke(app, ["tools", "check"])
    assert result.exit_code == 0
    assert "tools" in result.stdout.lower()


def test_sessions_list():
    """Test sessions list command"""
    result = runner.invoke(app, ["sessions", "list"])
    assert result.exit_code == 0
    # May be empty but should not error


def test_config_show():
    """Test config show command"""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
