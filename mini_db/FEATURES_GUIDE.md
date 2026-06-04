# Example Usage of New Features

This file demonstrates how to use the three newly added features:
1. Daily Backup Service
2. PDF Report Generation
3. Multi-Language Support (i18n)

## 1. Daily Backup Service

The backup service automatically backs up your data in multiple formats (SQLite, Excel, ODS) when the application closes.

### Configuration (in config.py)

```python
# Enable/disable backups
BACKUP_ENABLED = True

# Backup when manager closes the application
BACKUP_ON_APP_CLOSE = True

# Automatically empty the database after backing up
AUTO_EMPTY_AFTER_BACKUP = True

# Keep backups infinitely (False) or cleanup old ones (True)
BACKUP_RETENTION_ENABLED = False

# If retention is enabled, delete backups older than this many days
MAX_BACKUP_RETENTION_DAYS = 30
```

### Usage in Code

```python
from service.backup_service import BackupService

# Initialize backup service
backup_service = BackupService()

# Manual backup anytime (backs up SQLite, XLSX, and ODS)
backup_service.manual_backup()

# List all backups (all formats)
backups = backup_service.list_backups()

# List backups by format
sqlite_backups = backup_service.list_sqlite_backups()
xlsx_backups = backup_service.list_xlsx_backups()
ods_backups = backup_service.list_ods_backups()

# Restore from a backup (automatically detects format)
backup_service.restore_backup(backups[0])

# Get backup statistics
stats = backup_service.get_backup_stats()
print(f"Total backups: {stats['total_backups']}")
print(f"SQLite backups: {stats['sqlite_backups']}")
print(f"Excel backups: {stats['xlsx_backups']}")
print(f"ODS backups: {stats['ods_backups']}")
print(f"Total size: {stats['total_size_mb']} MB")
```

### Features

- **Multi-format backups**: SQLite (.db), Excel (.xlsx), and ODS (.ods) all backed up together
- **Automatic backup on app close** when manager closes the application
- **Manual backup** on demand
- **Auto-empty database** after successful backup (preserves schema)
- **Infinite backup retention** - keeps all backups indefinitely
- **Format-specific queries** - list or restore specific file types
- **Manifest files** - metadata for each backup set
- **Automatic format detection** - restore from any backup file type

### Backup Directory Structure

```
data/backups/
├── orphanage_backup_20240606_143022.db
├── orphanage_backup_20240606_143022.xlsx
├── orphanage_backup_20240606_143022.ods
├── orphanage_backup_20240606_143022.manifest
├── orphanage_20240605_100000.db
├── orphanage_20240605_100000.xlsx
├── orphanage_20240605_100000.ods
└── orphanage_20240605_100000.manifest
```

---

## 2. PDF Report Generation

Generate professional PDF reports from your system data.

### Supported Reports

1. **Family Assessment Summary** - Summary of all family cases with status
2. **Volunteer Activity Report** - Volunteer activities and assignments
3. **Financial Overview** - Financial metrics and summaries

### Usage in Code

```python
from service.pdf_service import PDFReportService

# Initialize PDF service
pdf_service = PDFReportService()

# Generate family assessment report
families = [
    {
        'family_code': 'FAM-000001',
        'status': 'Active',
        'number_of_children': 3,
        'monthly_income': '$500',
        'monthly_expenses': '$800',
        'assessment_status': 'Complete'
    },
    # ... more families
]
pdf_path = pdf_service.generate_family_assessment_summary(families)
print(f"Report generated: {pdf_path}")

# Generate volunteer activity report
volunteers = [
    {
        'volunteer_code': 'VOL-000001',
        'name': 'Ahmed Hassan',
        'specialization': 'Education',
        'assignment_count': 3,
        'status': 'Active'
    },
    # ... more volunteers
]
pdf_path = pdf_service.generate_volunteer_activity_report(volunteers)

# Generate financial overview
financial_data = {
    'total_families': 45,
    'total_orphans': 120,
    'active_volunteers': 12,
    'average_family_income': '$450',
    'total_sponsorship_amount': '$5400'
}
pdf_path = pdf_service.generate_financial_overview(financial_data)

# List all generated reports
reports = pdf_service.list_reports()
for report in reports:
    print(f"Report: {report.name}")

# Delete a report
pdf_service.delete_report(reports[0])
```

### Report Output

All reports are generated in the `data/reports/` directory with timestamps:
- `family_assessment_20240606_143022.pdf`
- `volunteer_activity_20240606_143022.pdf`
- `financial_overview_20240606_143022.pdf`

Each report includes:
- Professional header with title
- Generation date and time
- Data tables with color-coded headers
- Automatic pagination for large datasets

---

## 3. Multi-Language Support (i18n)

Easily switch your application between English and Arabic.

### Configuration (in config.py)

```python
# Default language ('en' for English, 'ar' for Arabic)
DEFAULT_LANGUAGE = 'en'

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ar': 'العربية (Arabic)'
}
```

### Usage in Code

