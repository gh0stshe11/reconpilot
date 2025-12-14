"""HTTPX tool adapter"""
import json

from reconpilot.core.models import Asset, Finding, Severity
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class HttpxAdapter(ToolAdapter):
    """Adapter for httpx tool"""

    def __init__(self):
        config = ToolConfig(
            name="httpx",
            binary="httpx",
            category=ToolCategory.WEB_PROBE,
            description="HTTP probe tool",
            produces=["http_service"],
            consumes=["domain", "subdomain", "ip"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build httpx command"""
        return [
            "httpx",
            "-silent",
            "-json",
            "-status-code",
            "-tech-detect",
            "-title",
            "-host", target,
        ]

    def parse_output(self, output: str) -> ToolResult:
        """Parse httpx JSON output"""
        assets = []
        findings = []

        for line in output.strip().split("\n"):
            if not line:
                continue
            
            try:
                data = json.loads(line)
                url = data.get("url", "")
                status_code = data.get("status_code", 0)
                title = data.get("title", "")
                technologies = data.get("tech", [])
                
                if url:
                    metadata = {
                        "status_code": status_code,
                        "title": title,
                        "technologies": technologies,
                    }
                    
                    assets.append(
                        Asset(
                            type="http_service",
                            value=url,
                            discovered_by="httpx",
                            metadata=metadata,
                        )
                    )
                    
                    # Check for interesting findings
                    if status_code in [401, 403]:
                        findings.append(
                            Finding(
                                severity=Severity.MEDIUM,
                                title=f"Protected Resource ({status_code})",
                                host=url,
                                description=f"Found protected resource with status {status_code}",
                                discovered_by="httpx",
                                evidence=f"Status: {status_code}, Title: {title}",
                            )
                        )
                    
                    # Check for sensitive titles
                    sensitive_keywords = ["admin", "login", "dashboard", "panel", "console"]
                    if any(kw in title.lower() for kw in sensitive_keywords):
                        findings.append(
                            Finding(
                                severity=Severity.MEDIUM,
                                title="Sensitive Page Detected",
                                host=url,
                                description=f"Found potentially sensitive page: {title}",
                                discovered_by="httpx",
                                evidence=f"Title: {title}",
                            )
                        )

            except json.JSONDecodeError:
                continue

        return ToolResult(
            tool_name="httpx",
            success=True,
            assets=assets,
            findings=findings,
            raw_output=output,
        )

    def parse_partial(self, output: str) -> ToolResult:
        """Parse partial output for real-time updates"""
        return self.parse_output(output)
