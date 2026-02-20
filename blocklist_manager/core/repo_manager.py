"""
Repository configuration manager
Handles loading, saving, and managing blocklist repository configurations
"""

import json
import os
from datetime import datetime


class RepoManager:
    """Manages repository configurations from JSON file"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            # Default to config directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, '..', 'config', 'repos.json')
        
        self.config_path = os.path.abspath(config_path)
        self.data = {"repositories": [], "settings": {}}
        self.load()
    
    def load(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                # Create default config if not exists
                self.data = {
                    "repositories": [],
                    "settings": {
                        "default_destination": "C:\\Users\\dariu\\Documents\\GitHub\\AD-BlockList",
                        "auto_enable_new": True,
                        "verify_downloads": False,
                        "max_concurrent_downloads": 5
                    }
                }
                self.save()
        except Exception as e:
            print(f"Error loading repos config: {e}")
            self.data = {"repositories": [], "settings": {}}
    
    def save(self):
        """Save configuration to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving repos config: {e}")
            return False
    
    def get_all_repos(self):
        """Get all repositories"""
        return self.data.get("repositories", [])
    
    def get_enabled_repos(self):
        """Get only enabled repositories"""
        return [r for r in self.get_all_repos() if r.get("enabled", False)]
    
    def get_repo(self, repo_id):
        """Get a specific repository by ID"""
        for repo in self.get_all_repos():
            if repo.get("id") == repo_id:
                return repo
        return None
    
    def add_repo(self, repo_data):
        """
        Add a new repository
        
        Args:
            repo_data: Dictionary with repo configuration
                Required: id, name, source
                Optional: enabled, description, etc.
        
        Returns:
            tuple: (success, message)
        """
        # Validate required fields
        if not repo_data.get("id"):
            return False, "Repository ID is required"
        if not repo_data.get("name"):
            return False, "Repository name is required"
        if not repo_data.get("source"):
            return False, "Source type is required"
        
        # Check for duplicate ID
        if self.get_repo(repo_data["id"]):
            return False, f"Repository with ID '{repo_data['id']}' already exists"
        
        # Set defaults
        repo_data.setdefault("enabled", self.data.get("settings", {}).get("auto_enable_new", True))
        repo_data.setdefault("description", "")
        repo_data.setdefault("destination_folder", "Custom Lists")
        
        # Add to list
        self.data["repositories"].append(repo_data)
        
        if self.save():
            return True, f"Repository '{repo_data['name']}' added successfully"
        else:
            return False, "Failed to save repository"
    
    def update_repo(self, repo_id, updates):
        """
        Update an existing repository
        
        Args:
            repo_id: Repository ID to update
            updates: Dictionary of fields to update
        
        Returns:
            tuple: (success, message)
        """
        repo = self.get_repo(repo_id)
        if not repo:
            return False, f"Repository '{repo_id}' not found"
        
        # Update fields
        for key, value in updates.items():
            if key != "id":  # Don't allow ID changes
                repo[key] = value
        
        if self.save():
            return True, f"Repository '{repo_id}' updated successfully"
        else:
            return False, "Failed to save changes"
    
    def remove_repo(self, repo_id):
        """
        Remove a repository
        
        Args:
            repo_id: Repository ID to remove
        
        Returns:
            tuple: (success, message)
        """
        original_count = len(self.data["repositories"])
        self.data["repositories"] = [
            r for r in self.data["repositories"] 
            if r.get("id") != repo_id
        ]
        
        if len(self.data["repositories"]) == original_count:
            return False, f"Repository '{repo_id}' not found"
        
        if self.save():
            return True, f"Repository '{repo_id}' removed successfully"
        else:
            return False, "Failed to save changes"
    
    def toggle_repo(self, repo_id):
        """
        Toggle enabled/disabled status of a repository
        
        Args:
            repo_id: Repository ID to toggle
        
        Returns:
            tuple: (success, new_status, message)
        """
        repo = self.get_repo(repo_id)
        if not repo:
            return False, None, f"Repository '{repo_id}' not found"
        
        new_status = not repo.get("enabled", False)
        repo["enabled"] = new_status
        
        if self.save():
            status_str = "enabled" if new_status else "disabled"
            return True, new_status, f"Repository '{repo_id}' {status_str}"
        else:
            return False, None, "Failed to save changes"
    
    def get_settings(self):
        """Get global settings"""
        return self.data.get("settings", {})
    
    def update_settings(self, settings):
        """Update global settings"""
        self.data["settings"].update(settings)
        return self.save()
    
    def get_destination_path(self, repo):
        """Get full destination path for a repository"""
        base_path = self.data.get("settings", {}).get(
            "default_destination", 
            "C:\\Users\\dariu\\Documents\\GitHub\\AD-BlockList"
        )
        folder = repo.get("destination_folder", "Custom Lists")
        return os.path.join(base_path, folder)
