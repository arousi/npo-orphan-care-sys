import os
from pathlib import Path
from datetime import datetime
import logging
import sys

# ===========================================
# PROJECT PATHS (Portable for .exe)
# ===========================================
# Detect if running as .exe or Python
IS_EXECUTABLE = getattr(sys, 'frozen', False)

if IS_EXECUTABLE:
    # Running as .exe - use exe directory
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as Python script
    BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ===========================================
# DATABASE AND STORAGE
# ===========================================
# Primary storage backend: 'sqlite' or 'excel' (Excel is live for NPO)
PRIMARY_BACKEND = 'excel'  # Can also be 'sqlite' for local testing

# SQLite configuration
SQLITE_DB_PATH = DATA_DIR / "orphanage.db"
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Excel/ODS file paths (LIVE sheets for NPO staff)
EXCEL_FILE_PATH = DATA_DIR / "orphanage_data.xlsx"
ODS_FILE_PATH = DATA_DIR / "orphanage_data.ods"

# Auto-backup intervals (in minutes)
BACKUP_INTERVAL = 60

# ===========================================
# USER ROLES AND PERMISSIONS
# ===========================================
ROLES = {
    'manager': {
        'description': 'NPO Manager - Full system access',
        'permissions': [
            'view_all_cases',
            'create_case',
            'edit_case',
            'delete_case',
            'assign_volunteer',
            'generate_reports',
            'manage_users',
            'view_analytics',
            'export_data'
        ]
    },
    'volunteer': {
        'description': 'Volunteer - Limited case management',
        'permissions': [
            'view_assigned_cases',
            'update_case_status',
            'add_case_notes',
            'view_family_info',
            'create_assessment'
        ]
    },
    'staff': {
        'description': 'Staff - Data entry and reporting',
        'permissions': [
            'view_all_cases',
            'create_case',
            'edit_case_basics',
            'add_documents',
            'generate_reports',
            'export_data'
        ]
    }
}

# ===========================================
# LOGGING CONFIGURATION
# ===========================================
LOG_LEVEL = logging.INFO
LOG_FILE = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ===========================================
# UI/TKINTER CONFIGURATION
# ===========================================
WINDOW_TITLE = "Kahatayn - Orphan Family Management System"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 10
FONT_SIZE_LARGE = 12
FONT_SIZE_TITLE = 14

# Color scheme
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#3498DB',
    'success': '#27AE60',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'light': '#ECF0F1',
    'dark': '#2C3E50',
    'text': '#2C3E50'
}

# ===========================================
# BUSINESS RULES
# ===========================================
# Orphan age thresholds
ADULT_AGE_THRESHOLD = 18
SPONSORSHIP_LIMIT_PER_VOLUNTEER = 10

# Assessment fields (financial support evaluation)
ASSESSMENT_FIELDS = [
    'salary', 'side_income',
    'gov_support_daman', 'gov_support_tadamun', 'gov_support_child',
    'rent', 'utilities', 'food', 'education', 'health'
]

# Document types
DOCUMENT_TYPES = [
    'ID Card',
    'Birth Certificate',
    'School Certificate',
    'Medical Report',
    'Family Assessment',
    'Sponsorship Agreement',
    'Volunteer Report',
    'Other'
]

# ===========================================
# BACKUP CONFIGURATION
# ===========================================
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)
BACKUP_ENABLED = True
BACKUP_ON_APP_CLOSE = True  # Backup automatically when app closes (manager dashboard)
AUTO_EMPTY_AFTER_BACKUP = True  # Empty SQLite DB after backup
BACKUP_RETENTION_ENABLED = False  # Keep backups infinitely (set to True to cleanup old backups)
MAX_BACKUP_RETENTION_DAYS = 30  # Keep backups for this many days (only if BACKUP_RETENTION_ENABLED is True)

# ===========================================
# MULTI-LANGUAGE SUPPORT (LOCALIZATION)
# ===========================================
# Supported languages: 'en' (English), 'ar' (Arabic)
DEFAULT_LANGUAGE = 'en'
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ar': 'العربية (Arabic)'
}

# ===========================================
# DEVELOPMENT
# ===========================================
DEBUG = False  # Set to True for development
DEMO_MODE = False  # Set to True to load sample data
