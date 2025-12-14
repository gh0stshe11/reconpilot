"""Nuclei tool adapter"""
import json

from reconpilot.core.models import Finding, Severity
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class NucleiAdapter(ToolAdapter):
    """Adapter for nuclei tool"""

    def __init__(self):
        config = ToolConfig(
            name="nuclei",
            binary="nuclei",
            category=ToolCategory.VULNERABILITY,
            description="Vulnerability scanner",
            timeout=600,
            produces=["vulnerability"],
            consumes=["http_service"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build nuclei command"""
        return [
            "nuclei",
            "-u", target,
            "-json",
            "-silent",
        ]

    def parse_output(self, output: str) -> ToolResult:
        """Parse nuclei JSON output"""
        findings = []

        for line in output.strip().split("\n"):
            if not line:
                continue
            
            try:
                data = json.loads(line)
                
                info = data.get("info", {})
                template_id = data.get("template-id", "")
                matched_at = data.get("matched-at", "")
                severity_str = info.get("severity", "info").lower()
                name = info.get("name", template_id)
                description = info.get("description", "")
                
                # Map nuclei severity to our severity
                severity_map = {
                    "critical": Severity.CRITICAL,
                    "high": Severity.HIGH,
                    "medium": Severity.MEDIUM,
                    "low": Severity.LOW,
                    "info": Severity.INFO,
                }
                severity = severity_map.get(severity_str, Severity.INFO)
                
                findings.append(
                    Finding(
                        severity=severity,
                        title=name,
                        host=matched_at,
                        description=description or f"Nuclei template: {template_id}",
                        discovered_by="nuclei",
                        evidence=json.dumps(data, indent=2),
                        metadata={"template_id": template_id},
                        recommendations=[
                            "Review the vulnerability details",
                            "Apply patches or mitigations",
                            "Verify the finding manually",
                        ],
                    )
                )

            except json.JSONDecodeError:
                continue

        return ToolResult(
            tool_name="nuclei",
            success=True,
            findings=findings,
            raw_output=output,
        )

    def parse_partial(self, output: str) -> ToolResult:
        """Parse partial output for real-time updates"""
        return self.parse_output(output)
