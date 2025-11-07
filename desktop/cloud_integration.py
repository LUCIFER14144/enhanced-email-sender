"""
Enhanced Email Sender - Cloud Integration
Desktop application with cloud authentication and data synchronization

This module provides cloud integration capabilities for the desktop email sender.
Users can authenticate with cloud credentials and sync their data.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import requests
import json
import os
from datetime import datetime, timedelta
import threading
import time
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudSync:
    """Handle cloud synchronization and authentication"""
    
    def __init__(self, api_base_url: str = None):
        self.api_base_url = api_base_url or "https://perfected-vercelblasting.vercel.app"
        self.token = None
        self.user_data = None
        self.expiration_check_interval = 300  # Check every 5 minutes
        self.last_sync = None
        
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user with cloud backend"""
        try:
            logger.info(f"Authenticating user: {username}")
            response = requests.post(
                f"{self.api_base_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data["token"]
                    self.user_data = data["user"]
                    self.last_sync = datetime.now()
                    
                    logger.info(f"Authentication successful for user: {username}")
                    return True
            
            logger.warning(f"Authentication failed for user: {username}")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def check_subscription_status(self) -> bool:
        """Check if user subscription is still valid"""
        if not self.token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_base_url}/api/auth/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    days_remaining = data.get("days_remaining", 0)
                    logger.info(f"Subscription check: {days_remaining} days remaining")
                    return days_remaining > 0
            
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Subscription check error: {e}")
            return False
    
    def save_recipients_to_cloud(self, list_name: str, recipients: List[str]) -> bool:
        """Save recipient list to cloud"""
        if not self.token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_base_url}/api/recipients/save",
                json={"list_name": list_name, "recipients": recipients},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Recipients saved to cloud: {list_name}")
                return True
            
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Save recipients error: {e}")
            return False
    
    def load_recipients_from_cloud(self) -> List[Dict]:
        """Load recipient lists from cloud"""
        if not self.token:
            return []
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_base_url}/api/recipients/load",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info(f"Loaded {len(data['lists'])} recipient lists from cloud")
                    return data["lists"]
            
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Load recipients error: {e}")
            return []
    
    def delete_recipients_from_cloud(self, list_id: int) -> bool:
        """Delete recipient list from cloud"""
        if not self.token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(
                f"{self.api_base_url}/api/recipients/delete/{list_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Deleted recipient list {list_id} from cloud")
                return True
            
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Delete recipients error: {e}")
            return False
    
    def save_settings_to_cloud(self, settings: Dict) -> bool:
        """Save user settings to cloud"""
        if not self.token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_base_url}/api/settings/save",
                json=settings,
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Save settings error: {e}")
            return False
    
    def load_settings_from_cloud(self) -> Dict:
        """Load user settings from cloud"""
        if not self.token:
            return {}
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_base_url}/api/settings/load",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("settings", {})
            
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Load settings error: {e}")
            return {}
    
    def update_email_stats(self, sent_count: int) -> bool:
        """Update email sending statistics in cloud"""
        if not self.token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_base_url}/api/stats/update",
                json={"emails_sent": sent_count},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Updated email stats: {sent_count} emails sent")
                return True
            
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Update stats error: {e}")
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """Get current user information including subscription status"""
        if not self.token or not self.user_data:
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_base_url}/api/user/info",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("user")
            
            # Fallback to stored user data
            return self.user_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get user info error: {e}")
            return self.user_data
    
    def validate_subscription(self, email_count: int) -> Optional[Dict]:
        """Validate if user can send specified number of emails"""
        if not self.token or not self.user_data:
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_base_url}/api/validate/subscription",
                json={
                    "email_count": email_count,
                    "username": self.user_data.get("username")
                },
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Validate subscription error: {e}")
            return None
    
    def get_campaign_history(self) -> Optional[List[Dict]]:
        """Get email campaign history for user"""
        if not self.token or not self.user_data:
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_base_url}/api/campaigns/history",
                params={"username": self.user_data.get("username")},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("campaigns", [])
            
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get campaign history error: {e}")
            return []

