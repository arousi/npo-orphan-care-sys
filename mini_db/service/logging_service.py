"""
Advanced Logging Service for Kahatayn
Tracks user interactions, system events, and errors for debugging
"""

import logging
import logging.handlers
import traceback
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional, Dict

from config import LOGS_DIR, BASE_DIR

logger = logging.getLogger(__name__)


class AdvancedLogger:
    """
    Comprehensive logging service that tracks:
    - User interactions (UI clicks, navigation)
    - System events and state changes
    - Errors with full context
    - Application flow
    """
    
    def __init__(self):
        """Initialize the advanced logging service."""
        self.logs_dir = LOGS_DIR
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create separate loggers
        self.app_logger = self._setup_logger('app')
        self.user_logger = self._setup_logger('user_actions')
        self.error_logger = self._setup_logger('errors')
        self.system_logger = self._setup_logger('system')
        
        self.current_user = None
        self.current_screen = "Login"
        
        self.app_logger.info("="*60)
        self.app_logger.info("AdvancedLogger Service Initialized")
        self.app_logger.info(f"Logs directory: {self.logs_dir}")
        self.app_logger.info("="*60)
    
    def _setup_logger(self, name: str) -> logging.Logger:
        """
        Create and configure a logger with file and console handlers.
        
        Args:
            name: Logger name
            
        Returns:
            Configured logger instance
        """
        logger_instance = logging.getLogger(f"kahatayn.{name}")
        logger_instance.setLevel(logging.DEBUG)
        
        # Don't add handlers if already present
        if logger_instance.handlers:
            return logger_instance
        
        # File handler
        log_file = self.logs_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger_instance.addHandler(file_handler)
        logger_instance.addHandler(console_handler)
        
        return logger_instance
    
    def set_user(self, username: str):
        """Track the current logged-in user."""
        self.current_user = username
        self.user_logger.info(f"User logged in: {username}")
    
    def clear_user(self):
        """Clear user when logging out."""
        if self.current_user:
            self.user_logger.info(f"User logged out: {self.current_user}")
        self.current_user = None
    
    def set_screen(self, screen_name: str):
        """Track which screen/window user is on."""
        self.current_screen = screen_name
        self.user_logger.debug(f"Screen changed to: {screen_name}")
    
    def user_action(self, action: str, details: Optional[Dict[str, Any]] = None, 
                   screen: Optional[str] = None):
        """
        Log a user action (button click, form submission, etc).
        
        Args:
            action: What the user did (e.g., "clicked_save", "opened_dialog")
            details: Additional information about the action
            screen: Override current screen for this log
        """
        screen = screen or self.current_screen
        user = self.current_user or "Anonymous"
        
        message = f"User: {user} | Screen: {screen} | Action: {action}"
        
        if details:
            message += f" | Details: {json.dumps(details, default=str)}"
        
        self.user_logger.info(message)
    
    def system_state(self, component: str, state: str, details: Optional[Dict] = None):
        """
        Log system state changes.
        
        Args:
            component: Which component (e.g., "BackupService", "PDFService")
            state: What changed (e.g., "backup_started", "pdf_generated")
            details: Additional information
        """
        message = f"Component: {component} | State: {state}"
        
        if details:
            message += f" | Details: {json.dumps(details, default=str)}"
        
        self.system_logger.info(message)
    
    def error(self, error_message: str, exception: Optional[Exception] = None,
             context: Optional[Dict[str, Any]] = None):
        """
        Log an error with full context.
        
        Args:
            error_message: Error description
            exception: Exception object (if any)
            context: Context information (user, screen, action, etc)
        """
        user = self.current_user or "Unknown"
        screen = self.current_screen
        
        error_log = f"\n{'='*60}\n"
        error_log += f"TIMESTAMP: {datetime.now().isoformat()}\n"
        error_log += f"USER: {user}\n"
        error_log += f"SCREEN: {screen}\n"
        error_log += f"ERROR: {error_message}\n"
        
        if context:
            error_log += f"CONTEXT:\n"
            for key, value in context.items():
                error_log += f"  {key}: {value}\n"
        
        if exception:
            error_log += f"\nEXCEPTION TYPE: {type(exception).__name__}\n"
            error_log += f"EXCEPTION: {str(exception)}\n"
            error_log += f"TRACEBACK:\n{traceback.format_exc()}\n"
        
        error_log += f"{'='*60}\n"
        
        self.error_logger.error(error_log)
    
    def critical_error(self, error_message: str, exception: Optional[Exception] = None):
        """Log a critical error that affects app functionality."""
        error_log = f"\n{'*'*60}\n"
        error_log += f"CRITICAL ERROR at {datetime.now().isoformat()}\n"
        error_log += f"User: {self.current_user or 'Unknown'}\n"
        error_log += f"Screen: {self.current_screen}\n"
        error_log += f"Message: {error_message}\n"
        
        if exception:
            error_log += f"\nFull Traceback:\n{traceback.format_exc()}\n"
        
        error_log += f"{'*'*60}\n"
        
        self.error_logger.critical(error_log)
    
    def debug(self, component: str, message: str, details: Optional[Dict] = None):
        """Log debug information."""
        msg = f"[{component}] {message}"
        if details:
            msg += f" | {json.dumps(details, default=str)}"
        self.app_logger.debug(msg)
    
    def info(self, component: str, message: str):
        """Log general information."""
        self.app_logger.info(f"[{component}] {message}")
    
    def warning(self, component: str, message: str, details: Optional[Dict] = None):
        """Log warnings."""
        msg = f"[{component}] {message}"
        if details:
            msg += f" | {json.dumps(details, default=str)}"
        self.app_logger.warning(msg)
    
    def get_log_files(self) -> Dict[str, Path]:
        """
        Get all log files for sharing.
        
        Returns:
            Dictionary of log type to file path
        """
        log_files = {}
        
        if self.logs_dir.exists():
            for log_file in sorted(self.logs_dir.glob("*.log"), reverse=True):
                log_type = log_file.stem.split('_')[0]
                log_files[log_type] = log_file
        
        return log_files
    
    def create_debug_package(self, filename: Optional[str] = None) -> Optional[Path]:
        """
        Create a ZIP with all logs for sharing with developer.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to created debug package
        """
        try:
            import zipfile
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"kahatayn_debug_{timestamp}.zip"
            
            debug_path = self.logs_dir.parent / filename
            
            with zipfile.ZipFile(debug_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add all log files
                for log_file in self.logs_dir.glob("*.log"):
                    zf.write(log_file, log_file.name)
                
                # Add system info
                info = self._get_system_info()
                zf.writestr("system_info.txt", info)
            
            self.app_logger.info(f"Debug package created: {debug_path}")
            return debug_path
        except Exception as e:
            self.error("Failed to create debug package", exception=e)
            return None
    
    def _get_system_info(self) -> str:
        """Get system information for debugging."""
        try:
            import platform
            import sys
            
            info = f"""
KAHATAYN DEBUG INFORMATION
=========================
Generated: {datetime.now().isoformat()}

SYSTEM INFO:
- Platform: {platform.platform()}
- Python Version: {sys.version}
- Architecture: {platform.architecture()}

APPLICATION INFO:
- Base Directory: {BASE_DIR}
- Logs Directory: {self.logs_dir}
- Current User: {self.current_user or 'None'}
- Current Screen: {self.current_screen}

LOG FILES:
"""
            for log_file in self.logs_dir.glob("*.log"):
                size_kb = log_file.stat().st_size / 1024
                info += f"- {log_file.name} ({size_kb:.2f} KB)\n"
            
            return info
        except Exception as e:
            return f"Error gathering system info: {e}"
    
    def session_summary(self):
        """Log a session summary."""
        summary = f"""
{'='*60}
SESSION SUMMARY
{'='*60}
User: {self.current_user or 'Unknown'}
Session End: {datetime.now().isoformat()}
Final Screen: {self.current_screen}
{'='*60}
"""
        self.app_logger.info(summary)


# Global logger instance
_global_logger = None


def get_logger() -> AdvancedLogger:
    """Get or create the global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = AdvancedLogger()
    return _global_logger
