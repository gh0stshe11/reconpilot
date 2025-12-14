"""Utility helpers for ReconPilot"""
import re
from datetime import datetime, timedelta
from typing import Optional


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    td = timedelta(seconds=int(seconds))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if td.days > 0:
        parts.append(f"{td.days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format timestamp to ISO format"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def is_valid_domain(domain: str) -> bool:
    """Check if string is a valid domain"""
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))


def is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IP address"""
    pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip))


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL"""
    pattern = r"^https?://(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}|(?:\d{1,3}\.){3}\d{1,3})(?::\d+)?(?:/.*)?$"
    return bool(re.match(pattern, url))


def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be used as a filename"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate a string to max length"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix
