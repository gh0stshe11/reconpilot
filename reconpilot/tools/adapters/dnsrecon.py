"""DNSRecon tool adapter"""
import json
import re

from reconpilot.core.models import Asset
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class DnsreconAdapter(ToolAdapter):
    """Adapter for dnsrecon tool"""

    def __init__(self):
        config = ToolConfig(
            name="dnsrecon",
            binary="dnsrecon",
            category=ToolCategory.DNS,
            description="DNS enumeration tool",
            produces=["ip", "subdomain", "dns_record"],
            consumes=["domain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build dnsrecon command"""
        return ["dnsrecon", "-d", target, "-j", "/dev/stdout"]

    def parse_output(self, output: str) -> ToolResult:
        """Parse dnsrecon output"""
        assets = []

        # Try JSON format first
        try:
            for line in output.split("\n"):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if isinstance(data, list):
                        for record in data:
                            self._parse_record(record, assets)
                    else:
                        self._parse_record(data, assets)
                except json.JSONDecodeError:
                    continue
        except Exception:
            # Fallback to regex parsing
            self._parse_text_output(output, assets)

        return ToolResult(
            tool_name="dnsrecon",
            success=True,
            assets=assets,
            raw_output=output,
        )

    def _parse_record(self, record: dict, assets: list[Asset]) -> None:
        """Parse a DNS record"""
        record_type = record.get("type", "")
        name = record.get("name", "")
        address = record.get("address", "")

        if record_type == "A" and address:
            assets.append(
                Asset(
                    type="ip",
                    value=address,
                    discovered_by="dnsrecon",
                    metadata={"hostname": name},
                )
            )
        elif record_type == "AAAA" and address:
            assets.append(
                Asset(
                    type="ip",
                    value=address,
                    discovered_by="dnsrecon",
                    metadata={"hostname": name, "ipv6": True},
                )
            )
        elif record_type in ["CNAME", "NS", "MX"] and name:
            assets.append(
                Asset(
                    type="dns_record",
                    value=name,
                    discovered_by="dnsrecon",
                    metadata={"record_type": record_type},
                )
            )

    def _parse_text_output(self, output: str, assets: list[Asset]) -> None:
        """Parse text output as fallback"""
        # Extract IPs
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        for ip in re.findall(ip_pattern, output):
            if ip not in ["127.0.0.1", "0.0.0.0"]:
                assets.append(
                    Asset(
                        type="ip",
                        value=ip,
                        discovered_by="dnsrecon",
                    )
                )
