"""Subfinder tool adapter"""
from reconpilot.core.models import Asset
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class SubfinderAdapter(ToolAdapter):
    """Adapter for subfinder tool"""

    def __init__(self):
        config = ToolConfig(
            name="subfinder",
            binary="subfinder",
            category=ToolCategory.SUBDOMAIN,
            description="Subdomain discovery tool",
            produces=["subdomain"],
            consumes=["domain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build subfinder command"""
        return ["subfinder", "-d", target, "-silent"]

    def parse_output(self, output: str) -> ToolResult:
        """Parse subfinder output"""
        assets = []

        for line in output.strip().split("\n"):
            subdomain = line.strip()
            if subdomain and "." in subdomain:
                assets.append(
                    Asset(
                        type="subdomain",
                        value=subdomain,
                        discovered_by="subfinder",
                    )
                )

        return ToolResult(
            tool_name="subfinder",
            success=True,
            assets=assets,
            raw_output=output,
        )

    def parse_partial(self, output: str) -> ToolResult:
        """Parse partial output for real-time updates"""
        return self.parse_output(output)
