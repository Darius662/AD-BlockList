"""
Core blocklist operations
All functions support progress callbacks for UI updates
"""

import os
import json
import urllib.request
import urllib.error
from config.settings import PROCESSING, GITHUB_SOURCES
from utils.helpers import ensure_directory, is_comment, convert_adguard_to_pihole, convert_pihole_to_adguard


def remove_duplicates(input_file, output_file, progress_callback=None, log_callback=None):
    """
    Remove duplicate lines from blocklist file
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        progress_callback: Function(percent, status_message) to call for progress updates
        log_callback: Function(message) to call for log updates
    
    Returns:
        tuple: (total_lines, unique_lines, success)
    """
    try:
        seen = set()
        total_lines = 0
        unique_lines = 0
        batch_size = PROCESSING['batch_size']
        
        # Count total lines first
        with open(input_file, 'rb') as f:
            for _ in f:
                total_lines += 1
        
        if log_callback:
            log_callback(f"Total lines to process: {total_lines:,}")
        
        # Process file
        with open(input_file, 'r', encoding=PROCESSING['encoding'], 
                  errors=PROCESSING['errors']) as infile:
            with open(output_file, 'w', encoding=PROCESSING['encoding']) as outfile:
                processed = 0
                for line in infile:
                    processed += 1
                    stripped = line.strip()
                    
                    if not stripped:
                        continue
                    
                    if stripped not in seen:
                        seen.add(stripped)
                        outfile.write(stripped + '\n')
                        unique_lines += 1
                    
                    # Update progress
                    if processed % batch_size == 0:
                        percent = (processed / total_lines) * 100
                        if progress_callback:
                            progress_callback(percent, f"Processed {processed:,} lines...")
                
                # Final progress update
                if progress_callback:
                    progress_callback(100, "Complete")
        
        return total_lines, unique_lines, True
        
    except Exception as e:
        if log_callback:
            log_callback(f"Error: {str(e)}")
        return 0, 0, False


def clean_blocklist(input_file, output_file, progress_callback=None, log_callback=None):
    """
    Remove comments and empty lines from blocklist
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        progress_callback: Function(percent, status_message) for progress
        log_callback: Function(message) for log updates
    
    Returns:
        tuple: (total_lines, kept_lines, success)
    """
    try:
        total_lines = 0
        kept_lines = 0
        batch_size = PROCESSING['batch_size']
        
        # Count total lines
        with open(input_file, 'rb') as f:
            for _ in f:
                total_lines += 1
        
        with open(input_file, 'r', encoding=PROCESSING['encoding'],
                  errors=PROCESSING['errors']) as infile:
            with open(output_file, 'w', encoding=PROCESSING['encoding']) as outfile:
                processed = 0
                for line in infile:
                    processed += 1
                    
                    if not is_comment(line):
                        outfile.write(line.strip() + '\n')
                        kept_lines += 1
                    
                    # Update progress
                    if processed % batch_size == 0:
                        percent = (processed / total_lines) * 100
                        if progress_callback:
                            progress_callback(percent, f"Processed {processed:,} lines...")
                
                if progress_callback:
                    progress_callback(100, "Complete")
        
        return total_lines, kept_lines, True
        
    except Exception as e:
        if log_callback:
            log_callback(f"Error: {str(e)}")
        return 0, 0, False


def convert_to_pihole(source_dir, target_dir, progress_callback=None, log_callback=None):
    """
    Convert AdGuard format files to PiHole format
    
    Args:
        source_dir: Source directory with AdGuard files
        target_dir: Target directory for PiHole files
        progress_callback: Function(percent, status_message) for progress
        log_callback: Function(filename) for file processing updates
    
    Returns:
        tuple: (processed_files, success)
    """
    try:
        ensure_directory(target_dir)
        
        main_files = [
            'BlockList.txt', 'BlockList_clean.txt', 
            'BlockList_unique.txt', 'Romanian_Complete_Blocklist.txt'
        ]
        
        total_files = len(main_files)
        processed_files = 0
        
        for filename in main_files:
            source_path = os.path.join(source_dir, filename)
            if os.path.exists(source_path):
                if log_callback:
                    log_callback(filename)
                
                target_path = os.path.join(target_dir, filename)
                
                with open(source_path, 'r', encoding=PROCESSING['encoding'],
                          errors=PROCESSING['errors']) as infile:
                    with open(target_path, 'w', encoding=PROCESSING['encoding']) as outfile:
                        for line in infile:
                            domain = convert_adguard_to_pihole(line)
                            if domain:
                                outfile.write(domain + '\n')
                
                processed_files += 1
                if progress_callback:
                    percent = (processed_files / total_files) * 100
                    progress_callback(percent, f"Converted {processed_files}/{total_files} files")
        
        if progress_callback:
            progress_callback(100, "Complete")
        
        return processed_files, True
        
    except Exception as e:
        if log_callback:
            log_callback(f"Error: {str(e)}")
        return 0, False


