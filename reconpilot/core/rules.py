"""Rules engine for task chaining"""
from dataclasses import dataclass
from typing import Callable

from reconpilot.core.models import Asset


@dataclass
class ChainRule:
    """Represents a rule for chaining tasks"""
    name: str
    condition: Callable[[Asset], bool]
    target_tool: str
    reason: str
    priority: int = 5


class RulesEngine:
    """Engine for determining task chains based on discoveries"""

    def __init__(self):
        self.rules: list[ChainRule] = []
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Initialize default chaining rules"""
        self.rules = [
            # Domain -> DNS enumeration
            ChainRule(
                name="domain_to_dns",
                condition=lambda a: a.type == "domain",
                target_tool="dnsrecon",
                reason="Enumerate DNS records",
                priority=10,
            ),
            ChainRule(
                name="domain_to_whois",
                condition=lambda a: a.type == "domain",
                target_tool="whois",
                reason="Get WHOIS information",
                priority=9,
            ),
            # Domain -> Subdomain enumeration
            ChainRule(
                name="domain_to_subfinder",
                condition=lambda a: a.type == "domain",
                target_tool="subfinder",
                reason="Find subdomains",
                priority=10,
            ),
            ChainRule(
                name="domain_to_amass",
                condition=lambda a: a.type == "domain",
                target_tool="amass",
                reason="Deep subdomain enumeration",
                priority=8,
            ),
            # Subdomain -> DNS resolution
            ChainRule(
                name="subdomain_to_dnsx",
                condition=lambda a: a.type == "subdomain",
                target_tool="dnsx",
                reason="Resolve subdomain IPs",
                priority=9,
            ),
            # Subdomain -> HTTP probing
            ChainRule(
                name="subdomain_to_httpx",
                condition=lambda a: a.type == "subdomain",
                target_tool="httpx",
                reason="Probe for HTTP services",
                priority=8,
            ),
            # HTTP service -> Web tech identification
            ChainRule(
                name="http_to_whatweb",
                condition=lambda a: a.type == "http_service",
                target_tool="whatweb",
                reason="Identify web technologies",
                priority=7,
            ),
            ChainRule(
                name="http_to_wafw00f",
                condition=lambda a: a.type == "http_service",
                target_tool="wafw00f",
                reason="Detect WAF",
                priority=6,
            ),
            # HTTP service -> Vulnerability scanning
            ChainRule(
                name="http_to_nuclei",
                condition=lambda a: a.type == "http_service",
                target_tool="nuclei",
                reason="Scan for vulnerabilities",
                priority=7,
            ),
            # WordPress -> WPScan
            ChainRule(
                name="wordpress_to_wpscan",
                condition=lambda a: a.type == "http_service" and a.metadata.get("technology") == "WordPress",
                target_tool="wpscan",
                reason="Scan WordPress site",
                priority=8,
            ),
            # IP -> Port scanning
            ChainRule(
                name="ip_to_nmap",
                condition=lambda a: a.type == "ip",
                target_tool="nmap",
                reason="Scan for open ports",
                priority=9,
            ),
            ChainRule(
                name="ip_to_rustscan",
                condition=lambda a: a.type == "ip",
                target_tool="rustscan",
                reason="Fast port scan",
                priority=8,
            ),
        ]

    def get_next_tools(self, asset: Asset) -> list[tuple[str, str, int]]:
        """Get list of tools to run based on asset type"""
        matches = []
        for rule in self.rules:
            if rule.condition(asset):
                matches.append((rule.target_tool, rule.reason, rule.priority))
        
        # Sort by priority (higher first)
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches

    def add_rule(self, rule: ChainRule) -> None:
        """Add a custom chaining rule"""
        self.rules.append(rule)
