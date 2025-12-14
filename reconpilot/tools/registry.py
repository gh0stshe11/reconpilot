"""Tool registry for managing adapters"""
from typing import Optional

from reconpilot.tools.base import ToolAdapter, ToolCategory


class ToolRegistry:
    """Registry for tool adapters"""

    def __init__(self):
        self._tools: dict[str, ToolAdapter] = {}

    def register(self, adapter: ToolAdapter) -> None:
        """Register a tool adapter"""
        self._tools[adapter.config.name] = adapter

    def get(self, name: str) -> Optional[ToolAdapter]:
        """Get a tool adapter by name"""
        return self._tools.get(name)

    def get_by_category(self, category: ToolCategory) -> list[ToolAdapter]:
        """Get all tools in a category"""
        return [
            tool for tool in self._tools.values()
            if tool.config.category == category
        ]

    def get_available(self) -> list[ToolAdapter]:
        """Get all available tools"""
        return [tool for tool in self._tools.values() if tool.is_available()]

    def get_for_asset_type(self, asset_type: str) -> list[ToolAdapter]:
        """Get tools that can process a specific asset type"""
        return [
            tool for tool in self._tools.values()
            if asset_type in tool.config.consumes
        ]

    def get_producers(self, asset_type: str) -> list[ToolAdapter]:
        """Get tools that produce a specific asset type"""
        return [
            tool for tool in self._tools.values()
            if asset_type in tool.config.produces
        ]

    def all_tools(self) -> list[ToolAdapter]:
        """Get all registered tools"""
        return list(self._tools.values())


def create_default_registry() -> ToolRegistry:
    """Create and populate the default tool registry"""
    from reconpilot.tools.adapters.amass import AmassAdapter
    from reconpilot.tools.adapters.assetfinder import AssetfinderAdapter
    from reconpilot.tools.adapters.dnsrecon import DnsreconAdapter
    from reconpilot.tools.adapters.dnsx import DnsxAdapter
    from reconpilot.tools.adapters.httpx import HttpxAdapter
    from reconpilot.tools.adapters.masscan import MasscanAdapter
    from reconpilot.tools.adapters.nikto import NiktoAdapter
    from reconpilot.tools.adapters.nmap import NmapAdapter
    from reconpilot.tools.adapters.nuclei import NucleiAdapter
    from reconpilot.tools.adapters.rustscan import RustscanAdapter
    from reconpilot.tools.adapters.subfinder import SubfinderAdapter
    from reconpilot.tools.adapters.wafw00f import Wafw00fAdapter
    from reconpilot.tools.adapters.whatweb import WhatwWebAdapter
    from reconpilot.tools.adapters.whois import WhoisAdapter
    from reconpilot.tools.adapters.wpscan import WpscanAdapter

    registry = ToolRegistry()
    
    # Register all adapters
    registry.register(WhoisAdapter())
    registry.register(DnsreconAdapter())
    registry.register(DnsxAdapter())
    registry.register(SubfinderAdapter())
    registry.register(AmassAdapter())
    registry.register(AssetfinderAdapter())
    registry.register(NmapAdapter())
    registry.register(MasscanAdapter())
    registry.register(RustscanAdapter())
    registry.register(HttpxAdapter())
    registry.register(WhatwWebAdapter())
    registry.register(Wafw00fAdapter())
    registry.register(NucleiAdapter())
    registry.register(NiktoAdapter())
    registry.register(WpscanAdapter())

    return registry