def convert_to_adguard(source_dir, target_dir, progress_callback=None, log_callback=None):
    """
    Convert PiHole format files to AdGuard format
    
    Args:
        source_dir: Source directory with PiHole files
        target_dir: Target directory for AdGuard files
        progress_callback: Function(percent, status_message) for progress
        log_callback: Function(filename) for file processing updates
    
    Returns:
        tuple: (processed_files, success)
    """
    try:
        ensure_directory(target_dir)
        
        main_files = [
            'BlockList.txt', 'BlockList_clean.txt', 
            'BlockList_unique.txt', 'Romanian_Complete_Blocklist.txt'
        ]
        
        total_files = len(main_files)
        processed_files = 0
        
        for filename in main_files:
            source_path = os.path.join(source_dir, filename)
            if os.path.exists(source_path):
                if log_callback:
                    log_callback(filename)
                
                target_path = os.path.join(target_dir, filename)
                
                with open(source_path, 'r', encoding=PROCESSING['encoding'],
                          errors=PROCESSING['errors']) as infile:
                    with open(target_path, 'w', encoding=PROCESSING['encoding']) as outfile:
                        for line in infile:
                            domain = convert_pihole_to_adguard(line)
                            if domain:
                                outfile.write(domain + '\n')
                
                processed_files += 1
                if progress_callback:
                    percent = (processed_files / total_files) * 100
                    progress_callback(percent, f"Converted {processed_files}/{total_files} files")
        
        if progress_callback:
            progress_callback(100, "Complete")
        
        return processed_files, True
        
    except Exception as e:
        if log_callback:
            log_callback(f"Error: {str(e)}")
        return 0, False


