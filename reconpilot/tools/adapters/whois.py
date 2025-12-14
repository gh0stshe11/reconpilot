"""WHOIS tool adapter"""
import re

from reconpilot.core.models import Asset, Finding, Severity
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class WhoisAdapter(ToolAdapter):
    """Adapter for whois tool"""

    def __init__(self):
        config = ToolConfig(
            name="whois",
            binary="whois",
            category=ToolCategory.OSINT,
            description="Query WHOIS information",
            produces=["whois_info"],
            consumes=["domain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build whois command"""
        return ["whois", target]

    def parse_output(self, output: str) -> ToolResult:
        """Parse whois output"""
        assets = []
        findings = []

        # Extract registrar
        registrar_match = re.search(r"Registrar:\s+(.+)", output, re.IGNORECASE)
        if registrar_match:
            assets.append(
                Asset(
                    type="whois_info",
                    value=f"Registrar: {registrar_match.group(1).strip()}",
                    discovered_by="whois",
                )
            )

        # Extract creation date
        created_match = re.search(r"Creation Date:\s+(.+)", output, re.IGNORECASE)
        if created_match:
            assets.append(
                Asset(
                    type="whois_info",
                    value=f"Created: {created_match.group(1).strip()}",
                    discovered_by="whois",
                )
            )

        # Extract nameservers
        nameservers = re.findall(r"Name Server:\s+(.+)", output, re.IGNORECASE)
        for ns in nameservers:
            assets.append(
                Asset(
                    type="nameserver",
                    value=ns.strip().lower(),
                    discovered_by="whois",
                )
            )

        # Check for privacy protection
        if "redacted" in output.lower() or "privacy" in output.lower():
            # Extract domain from output
            domain_match = re.search(r"Domain Name:\s+(.+)", output, re.IGNORECASE)
            domain = domain_match.group(1).strip() if domain_match else "unknown"
            
            findings.append(
                Finding(
                    severity=Severity.INFO,
                    title="Domain Privacy Enabled",
                    host=domain,
                    description="Domain has privacy protection enabled",
                    discovered_by="whois",
                )
            )

        return ToolResult(
            tool_name="whois",
            success=True,
            assets=assets,
            findings=findings,
            raw_output=output,
        )
