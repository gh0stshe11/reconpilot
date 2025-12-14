"""Wafw00f tool adapter"""
import re

from reconpilot.core.models import Asset, Finding, Severity
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class Wafw00fAdapter(ToolAdapter):
    """Adapter for wafw00f tool"""

    def __init__(self):
        config = ToolConfig(
            name="wafw00f",
            binary="wafw00f",
            category=ToolCategory.TECHNOLOGY,
            description="Web application firewall detector",
            produces=["waf"],
            consumes=["http_service"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build wafw00f command"""
        return ["wafw00f", target]

    def parse_output(self, output: str) -> ToolResult:
        """Parse wafw00f output"""
        assets = []
        findings = []

        # Look for WAF detection
        for line in output.split("\n"):
            if "is behind" in line.lower() or "detected" in line.lower():
                # Extract WAF name
                if "(" in line and ")" in line:
                    waf_name = line.split("(")[1].split(")")[0]
                    
                    assets.append(
                        Asset(
                            type="waf",
                            value=waf_name,
                            discovered_by="wafw00f",
                        )
                    )
                    
                    # Extract URL from output
                    url_match = re.search(r"https?://[^\s]+", output)
                    url = url_match.group(0) if url_match else "unknown"
                    
                    findings.append(
                        Finding(
                            severity=Severity.INFO,
                            title=f"WAF Detected: {waf_name}",
                            host=url,
                            description=f"Web application firewall detected: {waf_name}",
                            discovered_by="wafw00f",
                            evidence=line.strip(),
                            recommendations=[
                                "WAF may block certain security testing",
                                "Consider WAF bypass techniques if authorized",
                            ],
                        )
                    )

        return ToolResult(
            tool_name="wafw00f",
            success=True,
            assets=assets,
            findings=findings,
            raw_output=output,
        )
