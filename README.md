# 🎯 ReconPilot

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/gh0stshe11/reconpilot/workflows/CI/badge.svg)](https://github.com/gh0stshe11/reconpilot/actions)

**AI-Powered Reconnaissance Orchestrator for Penetration Testing**

ReconPilot is an intelligent reconnaissance automation framework that chains together security tools based on discoveries, prioritizes targets, and provides real-time feedback through an interactive TUI dashboard.

## ✨ Features

- 🤖 **Intelligent Orchestration** - Automatically chains tools based on discoveries
- 🎯 **Smart Prioritization** - Scores assets and findings based on risk
- 📊 **Real-time TUI Dashboard** - Beautiful terminal UI with live updates
- 🔄 **Async Execution** - Parallel task execution for speed
- 💾 **Session Management** - Save, load, and resume scans
- 📝 **Professional Reports** - HTML, Markdown, and JSON output formats
- 🛠️ **Extensible** - Easy to add custom tools and rules
- 🔍 **15+ Tools Supported** - DNS, subdomain, port scanning, web, and vulnerability tools

## 🚀 Quick Start

### Installation

#### Kali Linux (Recommended)

```bash
git clone https://github.com/gh0stshe11/reconpilot.git
cd reconpilot
chmod +x scripts/install-kali.sh
sudo ./scripts/install-kali.sh
```

#### Other Linux Distributions

```bash
# Install Python dependencies
pip install -e .

# Install reconnaissance tools manually
# See scripts/check-tools.py for the full list
```

### Basic Usage

```bash
# Start a scan with TUI dashboard
reconpilot scan example.com

# Scan without dashboard (CLI only)
reconpilot scan example.com --no-dashboard

# Passive reconnaissance only
reconpilot scan example.com --passive-only

# Stealth mode with limited parallelism
reconpilot scan example.com --stealth --max-parallel 1
```

## 📖 Usage Guide

### Scanning

```bash
# Auto mode (default) - intelligently chains tools
reconpilot scan example.com --mode auto

# Interactive mode - prompts before running tools
reconpilot scan example.com --mode interactive

# Passive mode - only passive reconnaissance
reconpilot scan example.com --mode passive

# With scope restrictions
reconpilot scan example.com --scope "*.example.com" --exclude "dev.example.com"

# Custom timeout and parallelism
reconpilot scan example.com --timeout 600 --max-parallel 5
```

### Session Management

```bash
# List all scan sessions
reconpilot sessions list

# Show session details
reconpilot sessions show <session-id>

# Delete a session
reconpilot sessions delete <session-id>
```

### Report Generation

```bash
# Generate HTML report (default)
reconpilot report <session-id>

# Generate Markdown report
reconpilot report <session-id> --format md

# Generate JSON report
reconpilot report <session-id> --format json

# Custom output path
reconpilot report <session-id> --output /path/to/report.html
```

### Tool Management

```bash
# List all supported tools
reconpilot tools list

# Check which tools are installed
reconpilot tools check
```

### Configuration

```bash
# Show current configuration
reconpilot config show

# Edit configuration file
reconpilot config edit

# Reset to defaults
reconpilot config reset
```

## 🛠️ Supported Tools

### DNS & OSINT
- **whois** - Domain registration information
- **dnsrecon** - DNS enumeration
- **dnsx** - Fast DNS resolution

### Subdomain Enumeration
- **subfinder** - Passive subdomain discovery
- **amass** - Advanced subdomain enumeration
- **assetfinder** - Find related domains and subdomains

### Port Scanning
- **nmap** - Network port scanner with service detection
- **masscan** - Fast port scanner
- **rustscan** - Ultra-fast port scanner

### Web Reconnaissance
- **httpx** - HTTP probe with technology detection
- **whatweb** - Web technology identifier
- **wafw00f** - WAF detection

### Vulnerability Scanning
- **nuclei** - Template-based vulnerability scanner
- **nikto** - Web server scanner
- **wpscan** - WordPress vulnerability scanner

## 📁 Project Structure

```
reconpilot/
├── reconpilot/
│   ├── core/           # Core orchestration logic
│   ├── tools/          # Tool adapters
│   ├── dashboard/      # TUI dashboard
│   ├── reports/        # Report generation
│   ├── utils/          # Utilities
│   ├── cli.py          # CLI interface
│   └── config.py       # Configuration management
├── tests/              # Test suite
├── scripts/            # Installation and utility scripts
└── .github/            # CI/CD workflows
```

## 🎨 Dashboard Controls

When running with the TUI dashboard:

- **P** - Pause the scan
- **R** - Resume the scan
- **S** - Skip current task
- **Q** - Quit (saves session)

## 🔧 Configuration

ReconPilot stores configuration in `~/.reconpilot/config.yaml`:

```yaml
general:
  max_parallel_tasks: 3
  stealth_mode: false
  passive_only: false

scope:
  include: []
  exclude: []
  in_scope_only: true

reporting:
  format: html
  auto_save: true
  output_dir: ./reports

notifications:
  enabled: false
  webhook_url: null
  email: null
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

ReconPilot is designed for legal security testing and research purposes only. Users are responsible for complying with applicable laws and regulations. The authors assume no liability for misuse of this tool.

## 🙏 Acknowledgments

- All the amazing open-source reconnaissance tools this project integrates with
- The security research community
- Project Discovery for their excellent Go-based tools

## 📬 Contact

- GitHub: [@gh0stshe11](https://github.com/gh0stshe11)
- Issues: [GitHub Issues](https://github.com/gh0stshe11/reconpilot/issues)

---

**Made with ❤️ by gh0stshe11**