def download_blocklists(repo_manager, progress_callback=None, log_callback=None):
    """
    Download blocklists from configured repositories
    
    Args:
        repo_manager: RepoManager instance with repository configurations
        progress_callback: Function(percent, status_message) for progress
        log_callback: Function(message, file_name) for download updates
    
    Returns:
        tuple: (downloaded_count, success)
    """
    headers = {'User-Agent': 'Python/BlocklistManager'}
    downloaded = 0
    total_files_estimate = 0
    
    try:
        # Get enabled repositories
        repos = repo_manager.get_enabled_repos()
        
        if not repos:
            if log_callback:
                log_callback("No repositories enabled! Please enable at least one repository.", None)
            return 0, False
        
        # Estimate total files for progress calculation
        for repo in repos:
            if repo.get("source") == "github_api":
                total_files_estimate += 50  # Estimate for API sources
            else:
                total_files_estimate += 1  # Single file sources
        
        # Process each enabled repository
        for repo in repos:
            repo_name = repo.get("name", repo.get("id", "Unknown"))
            source_type = repo.get("source")
            
            if log_callback:
                log_callback(f"Processing {repo_name}...", None)
            
            # Get destination path
            dest_folder = repo_manager.get_destination_path(repo)
            ensure_directory(dest_folder)
            
            if source_type == "github_api":
                # GitHub API source - fetch file list and download
                api_url = repo.get("api_url")
                file_pattern = repo.get("file_pattern", ".*")
                
                try:
                    req = urllib.request.Request(api_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=30) as response:
                        data = json.loads(response.read().decode('utf-8'))
                    
                    import re
                    files = [f for f in data if re.match(file_pattern, f['name'])]
                    
                    if log_callback:
                        log_callback(f"Found {len(files)} files", None)
                    
                    for file_info in files:
                        if log_callback:
                            log_callback(f"Downloading {file_info['name']}...", file_info['name'])
                        
                        output_path = os.path.join(dest_folder, file_info['name'])
                        req_file = urllib.request.Request(file_info['download_url'], headers=headers)
                        
                        with urllib.request.urlopen(req_file, timeout=30) as file_response:
                            with open(output_path, 'wb') as f:
                                f.write(file_response.read())
                        
                        downloaded += 1
                        
                        if progress_callback:
                            percent = min((downloaded / total_files_estimate) * 100, 99)
                            progress_callback(percent, f"Downloaded {file_info['name']}")
                            
                except Exception as e:
                    if log_callback:
                        log_callback(f"Error with {repo_name}: {str(e)}", None)
                    continue
                    
            elif source_type in ("github_raw", "direct_url"):
                # Direct URL source - download single file
                url = repo.get("url")
                filename = repo.get("filename")
                
                if not url or not filename:
                    if log_callback:
                        log_callback(f"Missing URL or filename for {repo_name}", None)
                    continue
                
                try:
                    if log_callback:
                        log_callback(f"Downloading {filename}...", filename)
                    
                    output_path = os.path.join(dest_folder, filename)
                    req = urllib.request.Request(url, headers=headers)
                    
                    with urllib.request.urlopen(req, timeout=30) as response:
                        with open(output_path, 'wb') as f:
                            f.write(response.read())
                    
                    downloaded += 1
                    
                    if progress_callback:
                        percent = min((downloaded / total_files_estimate) * 100, 99)
                        progress_callback(percent, f"Downloaded {filename}")
                        
                except Exception as e:
                    if log_callback:
                        log_callback(f"Error downloading {filename}: {str(e)}", None)
                    continue
        
        if progress_callback:
            progress_callback(100, "Complete")
        
        return downloaded, True
        
    except Exception as e:
        if log_callback:
            log_callback(f"Error: {str(e)}", None)
        return downloaded, False


def merge_folder_dedupe(source_folder, output_file, file_pattern="*.txt",
                        progress_callback=None, log_callback=None):
    """
    Merge all blocklist files from a folder and remove duplicates
    
    Args:
        source_folder: Folder containing blocklist files
        output_file: Path to output merged/deduplicated file
        file_pattern: Glob pattern to match files (default: "*.txt")
        progress_callback: Function(percent, status_message) for progress
        log_callback: Function(message) for log updates
    
    Returns:
        tuple: (files_processed, total_lines, unique_lines, success)
    """
    try:
        import glob
        
        # Find all matching files
        search_pattern = os.path.join(source_folder, file_pattern)
        files = glob.glob(search_pattern)
        
        # Also check subdirectories
        subdir_pattern = os.path.join(source_folder, "**", file_pattern)
        files.extend(glob.glob(subdir_pattern, recursive=True))
        
        # Remove duplicates while preserving order
        files = list(dict.fromkeys(files))
        
        # Filter out directories and non-files
        files = [f for f in files if os.path.isfile(f)]
        
        if not files:
            if log_callback:
                log_callback(f"No files matching '{file_pattern}' found in {source_folder}")
            return 0, 0, 0, False
        
        if log_callback:
            log_callback(f"Found {len(files)} files to process")
            for f in files:
                log_callback(f"  - {os.path.basename(f)}")
        
        # First pass: count total lines across all files
        total_lines_all = 0
        file_line_counts = {}
        
        for filepath in files:
            try:
                count = 0
                with open(filepath, 'rb') as f:
                    for _ in f:
                        count += 1
                file_line_counts[filepath] = count
                total_lines_all += count
            except Exception as e:
                if log_callback:
                    log_callback(f"Warning: Could not count lines in {os.path.basename(filepath)}: {e}")
                file_line_counts[filepath] = 0
        
        if log_callback:
            log_callback(f"Total lines to process: {total_lines_all:,}")
        
        # Second pass: process all files and deduplicate
        seen = set()
        unique_lines = 0
        files_processed = 0
        total_processed = 0
        
        with open(output_file, 'w', encoding=PROCESSING['encoding']) as outfile:
            for filepath in files:
                files_processed += 1
                filename = os.path.basename(filepath)
                file_lines = file_line_counts.get(filepath, 0)
                
                if log_callback:
                    log_callback(f"Processing {filename} ({file_lines:,} lines)...")
                
                try:
                    with open(filepath, 'r', encoding=PROCESSING['encoding'],
                             errors=PROCESSING['errors']) as infile:
                        for line in infile:
                            total_processed += 1
                            stripped = line.strip()
                            
                            if not stripped:
                                continue
                            
                            if stripped not in seen:
                                seen.add(stripped)
                                outfile.write(stripped + '\n')
                                unique_lines += 1
                            
                            # Update progress periodically
                            if total_processed % PROCESSING['batch_size'] == 0:
                                if progress_callback and total_lines_all > 0:
                                    percent = (total_processed / total_lines_all) * 100
                                    progress_callback(percent, 
                                        f"Processed {total_processed:,}/{total_lines_all:,} lines...")
                                
                except Exception as e:
                    if log_callback:
                        log_callback(f"Error reading {filename}: {e}")
                    continue
        
        if progress_callback:
            progress_callback(100, "Complete")
        
        return files_processed, total_lines_all, unique_lines, True
        
    except Exception as e:
        if log_callback:
            log_callback(f"Error: {str(e)}")
        return 0, 0, 0, False


