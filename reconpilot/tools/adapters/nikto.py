"""Nikto tool adapter"""
import re

from reconpilot.core.models import Finding, Severity
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class NiktoAdapter(ToolAdapter):
    """Adapter for nikto tool"""

    def __init__(self):
        config = ToolConfig(
            name="nikto",
            binary="nikto",
            category=ToolCategory.VULNERABILITY,
            description="Web server scanner",
            timeout=600,
            produces=["vulnerability"],
            consumes=["http_service"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build nikto command"""
        return [
            "nikto",
            "-h", target,
            "-nointeractive",
        ]

    def parse_output(self, output: str) -> ToolResult:
        """Parse nikto output"""
        findings = []

        # Extract target from output
        target_match = re.search(r"Target:\s+(.+)", output, re.IGNORECASE)
        target_host = target_match.group(1).strip() if target_match else "unknown"

        # Parse findings from output
        for line in output.split("\n"):
            # Look for vulnerability lines (usually start with +)
            if line.strip().startswith("+"):
                line = line.strip()[1:].strip()
                
                # Determine severity based on keywords
                severity = Severity.INFO
                if any(kw in line.lower() for kw in ["vulnerable", "exploit", "exposed"]):
                    severity = Severity.HIGH
                elif any(kw in line.lower() for kw in ["outdated", "deprecated", "old"]):
                    severity = Severity.MEDIUM
                elif any(kw in line.lower() for kw in ["missing", "weak"]):
                    severity = Severity.LOW
                
                # Extract OSVDB reference if present
                osvdb_match = re.search(r"OSVDB-(\d+)", line)
                metadata = {}
                if osvdb_match:
                    metadata["osvdb"] = osvdb_match.group(1)
                
                if len(line) > 10:  # Filter out very short lines
                    findings.append(
                        Finding(
                            severity=severity,
                            title="Nikto Finding",
                            host=target_host,
                            description=line,
                            discovered_by="nikto",
                            evidence=line,
                            metadata=metadata,
                        )
                    )

        return ToolResult(
            tool_name="nikto",
            success=True,
            findings=findings,
            raw_output=output,
        )
