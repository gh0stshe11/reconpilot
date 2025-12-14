"""WhatWeb tool adapter"""
import json

from reconpilot.core.models import Asset
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class WhatwWebAdapter(ToolAdapter):
    """Adapter for whatweb tool"""

    def __init__(self):
        config = ToolConfig(
            name="whatweb",
            binary="whatweb",
            category=ToolCategory.TECHNOLOGY,
            description="Web technology identifier",
            produces=["technology"],
            consumes=["http_service"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build whatweb command"""
        return ["whatweb", "--log-json=/dev/stdout", target]

    def parse_output(self, output: str) -> ToolResult:
        """Parse whatweb JSON output"""
        assets = []

        for line in output.strip().split("\n"):
            if not line:
                continue
            
            try:
                data = json.loads(line)
                target_url = data.get("target", "")
                plugins = data.get("plugins", {})
                
                for plugin_name, plugin_data in plugins.items():
                    if isinstance(plugin_data, dict):
                        version = plugin_data.get("version", [""])[0] if "version" in plugin_data else ""
                        
                        tech_value = plugin_name
                        if version:
                            tech_value += f" {version}"
                        
                        assets.append(
                            Asset(
                                type="technology",
                                value=tech_value,
                                discovered_by="whatweb",
                                metadata={
                                    "url": target_url,
                                    "technology": plugin_name,
                                    "version": version,
                                },
                            )
                        )

            except json.JSONDecodeError:
                continue

        return ToolResult(
            tool_name="whatweb",
            success=True,
            assets=assets,
            raw_output=output,
        )
