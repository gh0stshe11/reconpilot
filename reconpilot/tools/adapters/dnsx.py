"""DNSX tool adapter"""
import json

from reconpilot.core.models import Asset
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class DnsxAdapter(ToolAdapter):
    """Adapter for dnsx tool"""

    def __init__(self):
        config = ToolConfig(
            name="dnsx",
            binary="dnsx",
            category=ToolCategory.DNS,
            description="Fast DNS resolution",
            produces=["ip"],
            consumes=["domain", "subdomain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build dnsx command"""
        return ["dnsx", "-silent", "-json", "-a", "-aaaa", "-host", target]

    def parse_output(self, output: str) -> ToolResult:
        """Parse dnsx JSON output"""
        assets = []

        for line in output.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                host = data.get("host", "")
                
                # A records
                for ip in data.get("a", []):
                    assets.append(
                        Asset(
                            type="ip",
                            value=ip,
                            discovered_by="dnsx",
                            metadata={"hostname": host},
                        )
                    )
                
                # AAAA records
                for ip in data.get("aaaa", []):
                    assets.append(
                        Asset(
                            type="ip",
                            value=ip,
                            discovered_by="dnsx",
                            metadata={"hostname": host, "ipv6": True},
                        )
                    )
            except json.JSONDecodeError:
                continue

        return ToolResult(
            tool_name="dnsx",
            success=True,
            assets=assets,
            raw_output=output,
        )
