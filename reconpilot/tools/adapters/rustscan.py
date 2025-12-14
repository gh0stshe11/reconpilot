"""Rustscan tool adapter"""
import re

from reconpilot.core.models import Asset
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class RustscanAdapter(ToolAdapter):
    """Adapter for rustscan tool"""

    def __init__(self):
        config = ToolConfig(
            name="rustscan",
            binary="rustscan",
            category=ToolCategory.PORT_SCAN,
            description="Fast port scanner",
            timeout=300,
            produces=["port"],
            consumes=["ip", "domain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build rustscan command"""
        return [
            "rustscan",
            "-a", target,
            "--ulimit", "5000",
            "--greppable",
        ]

    def parse_output(self, output: str) -> ToolResult:
        """Parse rustscan output"""
        assets = []

        # RustScan output format: IP -> [port1, port2, ...]
        for line in output.strip().split("\n"):
            match = re.search(r"(\S+)\s+->\s+\[(.+)\]", line)
            if match:
                ip = match.group(1)
                ports_str = match.group(2)
                
                for port in ports_str.split(","):
                    port = port.strip()
                    if port.isdigit():
                        assets.append(
                            Asset(
                                type="port",
                                value=f"{ip}:{port}",
                                discovered_by="rustscan",
                                metadata={"port": port},
                            )
                        )

        return ToolResult(
            tool_name="rustscan",
            success=True,
            assets=assets,
            raw_output=output,
        )
