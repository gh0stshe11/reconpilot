#!/bin/bash
#
# ReconPilot Installation Script for Kali Linux
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗         ║"
echo "║     ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║         ║"
echo "║     ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║         ║"
echo "║     ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║         ║"
echo "║     ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║         ║"
echo "║     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝         ║"
echo "║                                                           ║"
echo "║              PILOT - Installation Script                 ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${GREEN}[+] Installing system packages...${NC}"
apt-get update -qq
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    nmap \
    masscan \
    whois \
    dnsutils \
    nikto \
    whatweb \
    wafw00f \
    golang-go \
    git \
    curl

# Set up Go environment
echo -e "${GREEN}[+] Setting up Go environment...${NC}"
export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Add to bashrc if not already there
if ! grep -q "export GOPATH=" ~/.bashrc; then
    echo "export GOPATH=\$HOME/go" >> ~/.bashrc
    echo "export PATH=\$PATH:/usr/local/go/bin:\$GOPATH/bin" >> ~/.bashrc
fi

# Install Go-based tools
echo -e "${GREEN}[+] Installing Go-based reconnaissance tools...${NC}"

# Subfinder
if ! command -v subfinder &> /dev/null; then
    echo -e "${YELLOW}  Installing subfinder...${NC}"
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
fi

# HTTPX
if ! command -v httpx &> /dev/null; then
    echo -e "${YELLOW}  Installing httpx...${NC}"
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
fi

# Nuclei
if ! command -v nuclei &> /dev/null; then
    echo -e "${YELLOW}  Installing nuclei...${NC}"
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
fi

# DNSX
if ! command -v dnsx &> /dev/null; then
    echo -e "${YELLOW}  Installing dnsx...${NC}"
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
fi

# Assetfinder
if ! command -v assetfinder &> /dev/null; then
    echo -e "${YELLOW}  Installing assetfinder...${NC}"
    go install github.com/tomnomnom/assetfinder@latest
fi

# Amass (optional - takes longer)
if ! command -v amass &> /dev/null; then
    echo -e "${YELLOW}  Installing amass...${NC}"
    go install -v github.com/owasp-amass/amass/v4/...@master || echo "Amass installation failed, continuing..."
fi

# RustScan (optional - requires cargo)
if command -v cargo &> /dev/null; then
    if ! command -v rustscan &> /dev/null; then
        echo -e "${YELLOW}  Installing rustscan...${NC}"
        cargo install rustscan || echo "RustScan installation failed, continuing..."
    fi
fi

# Install WPScan (Ruby gem)
if command -v gem &> /dev/null; then
    if ! command -v wpscan &> /dev/null; then
        echo -e "${YELLOW}  Installing wpscan...${NC}"
        gem install wpscan || echo "WPScan installation failed, continuing..."
    fi
fi

# Install ReconPilot
echo -e "${GREEN}[+] Installing ReconPilot...${NC}"
pip3 install -e .

# Verify installation
echo -e "${GREEN}[+] Verifying installation...${NC}"
if command -v reconpilot &> /dev/null; then
    echo -e "${GREEN}✓ ReconPilot installed successfully!${NC}"
    reconpilot --version
else
    echo -e "${RED}✗ ReconPilot installation failed${NC}"
    exit 1
fi

# Check tool availability
echo -e "${GREEN}[+] Checking tool availability...${NC}"
reconpilot tools check

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║                Installation Complete!                     ║"
echo "║                                                           ║"
echo "║  Run 'reconpilot --help' to get started                  ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