def create_cloud_login_window() -> Optional[CloudSync]:
    """Create and show cloud login window"""
    root = tk.Tk()
    root.title("Enhanced Email Sender - Cloud Login")
    root.geometry("500x400")
    root.resizable(False, False)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Styling
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass
    
    # Colors
    bg_card = "#FFF6EE"
    bg_window = "#FDF7F0"
    fg_primary = "#3E2F2F"
    accent = "#E07A5F"
    accent_dark = "#C75B43"
    
    root.configure(bg=bg_window)
    
    # Main container
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="📧 Enhanced Email Sender", 
                           font=('Segoe UI', 18, 'bold'))
    title_label.pack(pady=(0, 10))
    
    subtitle_label = ttk.Label(main_frame, text="Cloud Authentication Required", 
                              font=('Segoe UI', 12))
    subtitle_label.pack(pady=(0, 20))
    
    # Login form
    form_frame = ttk.LabelFrame(main_frame, text="Sign In", padding="20")
    form_frame.pack(fill=tk.X, pady=(0, 20))
    
    # API URL input
    ttk.Label(form_frame, text="API URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 10))
    api_url_var = tk.StringVar(value="https://your-vercel-app.vercel.app")
    api_url_entry = ttk.Entry(form_frame, textvariable=api_url_var, width=40)
    api_url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
    
    # Username input
    ttk.Label(form_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 10))
    username_var = tk.StringVar()
    username_entry = ttk.Entry(form_frame, textvariable=username_var, width=40)
    username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
    
    # Password input
    ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 10))
    password_var = tk.StringVar()
    password_entry = ttk.Entry(form_frame, textvariable=password_var, show="*", width=40)
    password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)
    
    # Status label
    status_label = ttk.Label(main_frame, text="", font=('Segoe UI', 10))
    status_label.pack(pady=(0, 10))
    
    # Result storage
    result = {"cloud_sync": None}
    
    def try_login():
        """Attempt to authenticate with cloud"""
        username = username_var.get().strip()
        password = password_var.get()
        api_url = api_url_var.get().strip()
        
        if not username or not password:
            status_label.config(text="❌ Please enter username and password", foreground="red")
            return
        
        if not api_url:
            status_label.config(text="❌ Please enter API URL", foreground="red")
            return
        
        status_label.config(text="🔄 Authenticating...", foreground="blue")
        root.update()
        
        # Create cloud sync instance
        cloud_sync = CloudSync(api_url)
        
        # Try authentication
        if cloud_sync.authenticate(username, password):
            # Check subscription status
            days_remaining = cloud_sync.user_data.get("days_remaining", 0)
            
            if days_remaining <= 0:
                status_label.config(text="❌ Your subscription has expired", foreground="red")
                messagebox.showerror("Subscription Expired", 
                                   "Your subscription has expired. Please contact admin to renew.")
                return
            
            # Show success and warnings
            status_label.config(text="✅ Authentication successful!", foreground="green")
            
            if days_remaining <= 7:
                messagebox.showwarning("Subscription Expiring", 
                                     f"⚠️ Your subscription expires in {days_remaining} days!")
            elif days_remaining <= 30:
                messagebox.showinfo("Subscription Notice", 
                                  f"ℹ️ Your subscription expires in {days_remaining} days.")
            
            result["cloud_sync"] = cloud_sync
            root.after(1000, root.quit)
            
        else:
            status_label.config(text="❌ Authentication failed", foreground="red")
    
    def try_offline_mode():
        """Continue in offline mode"""
        response = messagebox.askyesno("Offline Mode", 
                                     "Continue without cloud features?\n\n"
                                     "• No cloud sync\n"
                                     "• No backup to cloud\n"
                                     "• Local data only")
        if response:
            result["cloud_sync"] = None
            root.quit()
    
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    login_btn = ttk.Button(button_frame, text="🚀 Sign In", command=try_login)
    login_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    offline_btn = ttk.Button(button_frame, text="💻 Offline Mode", command=try_offline_mode)
    offline_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    exit_btn = ttk.Button(button_frame, text="❌ Exit", command=root.quit)
    exit_btn.pack(side=tk.RIGHT)
    
    # Info section
    info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Information", padding="15")
    info_frame.pack(fill=tk.X, pady=(20, 0))
    
    info_text = """
🔒 Secure cloud authentication
☁️ Sync recipients across devices  
📊 Track usage and campaigns
⏰ Subscription management
📧 Email templates and settings
    """.strip()
    
    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
    
    # Bind Enter key
    def on_enter(event):
        try_login()
    
    root.bind("<Return>", on_enter)
    username_entry.focus_set()
    
    # Start the GUI
    root.mainloop()
    root.destroy()
    
    return result["cloud_sync"]

def create_subscription_info_window(cloud_sync: CloudSync):
    """Create subscription information window"""
    if not cloud_sync or not cloud_sync.user_data:
        return
    
    window = tk.Toplevel()
    window.title("Subscription Information")
    window.geometry("400x300")
    window.resizable(False, False)
    
    # Center window
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
    y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
    window.geometry(f"+{x}+{y}")
    
    main_frame = ttk.Frame(window, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    ttk.Label(main_frame, text="💳 Subscription Details", 
             font=('Arial', 14, 'bold')).pack(pady=(0, 15))
    
    user = cloud_sync.user_data
    
    # User info
    info_text = f"""
👤 Username: {user.get('username', 'N/A')}
📧 Email: {user.get('email', 'Not provided')}
🎯 Subscription: {user.get('subscription_type', 'free').title()}
⏰ Expires: {user.get('expires_at', 'N/A')[:10] if user.get('expires_at') else 'N/A'}
📅 Days Remaining: {user.get('days_remaining', 0)}
📊 Emails Sent: {user.get('total_emails_sent', 0)}
    """.strip()
    
    info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT, 
                          font=('Courier New', 10))
    info_label.pack(pady=(0, 15), anchor=tk.W)
    
    # Warning if expiring soon
    days_remaining = user.get('days_remaining', 0)
    if days_remaining <= 30:
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ Notice", padding="10")
        warning_frame.pack(fill=tk.X, pady=(0, 15))
        
        if days_remaining <= 0:
            warning_text = "🚨 Your subscription has EXPIRED!"
            color = 'red'
        elif days_remaining <= 7:
            warning_text = f"🚨 Expires in {days_remaining} days!"
            color = 'red'
        else:
            warning_text = f"⚠️ Expires in {days_remaining} days"
            color = 'orange'
        
        warning_label = ttk.Label(warning_frame, text=warning_text, 
                                 foreground=color, font=('Arial', 10, 'bold'))
        warning_label.pack()
    
    # Close button
    ttk.Button(main_frame, text="Close", command=window.destroy).pack(pady=(10, 0))

if __name__ == "__main__":
    # Test the cloud authentication
    print("Testing cloud authentication...")
    cloud_sync = create_cloud_login_window()
    
    if cloud_sync:
        print(f"Authenticated as: {cloud_sync.user_data['username']}")
        print(f"Days remaining: {cloud_sync.user_data['days_remaining']}")
        
        # Show subscription info
        root = tk.Tk()
        root.withdraw()  # Hide main window
        create_subscription_info_window(cloud_sync)
        root.mainloop()
    else:
        print("Authentication failed or offline mode selected")
