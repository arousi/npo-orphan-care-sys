import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime
from config import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, COLORS, ROLES, 
    PRIMARY_BACKEND, EXCEL_FILE_PATH, SQLITE_URL
)
from repo.files import RepositoryFactory
from service.auth import AuthManager
from models.models import Base
from ui.components import StyledFrame, StyledButton, StyledLabel, StyledEntry, FormField
from ui.dashboards import ManagerDashboard, VolunteerDashboard, StaffDashboard

logger = logging.getLogger(__name__)

class LoginWindow(tk.Toplevel):
    """Login window for user authentication."""
    
    def __init__(self, parent, auth_manager, on_login_success):
        super().__init__(parent)
        self.title("Login - Kahatayn System")
        self.geometry('400x300')
        self.resizable(False, False)
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        
        # Title
        title = StyledLabel(self, text="Kahatayn - Orphan Family Management", 
                          size='large', weight='bold', fg=COLORS['primary'])
        title.pack(pady=20)
        
        # Username
        username_label = StyledLabel(self, text="Username:")
        username_label.pack(anchor='w', padx=40, pady=(10, 2))
        self.username_entry = StyledEntry(self)
        self.username_entry.pack(padx=40, fill='x')
        
        # Password
        password_label = StyledLabel(self, text="Password:")
        password_label.pack(anchor='w', padx=40, pady=(20, 2))
        self.password_entry = StyledEntry(self, show='*')
        self.password_entry.pack(padx=40, fill='x')
        
        # Login button
        login_btn = StyledButton(self, text="Login", style='success', command=self._login)
        login_btn.pack(pady=30)
        
        # Bind Enter key
        self.username_entry.bind('<Return>', lambda e: self._login())
        self.password_entry.bind('<Return>', lambda e: self._login())
        
        # Focus on username
        self.username_entry.focus()
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
    
    def _login(self):
        """Handle login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Login Failed", "Please enter username and password")
            return
        
        user = self.auth_manager.authenticate(username, password)
        if user:
            logger.info(f"Login successful: {username}")
            self.destroy()
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()

class MainWindow(tk.Tk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.configure(bg=COLORS['light'])
        
        # Initialize repository
        try:
            if PRIMARY_BACKEND == 'sqlite':
                self.repo = RepositoryFactory.get_repository(SQLITE_URL, 'sqlite')
                logger.info("Using SQLite backend")
            else:
                self.repo = RepositoryFactory.get_repository(str(EXCEL_FILE_PATH), 'excel')
                logger.info("Using Excel backend")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize database: {e}")
            logger.error(f"Database initialization error: {e}")
            self.destroy()
            return
        
        # Initialize auth manager
        self.auth_manager = AuthManager(self.repo)
        
        # Current user
        self.current_user = None
        self.current_dashboard = None
        
        # Show login
        self._show_login()
    
    def _show_login(self):
        """Show login window."""
        login = LoginWindow(self, self.auth_manager, self._on_login_success)
        self.wait_window(login)
    
    def _on_login_success(self, user):
        """Handle successful login."""
        self.current_user = user
        role = user.role if hasattr(user, 'role') else user.get('role')
        logger.info(f"User logged in: {user.username if hasattr(user, 'username') else user.get('username')} ({role})")
        self._load_dashboard(role)
    
    def _load_dashboard(self, role):
        """Load appropriate dashboard based on role."""
        # Clear previous dashboard
        if self.current_dashboard:
            self.current_dashboard.destroy()
        
        # Create new dashboard
        if role == 'manager':
            self.current_dashboard = ManagerDashboard(self, self.current_user, self.repo, self._on_logout)
        elif role == 'volunteer':
            self.current_dashboard = VolunteerDashboard(self, self.current_user, self.repo, self._on_logout)
        elif role == 'staff':
            self.current_dashboard = StaffDashboard(self, self.current_user, self.repo, self._on_logout)
        else:
            messagebox.showerror("Error", f"Unknown role: {role}")
            self._on_logout()
            return
        
        self.current_dashboard.pack(fill='both', expand=True)
    
    def _on_logout(self):
        """Handle logout."""
        self.auth_manager.logout()
        if self.current_dashboard:
            self.current_dashboard.destroy()
        self.current_user = None
        self._show_login()

def main():
    """Main entry point."""
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == '__main__':
    main()
