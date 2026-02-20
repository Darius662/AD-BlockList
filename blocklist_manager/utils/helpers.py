"""
Utility helper functions
"""

import os
import re
from datetime import datetime


def ensure_directory(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)
    return path


def count_lines(filepath):
    """Count total lines in a file efficiently"""
    count = 0
    with open(filepath, 'rb') as f:
        for _ in f:
            count += 1
    return count


def format_number(num):
    """Format number with thousand separators"""
    return f"{num:,}"


def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%H:%M:%S")


def is_comment(line):
    """Check if a line is a comment or empty"""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith('!'):
        return True
    if stripped.startswith('#'):
        return True
    if stripped.startswith('//'):
        return True
    if re.match(r'^:.*:$', stripped):
        return True
    return False


def convert_adguard_to_pihole(line):
    """
    Convert AdGuard format to PiHole format
    Returns None if line should be skipped
    """
    stripped = line.strip()
    if not stripped or stripped.startswith('!'):
        return None
    
    domain = stripped
    if domain.startswith('||'):
        domain = domain[2:]
    if domain.endswith('^'):
        domain = domain[:-1]
    if '^$' in domain:
        domain = domain.split('^$')[0]
    
    # Validate domain format
    if re.match(r'^[a-zA-Z0-9]', domain) and '.' in domain:
        return domain
    return None


def convert_pihole_to_adguard(line):
    """
    Convert PiHole format to AdGuard format
    Converts 'domain.com' to '||domain.com^'
    Returns None if line should be skipped
    """
    stripped = line.strip()
    
    # Skip comments and empty lines
    if not stripped:
        return None
    if stripped.startswith('#'):
        return None
    if stripped.startswith('!'):
        return None
    if stripped.startswith('//'):
        return None
    
    # Skip lines with spaces (likely not domains)
    if ' ' in stripped:
        return None
    
    # Skip IP addresses (PiHole hosts file format)
    if re.match(r'^\d+\.\d+\.\d+\.\d+\s+', stripped):
        # Extract domain after IP
        parts = stripped.split()
        if len(parts) >= 2:
            stripped = parts[-1]
        else:
            return None
    
    # Skip if already in AdGuard format
    if stripped.startswith('||') and stripped.endswith('^'):
        return stripped
    
    # Convert to AdGuard format
    # Validate it's a domain-like string
    if re.match(r'^[a-zA-Z0-9]', stripped) and '.' in stripped:
        # Basic domain validation - reject if it has invalid characters
        if re.match(r'^[a-zA-Z0-9\.\-_]+$', stripped):
            return f'||{stripped}^'
    
    return None


def validate_filepath(filepath, must_exist=False):
    """Validate file path, optionally check if file exists"""
    if not filepath:
        return False, "Path is empty"
    if must_exist and not os.path.exists(filepath):
        return False, f"File not found: {filepath}"
    return True, None
