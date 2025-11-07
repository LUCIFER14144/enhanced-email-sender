"""
Enhanced Email Sender - Desktop Application
Main entry point with cloud integration and subscription management

This is the main desktop application that integrates with the cloud backend
for user authentication, data synchronization, and subscription management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
import sys
import os
from datetime import datetime
import logging
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloud_integration import CloudSync, create_cloud_login_window, create_subscription_info_window

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedEmailSenderApp:
    """Main application class with cloud integration"""
    
    def __init__(self, root):
        self.root = root
        self.cloud_sync = None
        self.user_data = None
        self.setup_window()
        
        # Start with cloud login
        self.show_cloud_login()
        
    def show_cloud_login(self):
        """Show cloud login dialog first"""
        self.root.withdraw()  # Hide main window initially
        
        # Create login window
        login_window = tk.Toplevel()
        login_window.title("🔐 Enhanced Email Sender - Cloud Login")
        login_window.geometry("400x500")
        login_window.resizable(False, False)
        
        # Center login window
        login_window.update_idletasks()
        x = (login_window.winfo_screenwidth() // 2) - (login_window.winfo_width() // 2)
        y = (login_window.winfo_screenheight() // 2) - (login_window.winfo_height() // 2)
        login_window.geometry(f"+{x}+{y}")
        
        # Make it modal
        login_window.transient(self.root)
        login_window.grab_set()
        
        # Login form
        main_frame = ttk.Frame(login_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="☁️ Cloud Authentication", 
                               font=("Arial", 16, "bold"))
        header_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, 
                                 text="Connect to your cloud account to access\nyour email data from anywhere", 
                                 font=("Arial", 10))
        subtitle_label.pack(pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=50)
        username_entry.pack(fill=tk.X, pady=(0, 15))
        username_entry.focus()
        
        # Password
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=50)
        password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Login button
        login_btn = ttk.Button(buttons_frame, text="🔐 Login", 
                              command=lambda: self.handle_login(login_window))
        login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Register button
        register_btn = ttk.Button(buttons_frame, text="📝 Register", 
                                 command=lambda: self.handle_register(login_window))
        register_btn.pack(side=tk.LEFT)
        
        # Demo accounts info
        demo_frame = ttk.LabelFrame(main_frame, text="Demo Accounts", padding="10")
        demo_frame.pack(fill=tk.X, pady=(20, 0))
        
        demo_text = """Try these demo accounts:
• Username: demo | Password: demo123
• Username: testuser | Password: testpass123
        
