"""Nmap tool adapter"""
import xml.etree.ElementTree as ET

from reconpilot.core.models import Asset, Finding, Severity
from reconpilot.tools.base import ToolAdapter, ToolCategory, ToolConfig, ToolResult


class NmapAdapter(ToolAdapter):
    """Adapter for nmap tool"""

    def __init__(self):
        config = ToolConfig(
            name="nmap",
            binary="nmap",
            category=ToolCategory.PORT_SCAN,
            description="Network port scanner",
            timeout=600,
            produces=["port", "service"],
            consumes=["ip", "domain"],
        )
        super().__init__(config)

    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build nmap command"""
        return [
            "nmap",
            "-sV",
            "-sC",
            "--top-ports", "1000",
            "-oX", "-",
            target,
        ]

    def parse_output(self, output: str) -> ToolResult:
        """Parse nmap XML output"""
        assets = []
        findings = []

        try:
            root = ET.fromstring(output)
            
            for host in root.findall(".//host"):
                # Get host address
                addr_elem = host.find(".//address[@addrtype='ipv4']")
                if addr_elem is None:
                    addr_elem = host.find(".//address[@addrtype='ipv6']")
                if addr_elem is None:
                    continue
                
                host_addr = addr_elem.get("addr", "")
                
                # Parse ports
                for port in host.findall(".//port"):
                    port_id = port.get("portid", "")
                    protocol = port.get("protocol", "tcp")
                    
                    state = port.find("state")
                    if state is None or state.get("state") != "open":
                        continue
                    
                    service = port.find("service")
                    service_name = service.get("name", "unknown") if service is not None else "unknown"
                    service_product = service.get("product", "") if service is not None else ""
                    service_version = service.get("version", "") if service is not None else ""
                    
                    # Create asset
                    assets.append(
                        Asset(
                            type="port",
                            value=f"{host_addr}:{port_id}",
                            discovered_by="nmap",
                            metadata={
                                "port": port_id,
                                "protocol": protocol,
                                "service": service_name,
                                "product": service_product,
                                "version": service_version,
                            },
                        )
                    )
                    
                    # Check for vulnerable services
                    if service_name in ["telnet", "ftp", "smtp"]:
                        findings.append(
                            Finding(
                                severity=Severity.MEDIUM,
                                title=f"Insecure Service: {service_name.upper()}",
                                host=host_addr,
                                description=f"Insecure {service_name} service detected on port {port_id}",
                                discovered_by="nmap",
                                evidence=f"Port {port_id}/{protocol} - {service_name}",
                                recommendations=[
                                    f"Disable {service_name} if not required",
                                    "Use encrypted alternatives (SSH, SFTP, etc.)",
                                ],
                            )
                        )
                    
                    # Check for database ports
                    db_ports = {
                        "3306": "MySQL",
                        "5432": "PostgreSQL",
                        "27017": "MongoDB",
                        "6379": "Redis",
                        "1433": "MSSQL",
                    }
                    if port_id in db_ports:
                        findings.append(
                            Finding(
                                severity=Severity.HIGH,
                                title=f"Exposed Database: {db_ports[port_id]}",
                                host=host_addr,
                                description=f"{db_ports[port_id]} database port exposed",
                                discovered_by="nmap",
                                evidence=f"Port {port_id}/{protocol} - {service_name}",
                                recommendations=[
                                    "Restrict database access to trusted IPs only",
                                    "Use strong authentication",
                                    "Enable SSL/TLS encryption",
                                ],
                            )
                        )

        except ET.ParseError:
            # Fallback to text parsing
            pass

        return ToolResult(
            tool_name="nmap",
            success=True,
            assets=assets,
            findings=findings,
            raw_output=output,
        )
