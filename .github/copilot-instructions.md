# Copilot Instructions for ReconPilot

## Project Overview

ReconPilot is an AI-powered reconnaissance automation framework designed for penetration testing. It intelligently chains security tools together based on discoveries, prioritizes targets, and provides a real-time TUI dashboard for monitoring scans.

**Key Capabilities:**
- Intelligent orchestration of 15 reconnaissance tools (nmap, subfinder, nuclei, etc.)
- Asynchronous task execution for parallel scanning
- Interactive TUI dashboard built with Textual
- Session management and professional report generation
- Risk-based asset and finding prioritization

## Technology Stack

- **Language:** Python 3.11+ (required)
- **CLI Framework:** Typer with Rich for terminal output
- **TUI Framework:** Textual for the interactive dashboard
- **Async:** asyncio and aiosqlite for concurrent operations
- **Data Validation:** Pydantic v2 for configuration and data models
- **Testing:** pytest with pytest-asyncio
- **Linting:** ruff for code quality and formatting
- **Type Checking:** mypy (with some missing imports allowed)

## Code Style and Standards

### Python Style
- **Target Version:** Python 3.11+
- **Line Length:** 100 characters (configured in pyproject.toml)
- **Formatting:** Use `ruff format` for code formatting
- **Linting:** Use `ruff check` to validate code quality
- **Type Hints:** Always include type hints for function parameters and return values
- **Docstrings:** Use triple-quoted strings for module and function documentation

### Naming Conventions
- **Classes:** PascalCase (e.g., `Orchestrator`, `ScanConfig`)
- **Functions/Methods:** snake_case (e.g., `ensure_directories`, `create_default_registry`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `CONFIG_DIR`, `DATA_DIR`)
- **Private Methods:** Prefix with underscore (e.g., `_internal_method`)

### Async Patterns
- Use `async`/`await` for I/O operations and tool execution
- Leverage asyncio for parallel task execution
- Use `aiosqlite` for database operations
- Follow existing async patterns in `core/orchestrator.py` and `core/events.py`

## Project Structure

```
reconpilot/
├── reconpilot/
│   ├── core/           # Core orchestration logic (Orchestrator, EventBus, Database)
│   ├── tools/          # Tool adapters and registry
│   │   └── adapters/   # Individual tool integrations (nmap, subfinder, etc.)
│   ├── dashboard/      # Textual TUI dashboard
│   │   └── widgets/    # Custom dashboard widgets
│   ├── reports/        # Report generation (HTML, Markdown, JSON)
│   ├── utils/          # Utility functions and helpers
│   ├── cli.py          # CLI interface with Typer
│   └── config.py       # Configuration management with Pydantic
├── tests/              # Test suite
├── scripts/            # Installation and utility scripts
└── .github/            # CI/CD workflows
```

## Testing Practices

### Running Tests
- Run all tests: `make test` or `pytest tests/ -v`
- Run with coverage: `pytest tests/ -v --cov=reconpilot --cov-report=term`
- Tests are automatically run on CI for Python 3.11 and 3.12

### Writing Tests
- Use pytest for all tests
- Use `pytest-asyncio` for testing async code (set `asyncio_mode = "auto"` in pyproject.toml)
- Follow existing test patterns in `tests/test_cli.py` and `tests/test_orchestrator.py`
- Use `CliRunner` from `typer.testing` for testing CLI commands
- Keep tests focused and isolated
- Mock external tool calls when appropriate

### Test Structure
```python
"""Tests for module_name"""
from typer.testing import CliRunner

def test_specific_feature():
    """Test description"""
    # Arrange
    # Act
    # Assert
```

## Development Workflow

### Setup
```bash
make dev          # Install with development dependencies
```

### Code Quality
```bash
make format       # Format code with ruff
make lint         # Check code with ruff
mypy reconpilot/  # Type checking (some missing imports allowed)
```

### Building
```bash
make build        # Build package for distribution
make clean        # Clean build artifacts
```

### CLI Commands
The CLI has two entry points: `reconpilot` and `rp` (alias)

Main commands:
- `reconpilot scan <target>` - Start reconnaissance scan
- `reconpilot tools list|check` - Manage tool integrations
- `reconpilot sessions list|show|delete` - Session management
- `reconpilot report <session-id>` - Generate reports
- `reconpilot config show|edit|reset` - Configuration management

## Security Considerations

**CRITICAL:** This is a security tool designed for legal penetration testing only.

- All tool integrations must validate input to prevent command injection
- User-provided data should be sanitized before passing to external tools
- Configuration files may contain sensitive data (API keys, webhook URLs)
- Session data may contain sensitive reconnaissance findings
- Reports should be stored securely with appropriate permissions

When adding new features:
- Validate all user inputs
- Use subprocess safely (avoid shell=True when possible)
- Sanitize data before logging or displaying
- Document security implications of new tools or features

## Dependencies

### Core Dependencies
- typer, rich - CLI and terminal output
- textual - TUI dashboard
- pydantic - Data validation and configuration
- aiosqlite - Async database operations
- jinja2 - Template rendering for reports
- pyyaml - Configuration file parsing
- httpx - HTTP client for web reconnaissance

### External Tools
ReconPilot integrates with 15 external security tools that must be installed separately:
- DNS/OSINT: whois, dnsrecon, dnsx
- Subdomains: subfinder, amass, assetfinder
- Port Scanning: nmap, masscan, rustscan
- Web: httpx, whatweb, wafw00f
- Vulnerabilities: nuclei, nikto, wpscan

See `scripts/check-tools.py` for the complete tool list.

## Common Patterns

### Configuration with Pydantic
```python
from pydantic import BaseModel, Field

class MyConfig(BaseModel):
    """Configuration description"""
    enabled: bool = True
    timeout: int = Field(default=300, ge=0)
    items: list[str] = Field(default_factory=list)
```

### CLI Commands with Typer
```python
@app.command()
def my_command(
    target: str = typer.Argument(..., help="Description"),
    option: str = typer.Option("default", help="Option description"),
) -> None:
    """Command description"""
    # Implementation
```

### Async Tool Execution
```python
async def run_tool(self, target: str) -> dict:
    """Run tool asynchronously"""
    # Validate inputs
    # Execute tool
    # Parse results
    return results
```

## Contributing Guidelines

1. Follow existing code style and patterns
2. Include type hints for all new functions
3. Write tests for new features
4. Update documentation when adding features
5. Run `make format` and `make lint` before committing
6. Ensure tests pass with `make test`
7. Keep commits focused and atomic

## Useful Resources

- Textual Documentation: https://textual.textualize.io/
- Typer Documentation: https://typer.tiangolo.com/
- Pydantic Documentation: https://docs.pydantic.dev/
- Python Async/Await: https://docs.python.org/3/library/asyncio.html

## Notes

- The project uses modern Python features (3.11+) including structural pattern matching
- Dashboard uses Textual widgets for reactive UI updates
- Event-driven architecture using EventBus for component communication
- Database schema is managed in `core/database.py`
- Tool adapters should follow the interface defined in `tools/registry.py`