Or register a new account above."""
        
        ttk.Label(demo_frame, text=demo_text, font=("Arial", 9)).pack()
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to connect...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 9), foreground="blue")
        status_label.pack(pady=(15, 0))
        
        # Handle Enter key
        password_entry.bind('<Return>', lambda e: self.handle_login(login_window))
        
        # Handle window close
        login_window.protocol("WM_DELETE_WINDOW", self.on_login_close)
        
    def handle_login(self, login_window):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        api_url = "https://perfected-vercelblasting.vercel.app"
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        self.status_var.set("Connecting to cloud...")
        login_window.update()
        
        # Initialize cloud sync
        try:
            self.cloud_sync = CloudSync(api_url)
            
            # Test connection first
            if not self.cloud_sync.test_connection():
                self.status_var.set("❌ Cannot connect to server")
                messagebox.showerror("Connection Error", 
                                   f"Cannot connect to server.\n\nPlease check your internet connection.")
                return
            
            # Attempt login
            result = self.cloud_sync.login(username, password)
            
            if result["success"]:
                self.user_data = result
                self.status_var.set("✅ Login successful!")
                login_window.update()
                
                # Close login window and show main app directly
                login_window.destroy()
                self.root.deiconify()  # Show main window
                self.create_widgets()  # Create main interface
                self.load_user_data()  # Load user's cloud data
                
            else:
                self.status_var.set("❌ Login failed")
                messagebox.showerror("Login Failed", result.get("message", "Invalid credentials"))
                
        except Exception as e:
            self.status_var.set("❌ Connection error")
            messagebox.showerror("Error", f"Connection failed:\n{str(e)}")
            
    def handle_register(self, login_window):
        """Handle registration"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        api_url = "https://perfected-vercelblasting.vercel.app"
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        # Simple email prompt
        email = tk.simpledialog.askstring("Email", "Enter your email address (optional):", 
                                         parent=login_window)
        
        self.status_var.set("Creating account...")
        login_window.update()
        
        try:
            if not self.cloud_sync:
                self.cloud_sync = CloudSync(api_url)
            
            result = self.cloud_sync.register_user(username, password, email or "", "free")
            
            if result.get("success"):
                self.status_var.set("✅ Registration successful!")
                messagebox.showinfo("Success", 
                                  f"Account created successfully!\n\nUsername: {username}\nSubscription: Free (30 days)\n\nYou can now login.")
                # Clear password for security
                self.password_var.set("")
                
            else:
                self.status_var.set("❌ Registration failed")
                messagebox.showerror("Registration Failed", result.get("message", "Registration failed"))
                
        except Exception as e:
            self.status_var.set("❌ Registration error")
            messagebox.showerror("Error", f"Registration failed:\n{str(e)}")
            
    def load_user_data(self):
        """Load user's cloud data after successful login"""
        if not self.cloud_sync:
            return
            
        try:
            # Load recipients from cloud
            result = self.cloud_sync.load_recipients()
            if result["success"] and result["recipients"]:
                # Populate recipients list
                for recipient in result["recipients"]:
                    # Add to UI (implement based on your recipient UI)
                    pass
                    
            # Check subscription status
            sub_result = self.cloud_sync.validate_subscription()
            if sub_result["success"]:
                if not sub_result["valid"]:
                    messagebox.showwarning("Subscription Expired", 
                                         f"Your subscription expired on {sub_result.get('expires_at', 'Unknown')}\n\nPlease contact admin to extend your subscription.")
                    
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            
    def on_login_close(self):
        """Handle login window close"""
        self.root.quit()
        
    def setup_window(self):
        """Configure main window"""
        self.root.title("📧 Enhanced Email Sender - Desktop")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Configure styles
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
    
    def create_widgets(self):
        """Create main application widgets"""
        # Header frame
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        # Title
        title_label = ttk.Label(header_frame, text="📧 Enhanced Email Sender", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Cloud status
        username = self.user_data.get("user", {}).get("username", "User") if self.user_data else "User"
        self.cloud_status_label = ttk.Label(header_frame, text=f"☁️ Connected as {username}", 
                                           font=('Segoe UI', 10))
        self.cloud_status_label.pack(side=tk.RIGHT)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create tabs
        self.create_email_tab()
        self.create_recipients_tab()
        self.create_campaigns_tab()
        self.create_cloud_tab()
        self.create_subscription_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_email_tab(self):
        """Create email composition tab"""
        email_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(email_frame, text="📝 Compose Email")
        
        # Subject
        ttk.Label(email_frame, text="Subject:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 10))
        self.subject_entry = ttk.Entry(email_frame, width=60)
        self.subject_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Body
        ttk.Label(email_frame, text="Message:").grid(row=1, column=0, sticky=(tk.W, tk.N), padx=(0, 10), pady=(0, 10))
        
        text_frame = ttk.Frame(email_frame)
        text_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.message_text = tk.Text(text_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.message_text.yview)
        self.message_text.configure(yscrollcommand=scrollbar.set)
        
        self.message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Send button
        send_frame = ttk.Frame(email_frame)
        send_frame.grid(row=2, column=1, sticky=tk.E, pady=(10, 0))
        
        ttk.Button(send_frame, text="🚀 Send Email", command=self.send_email).pack(side=tk.RIGHT)
        
        # Configure grid weights
        email_frame.grid_columnconfigure(1, weight=1)
        email_frame.grid_rowconfigure(1, weight=1)
    
    def create_recipients_tab(self):
        """Create recipients management tab"""
        recipients_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(recipients_frame, text="👥 Recipients")
        
        # Recipients text area
        ttk.Label(recipients_frame, text="Recipients (one email per line):").pack(anchor=tk.W, pady=(0, 5))
        
        text_frame = ttk.Frame(recipients_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.recipients_text = tk.Text(text_frame, wrap=tk.WORD)
        recipients_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.recipients_text.yview)
        self.recipients_text.configure(yscrollcommand=recipients_scrollbar.set)
        
        self.recipients_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        recipients_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(recipients_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📁 Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="💾 Save Local", command=self.save_recipients_local).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="☁️ Save to Cloud", command=self.save_recipients_cloud).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Load from Cloud", command=self.load_recipients_cloud).pack(side=tk.LEFT)
    
    def create_campaigns_tab(self):
        """Create campaigns history and analytics tab"""
        campaigns_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(campaigns_frame, text="📊 Campaigns")
        
        # Header
        header_frame = ttk.Frame(campaigns_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="📊 Campaign History & Analytics", 
                 font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="🔄 Refresh", 
                  command=self.refresh_campaigns).pack(side=tk.RIGHT)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(campaigns_frame, text="Statistics", padding="15")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.stats_labels = {}
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Total emails
        ttk.Label(stats_grid, text="Total Emails Sent:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.stats_labels['total'] = ttk.Label(stats_grid, text="0", font=('Arial', 10))
        self.stats_labels['total'].grid(row=0, column=1, sticky=tk.W)
        
        # Today's emails
        ttk.Label(stats_grid, text="Today:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.stats_labels['today'] = ttk.Label(stats_grid, text="0", font=('Arial', 10))
        self.stats_labels['today'].grid(row=0, column=3, sticky=tk.W)
        
        # This month
        ttk.Label(stats_grid, text="This Month:", font=('Arial', 10, 'bold')).grid(row=0, column=4, sticky=tk.W, padx=(20, 10))
        self.stats_labels['month'] = ttk.Label(stats_grid, text="0", font=('Arial', 10))
        self.stats_labels['month'].grid(row=0, column=5, sticky=tk.W)
        
        # Campaigns history
        history_frame = ttk.LabelFrame(campaigns_frame, text="Recent Campaigns", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for campaigns
        columns = ('Name', 'Emails Sent', 'Date', 'Success Rate', 'Status')
        self.campaigns_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=8)
        
        # Define headings
        for col in columns:
            self.campaigns_tree.heading(col, text=col)
            self.campaigns_tree.column(col, width=120)
        
        # Scrollbar
        campaigns_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.campaigns_tree.yview)
        self.campaigns_tree.configure(yscrollcommand=campaigns_scrollbar.set)
        
        self.campaigns_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        campaigns_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load initial data
        self.refresh_campaigns()
    
    def create_cloud_tab(self):
        """Create cloud management tab"""
        cloud_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(cloud_frame, text="☁️ Cloud Sync")
        
        # Connection status
        status_frame = ttk.LabelFrame(cloud_frame, text="Connection Status", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.connection_status_label = ttk.Label(status_frame, 
                                               text="❌ Not connected to cloud", 
                                               font=('Arial', 11))
        self.connection_status_label.pack()
        
        # Cloud actions
        actions_frame = ttk.LabelFrame(cloud_frame, text="Cloud Actions", padding="15")
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        button_grid = ttk.Frame(actions_frame)
        button_grid.pack()
        
        ttk.Button(button_grid, text="🔐 Connect to Cloud", 
                  command=self.connect_to_cloud).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_grid, text="🔄 Sync Data", 
                  command=self.sync_data).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_grid, text="📊 View Subscription", 
                  command=self.show_subscription_info).grid(row=0, column=2, padx=5, pady=5)
        
        # Cloud data lists
        if self.cloud_sync:
            self.create_cloud_data_lists(cloud_frame)
    
    def create_cloud_data_lists(self, parent):
        """Create cloud data management lists"""
        data_frame = ttk.LabelFrame(parent, text="Cloud Data", padding="15")
        data_frame.pack(fill=tk.BOTH, expand=True)
        
        # Recipient lists from cloud
        ttk.Label(data_frame, text="📧 Your Recipient Lists:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        list_frame = ttk.Frame(data_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cloud_lists_box = tk.Listbox(list_frame, height=8)
        cloud_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.cloud_lists_box.yview)
        self.cloud_lists_box.configure(yscrollcommand=cloud_scrollbar.set)
        
        self.cloud_lists_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cloud_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # List actions
        list_actions = ttk.Frame(data_frame)
        list_actions.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(list_actions, text="📥 Load Selected", 
                  command=self.load_selected_cloud_list).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(list_actions, text="🗑️ Delete Selected", 
                  command=self.delete_selected_cloud_list).pack(side=tk.LEFT)
    
    def create_subscription_tab(self):
        """Create subscription information tab"""
        sub_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(sub_frame, text="💳 Subscription")
        
        if not self.cloud_sync or not self.cloud_sync.user_data:
            ttk.Label(sub_frame, text="Connect to cloud to view subscription information", 
                     font=('Arial', 12)).pack(expand=True)
            return
        
        user = self.cloud_sync.user_data
        
        # Subscription info
        info_frame = ttk.LabelFrame(sub_frame, text="Subscription Information", padding="20")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        info_text = f"""
👤 Username: {user.get('username', 'N/A')}
📧 Email: {user.get('email', 'Not provided')}
🎯 Subscription: {user.get('subscription_type', 'free').title()}
⏰ Expires: {user.get('expires_at', 'N/A')[:10] if user.get('expires_at') else 'N/A'}
📅 Days Remaining: {user.get('days_remaining', 0)}
📊 Emails Sent: {user.get('total_emails_sent', 0)}
        """.strip()
        
        ttk.Label(info_frame, text=info_text, font=('Courier New', 10), 
                 justify=tk.LEFT).pack(anchor=tk.W)
        
        # Expiration warning
        days_remaining = user.get('days_remaining', 0)
        if days_remaining <= 30:
            warning_frame = ttk.LabelFrame(sub_frame, text="⚠️ Expiration Warning", padding="15")
            warning_frame.pack(fill=tk.X, pady=(0, 20))
            
            if days_remaining <= 0:
                warning_text = "🚨 Your subscription has EXPIRED! Contact admin to renew access."
            elif days_remaining <= 7:
                warning_text = f"🚨 Your subscription expires in {days_remaining} days! Renew immediately."
            else:
                warning_text = f"⚠️ Your subscription expires in {days_remaining} days. Plan for renewal."
            
            ttk.Label(warning_frame, text=warning_text, font=('Arial', 11, 'bold'), 
                     foreground='red' if days_remaining <= 7 else 'orange').pack()
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Email settings
        email_settings = ttk.LabelFrame(settings_frame, text="Email Configuration", padding="15")
        email_settings.pack(fill=tk.X, pady=(0, 15))
        
        # SMTP settings would go here
        ttk.Label(email_settings, text="SMTP configuration and email settings will be available here.").pack()
        
        # Application settings
        app_settings = ttk.LabelFrame(settings_frame, text="Application Settings", padding="15")
        app_settings.pack(fill=tk.X)
        
        # Auto-save setting
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(app_settings, text="Auto-save to cloud", 
                       variable=self.auto_save_var).pack(anchor=tk.W, pady=2)
        
        # Auto-sync interval
        ttk.Label(app_settings, text="Sync interval (minutes):").pack(anchor=tk.W, pady=(10, 2))
        self.sync_interval_var = tk.IntVar(value=5)
        ttk.Spinbox(app_settings, from_=1, to=60, textvariable=self.sync_interval_var, width=10).pack(anchor=tk.W)
        
        # Save settings button
        ttk.Button(app_settings, text="💾 Save Settings", 
                  command=self.save_settings).pack(anchor=tk.W, pady=(10, 0))
    
    # Cloud integration methods
    def connect_to_cloud(self):
        """Connect to cloud services"""
        cloud_sync = create_cloud_login_window()
        if cloud_sync:
            self.cloud_sync = cloud_sync
            self.update_cloud_status()
            self.refresh_cloud_tab()
            messagebox.showinfo("Success", "Connected to cloud successfully!")
    
    def update_cloud_status(self):
        """Update cloud connection status display"""
        if self.cloud_sync and self.cloud_sync.user_data:
            user = self.cloud_sync.user_data
            status_text = f"☁️ Connected as {user['username']}"
            self.cloud_status_label.config(text=status_text)
            self.connection_status_label.config(text="✅ Connected to cloud")
        else:
            username = self.user_data.get("user", {}).get("username", "User") if self.user_data else "User"
            self.cloud_status_label.config(text=f"☁️ Connected as {username}")
            self.connection_status_label.config(text="✅ Connected to cloud")
    
    def refresh_cloud_tab(self):
        """Refresh cloud tab content"""
        # Remove and recreate the cloud tab
        for i, tab_id in enumerate(self.notebook.tabs()):
            if self.notebook.tab(tab_id, "text") == "☁️ Cloud Sync":
                self.notebook.forget(tab_id)
                break
        
        self.create_cloud_tab()
    
    def sync_data(self):
        """Sync data with cloud"""
        if not self.cloud_sync:
            messagebox.showwarning("Warning", "Not connected to cloud")
            return
        
        try:
            self.status_bar.config(text="Syncing with cloud...")
            self.root.update()
            
            # Load cloud data
            cloud_lists = self.cloud_sync.load_recipients_from_cloud()
            
            # Update UI if cloud lists exist
            if hasattr(self, 'cloud_lists_box'):
                self.cloud_lists_box.delete(0, tk.END)
                for lst in cloud_lists:
                    display_text = f"{lst['list_name']} ({lst['count']} emails)"
                    self.cloud_lists_box.insert(tk.END, display_text)
            
            self.status_bar.config(text="Sync completed")
            messagebox.showinfo("Success", f"Synced {len(cloud_lists)} recipient lists from cloud")
            
        except Exception as e:
            logger.error(f"Sync error: {e}")
            self.status_bar.config(text="Sync failed")
            messagebox.showerror("Error", f"Sync failed: {str(e)}")
    
    def show_subscription_info(self):
        """Show subscription information window"""
        if self.cloud_sync:
            create_subscription_info_window(self.cloud_sync)
        else:
            messagebox.showinfo("Info", "Connect to cloud to view subscription information")
    
    # Email methods
    def send_email(self):
        """Send email with real SMTP functionality"""
        subject = self.subject_entry.get()
        message = self.message_text.get(1.0, tk.END).strip()
        recipients = self.get_recipients_list()
        
        if not subject or not message or not recipients:
            messagebox.showwarning("Warning", "Please fill in all fields")
            return
        
        # Check subscription status first
        if not self.check_subscription_status():
            return
        
        # Get SMTP settings
        smtp_settings = self.get_smtp_settings()
        if not smtp_settings:
            return
        
        # Send emails in background thread
        self.status_bar.config(text="Sending emails...")
        self.root.update()
        
        threading.Thread(target=self._send_emails_thread, 
                        args=(subject, message, recipients, smtp_settings), 
                        daemon=True).start()
    
    def check_subscription_status(self):
        """Check if user's subscription allows email sending"""
        if not self.cloud_sync or not self.user_data:
            messagebox.showwarning("Warning", "Please login to cloud first")
            return False
        
        # Get recipient count for validation
        recipients = self.get_recipients_list()
        email_count = len(recipients)
        
        if email_count == 0:
            return False
        
        # Validate subscription with cloud
        try:
            validation = self.cloud_sync.validate_subscription(email_count)
            
            if validation is None:
                messagebox.showwarning("Warning", "Could not verify subscription status. Please check your internet connection.")
                return True  # Allow sending if verification fails
            
            if not validation.get("can_send", False):
                error_msg = validation.get("error", "Subscription validation failed")
                messagebox.showerror("Cannot Send Emails", error_msg)
                return False
            
            # Show warnings if any
            warnings = validation.get("warnings", [])
            if warnings:
                warning_text = "\n".join(warnings)
                messagebox.showwarning("Subscription Warning", warning_text)
            
            # Show usage information in status
            usage = validation.get("usage", {})
            limits = validation.get("limits", {})
            
            usage_info = []
            if limits.get("daily_limit", -1) != -1:
                usage_info.append(f"Daily: {usage.get('daily', 0)}/{limits['daily_limit']}")
            if limits.get("monthly_limit", -1) != -1:
                usage_info.append(f"Monthly: {usage.get('monthly', 0)}/{limits['monthly_limit']}")
            
            if usage_info:
                self.status_bar.config(text=f"Usage: {', '.join(usage_info)}")
            
            return True
            
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not verify subscription status: {e}")
            return True  # Allow sending if verification fails
    
    def get_smtp_settings(self):
        """Get SMTP settings from user"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("📧 SMTP Settings")
        settings_window.geometry("400x350")
        settings_window.resizable(False, False)
        
        # Center window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (settings_window.winfo_width() // 2)
        y = (settings_window.winfo_screenheight() // 2) - (settings_window.winfo_height() // 2)
        settings_window.geometry(f"+{x}+{y}")
        
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="SMTP Server Settings", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # SMTP Server
        ttk.Label(main_frame, text="SMTP Server:").pack(anchor=tk.W)
        smtp_server_var = tk.StringVar(value="smtp.gmail.com")
        smtp_server_entry = ttk.Entry(main_frame, textvariable=smtp_server_var, width=40)
        smtp_server_entry.pack(pady=(0, 10), fill=tk.X)
        
        # Port
        ttk.Label(main_frame, text="Port:").pack(anchor=tk.W)
        port_var = tk.StringVar(value="587")
        port_entry = ttk.Entry(main_frame, textvariable=port_var, width=40)
        port_entry.pack(pady=(0, 10), fill=tk.X)
        
        # Email
        ttk.Label(main_frame, text="Your Email:").pack(anchor=tk.W)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(main_frame, textvariable=email_var, width=40)
        email_entry.pack(pady=(0, 10), fill=tk.X)
        
        # Password
        ttk.Label(main_frame, text="App Password:").pack(anchor=tk.W)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=password_var, show="*", width=40)
        password_entry.pack(pady=(0, 15), fill=tk.X)
        
        # Info label
        info_label = ttk.Label(main_frame, 
                              text="For Gmail: Use App Password instead of regular password.\n"
                                   "Enable 2-step verification and generate App Password.",
                              font=("Arial", 9), foreground="gray")
        info_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        result = {"settings": None}
        
        def save_settings():
            if not all([smtp_server_var.get(), port_var.get(), email_var.get(), password_var.get()]):
                messagebox.showwarning("Warning", "Please fill in all fields")
                return
            
            result["settings"] = {
                "smtp_server": smtp_server_var.get(),
                "port": int(port_var.get()),
                "email": email_var.get(),
                "password": password_var.get()
            }
            settings_window.destroy()
        
        def cancel():
            settings_window.destroy()
        
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Send Emails", command=save_settings).pack(side=tk.RIGHT)
        
        settings_window.wait_window()
        return result["settings"]
    
    def _send_emails_thread(self, subject, message, recipients, smtp_settings):
        """Send emails in background thread"""
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(smtp_settings["smtp_server"], smtp_settings["port"])
            server.starttls()
            server.login(smtp_settings["email"], smtp_settings["password"])
            
            sent_count = 0
            failed_count = 0
            
            for recipient in recipients:
                try:
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = smtp_settings["email"]
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    
                    # Add body
                    msg.attach(MIMEText(message, 'plain'))
                    
                    # Send email
                    server.send_message(msg)
                    sent_count += 1
                    
                    # Update status
                    self.root.after(0, lambda: self.status_bar.config(
                        text=f"Sent {sent_count}/{len(recipients)} emails..."))
                    
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to send to {recipient}: {e}")
            
            server.quit()
            
            # Update cloud statistics
            if self.cloud_sync and sent_count > 0:
                try:
                    self.cloud_sync.update_email_stats(sent_count)
                except Exception as e:
                    print(f"Failed to update cloud stats: {e}")
            
            # Show results
            self.root.after(0, lambda: self._show_send_results(sent_count, failed_count))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("SMTP Error", 
                                                           f"Failed to connect to SMTP server:\n{e}"))
        finally:
            self.root.after(0, lambda: self.status_bar.config(text="Ready"))
    
    def _show_send_results(self, sent_count, failed_count):
        """Show email sending results"""
        total = sent_count + failed_count
        if sent_count == total:
            messagebox.showinfo("Success", f"All {sent_count} emails sent successfully!")
        else:
            messagebox.showwarning("Partial Success", 
                                 f"Sent: {sent_count}\nFailed: {failed_count}\nTotal: {total}")
        
        # Clear form
        self.subject_entry.delete(0, tk.END)
        self.message_text.delete(1.0, tk.END)
        
        # Refresh campaigns after sending
        self.refresh_campaigns()
    
    def refresh_campaigns(self):
        """Refresh campaign history and statistics"""
        if not self.cloud_sync:
            return
        
        try:
            # Get user info for statistics
            user_info = self.cloud_sync.get_user_info()
            if user_info:
                self.stats_labels['total'].config(text=str(user_info.get('total_emails_sent', 0)))
                self.stats_labels['today'].config(text=str(user_info.get('daily_emails_sent', 0)))
                self.stats_labels['month'].config(text=str(user_info.get('monthly_emails_sent', 0)))
            
            # Get campaign history
            campaigns = self.cloud_sync.get_campaign_history()
            if campaigns:
                # Clear existing items
                for item in self.campaigns_tree.get_children():
                    self.campaigns_tree.delete(item)
                
                # Add campaigns to tree
                for campaign in campaigns:
                    date_str = campaign.get('timestamp', '')[:10]  # Extract date part
                    success_rate = f"{campaign.get('success_rate', 0):.1f}%"
                    
                    self.campaigns_tree.insert('', 'end', values=(
                        campaign.get('campaign_name', 'Unnamed'),
                        campaign.get('emails_sent', 0),
                        date_str,
                        success_rate,
                        campaign.get('status', 'unknown').title()
                    ))
        
        except Exception as e:
            print(f"Error refreshing campaigns: {e}")
    
    def get_recipients_list(self):
        """Get list of recipients from text area"""
        text = self.recipients_text.get(1.0, tk.END).strip()
        if not text:
            return []
        
        recipients = []
        for line in text.split('\n'):
            email = line.strip()
            if email and '@' in email:
                recipients.append(email)
        
        return recipients
    
    # File operations
    def import_csv(self):
        """Import recipients from CSV file"""
        from tkinter import filedialog
        import csv
        
        file_path = filedialog.askopenfilename(
            title="Import Recipients CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
                    emails = []
                    
                    for row in csv_reader:
                        if row:  # Skip empty rows
                            email = row[0].strip()  # First column
                            if '@' in email:
                                emails.append(email)
                
                self.recipients_text.delete(1.0, tk.END)
                self.recipients_text.insert(1.0, '\n'.join(emails))
                
                messagebox.showinfo("Success", f"Imported {len(emails)} email addresses")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
    
    def save_recipients_local(self):
        """Save recipients to local file"""
        from tkinter import filedialog
        
        recipients = self.get_recipients_list()
        if not recipients:
            messagebox.showwarning("Warning", "No recipients to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Recipients",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(recipients))
                
                messagebox.showinfo("Success", f"Saved {len(recipients)} recipients to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def save_recipients_cloud(self):
        """Save recipients to cloud"""
        if not self.cloud_sync:
            messagebox.showwarning("Warning", "Not connected to cloud")
            return
        
        recipients = self.get_recipients_list()
        if not recipients:
            messagebox.showwarning("Warning", "No recipients to save")
            return
        
        # Ask for list name
        from tkinter import simpledialog
        list_name = simpledialog.askstring("Save to Cloud", "Enter name for this recipient list:")
        
        if list_name:
            try:
                success = self.cloud_sync.save_recipients_to_cloud(list_name, recipients)
                if success:
                    messagebox.showinfo("Success", f"Saved {len(recipients)} recipients to cloud as '{list_name}'")
                    self.sync_data()  # Refresh cloud data
                else:
                    messagebox.showerror("Error", "Failed to save to cloud")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save to cloud: {str(e)}")
    
    def load_recipients_cloud(self):
        """Load recipients from cloud"""
        if not self.cloud_sync:
            messagebox.showwarning("Warning", "Not connected to cloud")
            return
        
        try:
            cloud_lists = self.cloud_sync.load_recipients_from_cloud()
            
            if not cloud_lists:
                messagebox.showinfo("Info", "No recipient lists found in cloud")
                return
            
            # Show selection dialog
            self.show_cloud_list_selection(cloud_lists)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load from cloud: {str(e)}")
    
    def show_cloud_list_selection(self, cloud_lists):
        """Show dialog to select cloud list to load"""
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Recipient List")
        selection_window.geometry("400x300")
        selection_window.resizable(False, False)
        
        # Center window
        selection_window.update_idletasks()
        x = (selection_window.winfo_screenwidth() // 2) - (selection_window.winfo_width() // 2)
        y = (selection_window.winfo_screenheight() // 2) - (selection_window.winfo_height() // 2)
        selection_window.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(selection_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Select a recipient list to load:", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        # List selection
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        for lst in cloud_lists:
            display_text = f"{lst['list_name']} ({lst['count']} emails)"
            listbox.insert(tk.END, display_text)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                selected_list = cloud_lists[selection[0]]
                self.recipients_text.delete(1.0, tk.END)
                self.recipients_text.insert(1.0, '\n'.join(selected_list['recipients']))
                messagebox.showinfo("Success", f"Loaded {len(selected_list['recipients'])} recipients")
                selection_window.destroy()
        
        ttk.Button(button_frame, text="Load Selected", command=load_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=selection_window.destroy).pack(side=tk.LEFT)
    
    def load_selected_cloud_list(self):
        """Load selected cloud list from listbox"""
        if not hasattr(self, 'cloud_lists_box'):
            return
        
        selection = self.cloud_lists_box.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a list to load")
            return
        
        # This would need the actual cloud data - implement as needed
        messagebox.showinfo("Info", "Load selected cloud list functionality")
    
    def delete_selected_cloud_list(self):
        """Delete selected cloud list"""
        if not hasattr(self, 'cloud_lists_box'):
            return
        
        selection = self.cloud_lists_box.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a list to delete")
            return
        
        # This would need the actual cloud data - implement as needed
        messagebox.showinfo("Info", "Delete selected cloud list functionality")
    
    def save_settings(self):
        """Save application settings"""
        settings = {
            "auto_save": self.auto_save_var.get(),
            "sync_interval": self.sync_interval_var.get(),
            "last_updated": datetime.now().isoformat()
        }
        
        if self.cloud_sync:
            success = self.cloud_sync.save_settings_to_cloud(settings)
            if success:
                messagebox.showinfo("Success", "Settings saved to cloud")
            else:
                messagebox.showerror("Error", "Failed to save settings to cloud")
        else:
            # Save locally if no cloud connection
            messagebox.showinfo("Info", "Settings saved locally (no cloud connection)")

def main():
    """Main application entry point"""
    # Check for required modules
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("Error: tkinter not found. Please install Python with tkinter support.")
        return
    
    # Show cloud login first
    print("Starting Enhanced Email Sender...")
    cloud_sync = create_cloud_login_window()
    
    # If user clicked exit or closed the window, quit application
    if cloud_sync is None:
        print("Login cancelled. Exiting...")
        return
        
    # Create main application
    root = tk.Tk()
    app = EnhancedEmailSenderApp(root)
    
    # Set cloud sync if authenticated
    if cloud_sync:
        app.cloud_sync = cloud_sync
        app.update_cloud_status()
        app.refresh_cloud_tab()
        
        # Start subscription monitoring
        def monitor_subscription():
            while True:
                try:
                    if not cloud_sync.check_subscription_status():
                        # Subscription expired
                        root.after(0, lambda: messagebox.showerror(
                            "Subscription Expired", 
                            "Your subscription has expired. The application will close."
                        ))
                        root.after(1000, root.quit)
                        break
                    
                    # Check every 5 minutes
                    threading.Event().wait(300)
                    
                except Exception as e:
                    logger.error(f"Subscription monitoring error: {e}")
                    break
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_subscription, daemon=True)
        monitor_thread.start()
    
    # Start the application
    root.protocol("WM_DELETE_WINDOW", lambda: root.quit())
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Error", f"Application error: {str(e)}")
    finally:
        print("Enhanced Email Sender closed")

if __name__ == "__main__":
    main()
