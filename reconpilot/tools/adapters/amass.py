"""Amass tool adapter"""
from reconpilot.core.models import Asset
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class AmassAdapter(ToolAdapter):
    """Adapter for amass tool"""

    def __init__(self):
        config = ToolConfig(
            name="amass",
            binary="amass",
            category=ToolCategory.SUBDOMAIN,
            description="Advanced subdomain enumeration",
            timeout=600,
            produces=["subdomain"],
            consumes=["domain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build amass command"""
        return ["amass", "enum", "-d", target, "-passive"]

    def parse_output(self, output: str) -> ToolResult:
        """Parse amass output"""
        assets = []

        for line in output.strip().split("\n"):
            subdomain = line.strip()
            if subdomain and "." in subdomain:
                assets.append(
                    Asset(
                        type="subdomain",
                        value=subdomain,
                        discovered_by="amass",
                    )
                )

        return ToolResult(
            tool_name="amass",
            success=True,
            assets=assets,
            raw_output=output,
        )

    def parse_partial(self, output: str) -> ToolResult:
        """Parse partial output for real-time updates"""
        return self.parse_output(output)
