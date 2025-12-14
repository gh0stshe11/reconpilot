"""Assetfinder tool adapter"""
from reconpilot.core.models import Asset
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class AssetfinderAdapter(ToolAdapter):
    """Adapter for assetfinder tool"""

    def __init__(self):
        config = ToolConfig(
            name="assetfinder",
            binary="assetfinder",
            category=ToolCategory.SUBDOMAIN,
            description="Find subdomains and related domains",
            produces=["subdomain"],
            consumes=["domain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build assetfinder command"""
        return ["assetfinder", "--subs-only", target]

    def parse_output(self, output: str) -> ToolResult:
        """Parse assetfinder output"""
        assets = []

        for line in output.strip().split("\n"):
            subdomain = line.strip()
            if subdomain and "." in subdomain:
                assets.append(
                    Asset(
                        type="subdomain",
                        value=subdomain,
                        discovered_by="assetfinder",
                    )
                )

        return ToolResult(
            tool_name="assetfinder",
            success=True,
            assets=assets,
            raw_output=output,
        )

    def parse_partial(self, output: str) -> ToolResult:
        """Parse partial output for real-time updates"""
        return self.parse_output(output)
