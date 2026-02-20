# AD-BlockList Manager

A high-performance Python GUI application for managing AdGuard and PiHole blocklists. Built with `tkinter` for a modern, responsive interface with multi-threading support.

## Features

- **Remove Duplicates** - Process large blocklists and remove duplicate entries
- **Merge Folder & Deduplicate** - Combine multiple .txt files from a folder into one clean list
- **Split Large Blocklists** - Split files into smaller chunks (e.g., 500K lines for GitHub)
- **Clean Blocklists** - Remove comments and empty lines
- **Convert AdGuard to PiHole** - Transform AdGuard format rules to PiHole-compatible format
- **Download Blocklists** - Fetch lists from 50+ configured repositories
- **Repository Management** - Add, remove, enable/disable blocklist sources via GUI

## Quick Start

```bash
# Run the application
python run_manager.py
```

## Project Structure

```
AD-BlockList/
├── run_manager.py                 # Launcher script
├── blocklist_manager/             # Main package
│   ├── config/
│   │   ├── settings.py           # Colors, paths, UI settings
│   │   └── repos.json            # Blocklist repository configurations
│   ├── core/
│   │   ├── operations.py         # Core processing functions
│   │   └── repo_manager.py       # Repository management class
│   ├── ui/
│   │   └── main_window.py        # GUI implementation
│   ├── utils/
│   │   └── helpers.py            # Utility functions
│   └── main.py                   # Application entry point
└── Powershell/                    # Legacy PowerShell scripts
```

## Configuration

### Repository Sources (`blocklist_manager/config/repos.json`)

Pre-configured sources include:

| Category | Sources |
|----------|---------|
| **AdGuard Official** | Hostlists Registry, Filters, SDNS Filter |
| **AdGuard Regional** | Spanish, French, German, Chinese, Japanese, Turkish, Dutch, Cyrillic |
| **EasyList** | Main list + Germany, Italy, China, Dutch, Hebrew |
| **Regional Lists** | ABPindo, AdblockID, hostsVN, List-KR, ROad-Block |
| **Consolidated** | OISD Big, hBlock Multi |

### Default Paths

Edit `blocklist_manager/config/settings.py` to customize:

- `temp_dir`: `C:\temp`
- `adguard_home`: `C:\temp\AdGuard-BlockLists\AdGuard-Home`
- `pihole`: `C:\temp\AdGuard-BlockLists\PiHole`

## Usage Guide

### 1. Remove Duplicates from Single File
- Select input file (large blocklist)
- Choose output location
- Click **Remove Duplicates**

### 2. Merge Multiple Files from Folder
- Select folder containing .txt files
- Set file pattern (default: `*.txt`)
- Choose output file
- Click **Merge & Remove Duplicates**

### 3. Split Large Blocklist
- Select large input file
- Choose output folder
- Set lines per file (default: 500,000 for GitHub)
- Click **Split Blocklist**
- Output: `filename_part001.txt`, `filename_part002.txt`, etc.

### 4. Clean Blocklist (Remove Comments)
- Select input file with comments
- Choose output location
- Click **Clean Blocklist**

### 5. Convert AdGuard to PiHole Format
- Select AdGuard source folder
- Choose PiHole destination folder
- Click **Convert to PiHole**
- Converts `||domain.com^` to `domain.com`

### 6. Download Blocklists
- Go to **Repository Management** section
- Enable desired repositories (checkmark ✓)
- Click **Download All Blocklists**

### 7. Manage Repositories
- **Enable/Disable** - Toggle repository active status
- **Remove** - Delete repository from configuration
- **Add New Repository** - Add custom blocklist source
- **Refresh List** - Reload repository list from JSON

## Adding Custom Repositories

Click **Add New Repository** and provide:

- **ID** - Unique identifier
- **Name** - Display name
- **Source Type**:
  - `github_api` - Fetch multiple files from GitHub API
  - `github_raw` - Single raw file from GitHub
  - `direct_url` - Any direct download URL
- **URL** - API endpoint or direct file URL
- **File Pattern** - Regex for filtering (GitHub API only)
- **Filename** - Target filename (direct/raw sources)
- **Destination Folder** - Where to save

## Requirements

- Python 3.7+
- No external dependencies (uses only built-in modules)
- Windows (developed and tested on Windows)

## Performance

- Multi-threaded operations for responsive UI
- Memory-efficient streaming for large files
- Progress bars and activity logging
- Batch processing with configurable batch sizes

## License

Personal project for managing AdGuard/PiHole blocklists.