```python
from service.i18n import I18nService

# Initialize with default language
i18n = I18nService()  # Defaults to English

# Or specify a language
i18n = I18nService('ar')  # Start in Arabic

# Translate a string
welcome_text = i18n.t('welcome')  # Returns: "أهلا وسهلا" (if Arabic)

# Change language
i18n.set_language('ar')
welcome_text = i18n.t('welcome')  # Returns: "أهلا وسهلا"

# Get current language
current_lang = i18n.get_language()  # Returns: 'ar'

# Get language name
lang_name = i18n.get_language_name()  # Returns: "العربية (Arabic)"

# Check if RTL (right-to-left)
if i18n.is_rtl():
    # Apply RTL layout
    pass

# Get all supported languages
languages = i18n.get_supported_languages()
# Returns: {'en': 'English', 'ar': 'العربية (Arabic)'}
```

### Adding Translations to Your UI

```python
from service.i18n import I18nService

i18n = I18nService()

# In your Tkinter buttons and labels:
from ui.components import StyledButton

# English button
logout_btn = StyledButton(
    parent, 
    text=i18n.t('logout'),  # "Logout" or "تسجيل الخروج"
    style='danger'
)

# You can also add new translations programmatically
i18n.add_translation('en', 'custom_key', 'Custom English Text')
i18n.add_translation('ar', 'custom_key', 'النص العربي المخصص')
```

### Available Translations

The system includes pre-translated strings for:
- UI button labels
- Dashboard and menu text
- Form field labels
- Status messages
- Error messages
- Menu items
- Report names
- Settings labels
- Months and time-related text

### Example: Language Switcher in Settings

```python
from tkinter import Combobox
from service.i18n import I18nService

i18n = I18nService()

# Create language selector
languages = i18n.get_supported_languages()
language_combo = Combobox(
    parent,
    values=list(languages.values()),
    state='readonly'
)

# When user changes language
def on_language_change(event):
    selected_name = language_combo.get()
    # Find the language code
    for code, name in languages.items():
        if name == selected_name:
            i18n.set_language(code)
            # Refresh UI with new language
            break

language_combo.bind('<<ComboboxSelected>>', on_language_change)
```

### Exporting and Importing Translations

You can export translations to JSON files for external editing or translation services:

```python
from pathlib import Path

# Export Arabic translations
i18n.export_translations('ar', Path('data/translations_ar.json'))

# Later, import them back
i18n.import_translations('ar', Path('data/translations_ar.json'))
```

---

## Integration with Main Application

Here's how to integrate all three features into your application (backup on manager close):

```python
import tkinter as tk
from service.backup_service import BackupService
from service.pdf_service import PDFReportService
from service.i18n import I18nService
from repo.files import RepositoryFactory
from ui.dashboards import ManagerDashboard

def main():
    # Initialize services
    backup_service = BackupService()
    pdf_service = PDFReportService()
    i18n = I18nService()
    
    # Create main window
    root = tk.Tk()
    root.title(i18n.t('kahatayn_system'))
    
    # ... rest of your UI code ...
    # Show manager dashboard that on close triggers backup
    
    def on_manager_close():
        # Perform backup when manager closes
        if backup_service.backup_on_close:
            print("Performing backup on application close...")
            backup_service.daily_backup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_manager_close)
    root.mainloop()

if __name__ == '__main__':
    main()
```

---

## Best Practices

### Backup Service
- Backups are stored in: `data/backups/`
- Backups include all three formats: SQLite, Excel, and ODS
- Backup files are timestamped: `orphanage_backup_20240606_143022.*`
- Each backup set has a manifest file with metadata
- Backups happen automatically on app close (configure in config.py)
- Run manual backups before major operations
- All backups are kept infinitely unless `BACKUP_RETENTION_ENABLED = True`

### PDF Service
- Reports are timestamped in the `data/reports/` directory
- Use custom filenames for important reports
- PDF reports include all relevant styling and formatting
- Reports are suitable for printing and distribution
- Consider batch generating reports at month/year end

### i18n Service
- Always use `i18n.t('key')` for all user-facing text
- Keep keys descriptive and lowercase
- Test both LTR (English) and RTL (Arabic) layouts
- Export translations before updates
- Document custom translation keys

---

## Troubleshooting

### Backup Issues
- **"Backup is disabled in configuration"** - Set `BACKUP_ENABLED = True` in config.py
- **"SQLite database not found"** - Ensure SQLite is being used as primary backend
- **Multiple backup formats** - XLSX and ODS files are optional; they're only backed up if they exist
- **Backup permissions** - Ensure the `data/backups/` directory is writable

### PDF Issues
- **"No suitable PDF engine found"** - Install reportlab: `pip install reportlab`
- **PDF files empty** - Ensure data is passed as list of dictionaries
- **Missing fonts** - PDFs use standard fonts (Helvetica) which are always available

### i18n Issues
- **Missing translations** - Check that the key exists in TRANSLATIONS dict
- **Fallback to English** - Empty strings default to the key itself
- **RTL layout issues** - Use `is_rtl()` to conditionally apply RTL styling in Tkinter

---

## Next Steps

1. Install required packages: `pip install -r requirements.txt`
2. Enable features in config.py
3. Integrate services into your UI
4. Test backup/restore process
5. Generate sample PDF reports
6. Test language switching
