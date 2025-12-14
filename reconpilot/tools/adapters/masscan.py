"""Masscan tool adapter"""
import json

from reconpilot.core.models import Asset
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class MasscanAdapter(ToolAdapter):
    """Adapter for masscan tool
    
    Note: Masscan requires root privileges to run. Ensure you have
    appropriate permissions and understand the security implications.
    """

    def __init__(self):
        config = ToolConfig(
            name="masscan",
            binary="masscan",
            category=ToolCategory.PORT_SCAN,
            description="Fast port scanner",
            requires_root=True,
            timeout=300,
            produces=["port"],
            consumes=["ip", "domain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build masscan command"""
        return [
            "masscan",
            target,
            "-p1-65535",
            "--rate=1000",
            "-oJ", "-",
        ]

    def parse_output(self, output: str) -> ToolResult:
        """Parse masscan JSON output"""
        assets = []

        for line in output.strip().split("\n"):
            if not line or line.startswith("#"):
                continue
            
            # Remove trailing comma if present
            line = line.rstrip(",")
            
            try:
                data = json.loads(line)
                ip = data.get("ip", "")
                ports = data.get("ports", [])
                
                for port_info in ports:
                    port = port_info.get("port", "")
                    proto = port_info.get("proto", "tcp")
                    
                    if ip and port:
                        assets.append(
                            Asset(
                                type="port",
                                value=f"{ip}:{port}",
                                discovered_by="masscan",
                                metadata={
                                    "port": str(port),
                                    "protocol": proto,
                                },
                            )
                        )
            except json.JSONDecodeError:
                continue

        return ToolResult(
            tool_name="masscan",
            success=True,
            assets=assets,
            raw_output=output,
        )
