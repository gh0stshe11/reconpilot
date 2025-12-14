"""Configuration management for ReconPilot"""
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


# Default paths
CONFIG_DIR = Path.home() / ".reconpilot"
DATA_DIR = CONFIG_DIR / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
REPORTS_DIR = Path.cwd() / "reports"


class ToolConfig(BaseModel):
    """Tool-specific configuration"""
    enabled: bool = True
    timeout: int = 300
    custom_args: list[str] = Field(default_factory=list)


class NotificationConfig(BaseModel):
    """Notification settings"""
    enabled: bool = False
    webhook_url: Optional[str] = None
    email: Optional[str] = None


class ReportingConfig(BaseModel):
    """Reporting settings"""
    format: str = "html"
    auto_save: bool = True
    output_dir: str = str(REPORTS_DIR)


class ScopeConfig(BaseModel):
    """Scope configuration"""
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    in_scope_only: bool = True


class GeneralConfig(BaseModel):
    """General settings"""
    max_parallel_tasks: int = 3
    stealth_mode: bool = False
    passive_only: bool = False
    user_agent: str = "ReconPilot/0.1.0"


class Config(BaseModel):
    """Main configuration"""
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    scope: ScopeConfig = Field(default_factory=ScopeConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    tools: dict[str, ToolConfig] = Field(default_factory=dict)

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "Config":
        """Load configuration from file"""
        if config_file is None:
            config_file = CONFIG_DIR / "config.yaml"

        if not config_file.exists():
            # Return default config
            return cls()

        with open(config_file, "r") as f:
            data = yaml.safe_load(f)
            return cls(**data if data else {})

    def save(self, config_file: Optional[Path] = None) -> None:
        """Save configuration to file"""
        if config_file is None:
            config_file = CONFIG_DIR / "config.yaml"

        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)


def ensure_directories() -> None:
    """Ensure all required directories exist"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
