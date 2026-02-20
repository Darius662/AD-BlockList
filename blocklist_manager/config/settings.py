"""
Configuration settings for Blocklist Manager
"""

import os

# Color scheme (VS Code dark theme inspired)
COLORS = {
    'bg': '#1e1e1e',
    'fg': '#ffffff',
    'accent': '#007acc',
    'accent_hover': '#005a9e',
    'panel': '#252526',
    'input': '#3e3e42',
    'success': '#4ec9b0',
    'warning': '#ce9178',
    'error': '#f48771',
    'info': '#9cdcfe'
}

# Default paths
DEFAULT_PATHS = {
    'temp_dir': r'C:\temp',
    'adguard_home': r'C:\temp\AdGuard-BlockLists\AdGuard-Home',
    'pihole': r'C:\temp\AdGuard-BlockLists\PiHole',
    'adguard_official': r'C:\Users\dariu\Documents\GitHub\AD-BlockList\Adguard Official Lists',
    'adguard_dns': r'C:\Users\dariu\Documents\GitHub\AD-BlockList\AdguardDNS Lists'
}

# GitHub API endpoints
GITHUB_SOURCES = {
    'hostlists_registry': {
        'url': 'https://api.github.com/repos/AdguardTeam/HostlistsRegistry/contents/assets',
        'pattern': r'^filter_\d+\.txt$',
        'destination': DEFAULT_PATHS['adguard_official']
    },
    'adguard_filters': {
        'url': 'https://api.github.com/repos/AdguardTeam/AdguardFilters/contents/BaseFilter/sections',
        'pattern': r'\.txt$',
        'destination': DEFAULT_PATHS['adguard_dns']
    }
}

# File processing settings
PROCESSING = {
    'batch_size': 10000,  # Lines to process before updating progress
    'encoding': 'utf-8',
    'errors': 'ignore'
}

# UI Settings
UI = {
    'window_width': 1100,
    'window_height': 850,
    'min_width': 900,
    'min_height': 700,
    'log_height': 12,
    'font_main': ('Segoe UI', 10),
    'font_mono': ('Consolas', 10),
    'font_title': ('Segoe UI', 22, 'bold'),
    'font_section': ('Segoe UI', 12, 'bold')
}