def split_blocklist(input_file, output_folder, lines_per_file=500000,
                    progress_callback=None, log_callback=None):
    """
    Split a large blocklist into smaller files
    
    Args:
        input_file: Path to large input file
        output_folder: Folder to save split files
        lines_per_file: Maximum lines per output file (default: 500000)
        progress_callback: Function(percent, status_message) for progress
        log_callback: Function(message) for log updates
    
    Returns:
        tuple: (files_created, total_lines, success)
    """
    try:
        # Ensure output folder exists
        ensure_directory(output_folder)
        
        # Count total lines
        if log_callback:
            log_callback("Counting lines...")
        
        total_lines = 0
        with open(input_file, 'rb') as f:
            for _ in f:
                total_lines += 1
        
        if log_callback:
            log_callback(f"Total lines: {total_lines:,}")
            log_callback(f"Splitting into files of ~{lines_per_file:,} lines each...")
        
        # Calculate number of files needed
        files_needed = (total_lines + lines_per_file - 1) // lines_per_file
        
        if log_callback:
            log_callback(f"Will create {files_needed} files")
        
        # Get base filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # Split the file
        current_file = 1
        current_line_count = 0
        output_file = None
        files_created = 0
        lines_processed = 0
        
        with open(input_file, 'r', encoding=PROCESSING['encoding'],
                  errors=PROCESSING['errors']) as infile:
            
            for line in infile:
                lines_processed += 1
                
                # Start new file if needed
                if output_file is None or current_line_count >= lines_per_file:
                    if output_file:
                        output_file.close()
                        files_created += 1
                        if log_callback:
                            log_callback(f"Created part {current_file-1}")
                    
                    # Create new output file
                    output_filename = f"{base_name}_part{current_file:03d}.txt"
                    output_path = os.path.join(output_folder, output_filename)
                    output_file = open(output_path, 'w', encoding=PROCESSING['encoding'])
                    
                    # Add header
                    output_file.write(f"# {base_name} - Part {current_file} of {files_needed}\n")
                    output_file.write(f"# Generated from: {os.path.basename(input_file)}\n")
                    output_file.write(f"# Lines: {min(lines_per_file, total_lines - lines_processed + 1):,}\n\n")
                    
                    current_file += 1
                    current_line_count = 0
                
                # Write line
                output_file.write(line)
                current_line_count += 1
                
                # Update progress
                if lines_processed % PROCESSING['batch_size'] == 0:
                    if progress_callback and total_lines > 0:
                        percent = (lines_processed / total_lines) * 100
                        progress_callback(percent, 
                            f"Processing... {lines_processed:,}/{total_lines:,} lines")
        
        # Close last file
        if output_file:
            output_file.close()
            files_created += 1
            if log_callback:
                log_callback(f"Created part {current_file-1}")
        
        if progress_callback:
            progress_callback(100, "Complete")
        
        return files_created, total_lines, True
        
    except Exception as e:
        if log_callback:
            log_callback(f"Error: {str(e)}")
        return 0, 0, False
