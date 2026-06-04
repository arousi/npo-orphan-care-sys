# Kahatayn NPO System - Quick Setup Guide

## For Developers: Build the .exe

### Windows

1. **Open Command Prompt** in the project folder
2. **Run setup**:
   ```
   setup_venv.bat
   ```
   This creates the virtual environment and installs all dependencies.

3. **Build the .exe**:
   ```
   run_build.bat
   ```
   This creates a portable executable in the `dist/` folder.

4. **Test the .exe**:
   ```
   dist\Kahatayn.exe
   ```

### Linux/Mac

```bash
chmod +x setup_venv.sh
./setup_venv.sh

chmod +x run_build.sh
./run_build.sh

# Test
./dist/Kahatayn
```

---

## For NPO: Run the Application

### Windows NPO User

1. **Get the folder**: Receive `Kahatayn/` folder (from developer)
2. **Run the app**: Double-click `Kahatayn.exe`
3. **Data is auto-saved** in the `data/` subfolder
4. **Backups created** automatically when you close the app

### Linux/Mac NPO User

1. **Get the folder**: Receive `Kahatayn/` folder
2. **Run the app**: 
   ```
   ./Kahatayn
   ```
   Or double-click if available
3. **Everything else same as Windows**

---

## Data Management

### Automatic Backups
- Every time you close the app, all data is backed up
- Backups saved in: `data/backups/`
- Includes SQLite, Excel, and ODS in one backup set

### Manual Backup
From the app (Manager → Settings):
- Click "Backup Data"
- Creates timestamped backup immediately

### Export Data for External Modification
From the app (Manager → Settings):
- Click "Export Data"
- Creates ZIP with data files
- NPO can modify Excel/ODS files externally
- Send back to import

### Restore from Backup
From the app (Manager → Settings):
- Click "Restore Backup"
- Select a backup file
- Confirm to restore

---

## File Structure

```
dist/
├── Kahatayn.exe                 ← Run this!
├── _internal/                   ← Libraries (don't touch)
└── data/
    ├── orphanage.db             ← SQLite database
    ├── orphanage_data.xlsx      ← Excel spreadsheet
    ├── orphanage_data.ods       ← ODS spreadsheet
    ├── backups/                 ← Automatic backups
    │   ├── orphanage_backup_*.db
    │   ├── orphanage_backup_*.xlsx
    │   ├── orphanage_backup_*.ods
    │   └── orphanage_backup_*.manifest
    ├── exports/                 ← Manual exports
    └── reports/                 ← Generated PDFs

logs/
├── app_20240604.log            ← Application logs
```

---

## Key Features

✓ **No Installation** - Just run Kahatayn.exe  
✓ **All Data Included** - DB, Excel, ODS files bundled  
✓ **Auto Backup** - Happens when you close  
✓ **Multi-Format** - Work with SQLite, Excel, or ODS  
✓ **External Editing** - NPO staff can edit Excel/ODS  
✓ **PDF Reports** - Generate and export reports  
✓ **Multi-Language** - English & Arabic support  
✓ **Role-Based Access** - Manager, Volunteer, Staff roles  

---

## Troubleshooting

### .exe Won't Open
- Check Windows antivirus isn't blocking it
- Make sure entire `dist/` folder is copied
- Look in `logs/` folder for error details

### Can't Save Changes
- Close Excel/ODS if editing externally
- Ensure `data/` folder is writable
- Check disk space available

### Need to Restore Data
1. Open app and go to Manager → Settings
2. Click "Restore Backup"
3. Select the backup you want to restore
4. Click Confirm

### Lost Files
1. Check `data/backups/` folder
2. Restore the latest backup from there
3. If still missing, contact developer

---

## For Developers: What's Included

### Build System
- `setup_venv.bat/sh` - Creates virtual environment
- `run_build.bat/sh` - Builds executable
- `kahatayn.spec` - PyInstaller configuration
- `requirements.txt` - Python dependencies

### Project Files
- `main.py` - Application entry point
- `config.py` - Configuration (portable paths)
- `models/` - Database models
- `repo/` - Data layer (SQLite, Excel, ODS)
- `service/` - Business logic (Backup, PDF, i18n, Export)
- `ui/` - User interface (Tkinter)

### Services
- **BackupService** - Auto/manual backups
- **PDFReportService** - Generate PDF reports
- **I18nService** - English/Arabic translations
- **DataExportService** - Export/import data
- **AuthManager** - User authentication

---

## Environment Variables

Optional - Create `.env` file for custom settings:

```env
# Primary storage backend (sqlite or excel)
PRIMARY_BACKEND=excel

# Enable/disable features
BACKUP_ENABLED=True
BACKUP_ON_APP_CLOSE=True
AUTO_EMPTY_AFTER_BACKUP=True

# Language (en or ar)
DEFAULT_LANGUAGE=en
```

---

## Next Steps

### For Developers
1. Run `setup_venv.bat`
2. Create initial data in `data/` folder
3. Run `run_build.bat` to create .exe
4. Test `dist/Kahatayn.exe`
5. Distribute `dist/` folder to NPO

### For NPO
1. Receive and extract `dist/` folder
2. Double-click `Kahatayn.exe`
3. Login with provided credentials
4. Start using the system!
5. Changes auto-backup on close

---

## Support

**For bug reports or questions:**
- Check logs in `logs/` folder
- Review documentation files (QUICKSTART.md, FEATURES_GUIDE.md)
- Contact development team with issue details

**Documentation files:**
- `README.md` - Project overview
- `QUICKSTART.md` - User workflows
- `FEATURES_GUIDE.md` - Feature documentation
- `DEPLOYMENT_GUIDE.md` - Detailed deployment info
- `IMPLEMENTATION_SUMMARY.md` - Technical details
