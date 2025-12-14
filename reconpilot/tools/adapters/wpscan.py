"""WPScan tool adapter"""
import json

from reconpilot.core.models import Asset, Finding, Severity
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class WpscanAdapter(ToolAdapter):
    """Adapter for wpscan tool"""

    def __init__(self):
        config = ToolConfig(
            name="wpscan",
            binary="wpscan",
            category=ToolCategory.VULNERABILITY,
            description="WordPress vulnerability scanner",
            timeout=600,
            produces=["vulnerability"],
            consumes=["http_service"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build wpscan command"""
        return [
            "wpscan",
            "--url", target,
            "--format", "json",
            "--random-user-agent",
        ]

    def parse_output(self, output: str) -> ToolResult:
        """Parse wpscan JSON output"""
        assets = []
        findings = []

        try:
            data = json.loads(output)
            
            # Extract target URL from JSON
            target_url = data.get("target_url", "unknown")
            
            # Extract version info
            version = data.get("version", {})
            if version:
                version_num = version.get("number", "")
                if version_num:
                    assets.append(
                        Asset(
                            type="technology",
                            value=f"WordPress {version_num}",
                            discovered_by="wpscan",
                            metadata={"version": version_num},
                        )
                    )
                
                # Check if version is outdated
                if version.get("status") == "insecure":
                    findings.append(
                        Finding(
                            severity=Severity.HIGH,
                            title="Outdated WordPress Version",
                            host=target_url,
                            description=f"WordPress version {version_num} is outdated",
                            discovered_by="wpscan",
                            recommendations=["Update WordPress to the latest version"],
                        )
                    )
            
            # Extract plugin vulnerabilities
            plugins = data.get("plugins", {})
            for plugin_name, plugin_data in plugins.items():
                vulnerabilities = plugin_data.get("vulnerabilities", [])
                for vuln in vulnerabilities:
                    title = vuln.get("title", "WordPress Plugin Vulnerability")
                    
                    findings.append(
                        Finding(
                            severity=Severity.HIGH,
                            title=title,
                            host=target_url,
                            description=f"Plugin {plugin_name}: {title}",
                            discovered_by="wpscan",
                            evidence=json.dumps(vuln, indent=2),
                            recommendations=[
                                f"Update or remove plugin: {plugin_name}",
                                "Review plugin security advisory",
                            ],
                        )
                    )
            
            # Extract theme vulnerabilities
            themes = data.get("themes", {})
            for theme_name, theme_data in themes.items():
                vulnerabilities = theme_data.get("vulnerabilities", [])
                for vuln in vulnerabilities:
                    title = vuln.get("title", "WordPress Theme Vulnerability")
                    
                    findings.append(
                        Finding(
                            severity=Severity.MEDIUM,
                            title=title,
                            host=target_url,
                            description=f"Theme {theme_name}: {title}",
                            discovered_by="wpscan",
                            evidence=json.dumps(vuln, indent=2),
                            recommendations=[
                                f"Update or change theme: {theme_name}",
                                "Review theme security advisory",
                            ],
                        )
                    )

        except json.JSONDecodeError:
            pass

        return ToolResult(
            tool_name="wpscan",
            success=True,
            assets=assets,
            findings=findings,
            raw_output=output,
        )
