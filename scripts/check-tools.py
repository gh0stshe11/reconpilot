#!/usr/bin/env python3
"""
Check availability of all reconnaissance tools
"""
import shutil
import sys

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

TOOLS = [
    # DNS/OSINT
    ("whois", "whois", "apt install whois"),
    ("dnsrecon", "dnsrecon", "pip install dnsrecon"),
    ("dnsx", "dnsx", "go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest"),
    
    # Subdomain enumeration
    ("subfinder", "subfinder", "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"),
    ("amass", "amass", "go install github.com/owasp-amass/amass/v4/...@master"),
    ("assetfinder", "assetfinder", "go install github.com/tomnomnom/assetfinder@latest"),
    
    # Port scanning
    ("nmap", "nmap", "apt install nmap"),
    ("masscan", "masscan", "apt install masscan"),
    ("rustscan", "rustscan", "cargo install rustscan"),
    
    # Web probing
    ("httpx", "httpx", "go install github.com/projectdiscovery/httpx/cmd/httpx@latest"),
    ("whatweb", "whatweb", "apt install whatweb"),
    ("wafw00f", "wafw00f", "apt install wafw00f"),
    
    # Vulnerability scanning
    ("nuclei", "nuclei", "go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"),
    ("nikto", "nikto", "apt install nikto"),
    ("wpscan", "wpscan", "gem install wpscan"),
]


def check_tool(name: str, binary: str) -> bool:
    """Check if a tool is available"""
    return shutil.which(binary) is not None


def main():
    """Main function"""
    print(f"{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║          ReconPilot Tool Availability Checker            ║{RESET}")
    print(f"{BLUE}╚═══════════════════════════════════════════════════════════╝{RESET}\n")
    
    available = []
    missing = []
    
    # Check each tool
    for name, binary, install_cmd in TOOLS:
        is_available = check_tool(name, binary)
        
        if is_available:
            print(f"{GREEN}✓{RESET} {name:<15} {GREEN}[Available]{RESET}")
            available.append(name)
        else:
            print(f"{RED}✗{RESET} {name:<15} {RED}[Missing]{RESET}")
            print(f"  {YELLOW}Install: {install_cmd}{RESET}")
            missing.append(name)
    
    # Print summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{GREEN}Available:{RESET} {len(available)}/{len(TOOLS)}")
    print(f"{RED}Missing:{RESET}   {len(missing)}/{len(TOOLS)}")
    
    if missing:
        print(f"\n{YELLOW}Missing tools:{RESET}")
        for tool in missing:
            print(f"  • {tool}")
        print(f"\n{YELLOW}Run scripts/install-kali.sh to install missing tools{RESET}")
        return 1
    else:
        print(f"\n{GREEN}All tools are available! 🎉{RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
