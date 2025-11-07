"""
Enhanced Email Sender - User Settings Manager
Handles local storage and cloud sync of user preferences and data
"""

import json
import os
from typing import Dict, Any
from pathlib import Path

class UserSettingsManager:
    """Manage user settings with local storage and cloud sync"""
    
    def __init__(self, cloud_sync=None):
        self.cloud_sync = cloud_sync
        self.settings_dir = Path.home() / ".enhanced_email_sender"
        self.settings_file = self.settings_dir / "settings.json"
        self.templates_file = self.settings_dir / "templates.json"
        self.recipients_file = self.settings_dir / "recipients.json"
        
        # Create settings directory if it doesn't exist
        self.settings_dir.mkdir(exist_ok=True)
        
        # Default settings
        self.default_settings = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "remember_credentials": False,
            "auto_save_drafts": True,
            "theme": "default",
            "window_geometry": "900x600",
            "last_email": "",
            "send_copy_to_self": False,
            "email_signature": ""
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """Load user settings from local storage"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # Merge with defaults for any missing keys
                return {**self.default_settings, **settings}
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save user settings to local storage"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            # Sync to cloud if available
            if self.cloud_sync:
                try:
                    self.cloud_sync.save_settings_to_cloud(settings)
                except Exception as e:
                    print(f"Cloud sync failed: {e}")
            
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_email_templates(self) -> Dict[str, Dict]:
        """Load email templates from local storage"""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "Welcome Email": {
                        "subject": "Welcome to our service!",
                        "body": "Dear {{name}},\n\nWelcome to our service. We're excited to have you on board!\n\nBest regards,\nThe Team"
                    },
                    "Follow Up": {
                        "subject": "Following up on our conversation",
                        "body": "Hi {{name}},\n\nI wanted to follow up on our recent conversation.\n\nLet me know if you have any questions.\n\nBest regards"
                    }
                }
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {}
    
    def save_email_templates(self, templates: Dict[str, Dict]) -> bool:
        """Save email templates to local storage"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving templates: {e}")
            return False
    
    def load_recipient_lists(self) -> Dict[str, list]:
        """Load recipient lists from local storage"""
        try:
            if self.recipients_file.exists():
                with open(self.recipients_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "Default List": [],
                    "Customers": [],
                    "Newsletter": []
                }
        except Exception as e:
            print(f"Error loading recipient lists: {e}")
            return {}
    
    def save_recipient_lists(self, lists: Dict[str, list]) -> bool:
        """Save recipient lists to local storage"""
        try:
            with open(self.recipients_file, 'w', encoding='utf-8') as f:
                json.dump(lists, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving recipient lists: {e}")
            return False
    
    def export_all_data(self, export_path: str) -> bool:
        """Export all user data to a file for backup"""
        try:
            export_data = {
                "settings": self.load_settings(),
                "templates": self.load_email_templates(),
                "recipients": self.load_recipient_lists(),
                "export_date": "2024-11-06T12:00:00"
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def import_all_data(self, import_path: str) -> bool:
        """Import all user data from a backup file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "settings" in import_data:
                self.save_settings(import_data["settings"])
            
            if "templates" in import_data:
                self.save_email_templates(import_data["templates"])
            
            if "recipients" in import_data:
                self.save_recipient_lists(import_data["recipients"])
            
            return True
        except Exception as e:
            print(f"Error importing data: {e}")
            return False
    
    def sync_with_cloud(self) -> bool:
        """Sync local data with cloud storage"""
        if not self.cloud_sync:
            return False
        
        try:
            # Load cloud settings and merge with local
            cloud_settings = self.cloud_sync.load_settings_from_cloud()
            if cloud_settings:
                local_settings = self.load_settings()
                merged_settings = {**local_settings, **cloud_settings}
                self.save_settings(merged_settings)
            
            return True
        except Exception as e:
            print(f"Error syncing with cloud: {e}")
            return False