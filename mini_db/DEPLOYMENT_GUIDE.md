# Kahatayn NPO System - Deployment Guide

## Quick Setup & Distribution

This guide covers how to:
1. Set up a Python virtual environment
2. Build the portable .exe
3. Distribute to NPO locations
4. Manage data backups and external modifications

---

## Windows Setup

### Step 1: Create Virtual Environment

Run the setup script from your Windows computer:

```bash
setup_venv.bat
```

This will:
- Create a virtual environment folder: `npo_venv\`
- Install all dependencies
- Be ready for building the .exe

Output should show:
```
Setup Complete!
Virtual environment created at: npo_venv\
```

### Step 2: Build the Portable .exe

Run the build script:

```bash
run_build.bat
```

This will:
- Clean previous build artifacts
- Bundle Python, all dependencies, and data files
- Create `dist\Kahatayn.exe`

Output should show:
```
Build Complete!
The .exe is ready at:
  dist\Kahatayn.exe
```

### Step 3: Prepare for Distribution

```
dist/
├── Kahatayn.exe          ← Run this file
├── _internal/            ← Libraries (do not modify)
└── data/
    ├── orphanage.db      ← SQLite database
    ├── orphanage_data.xlsx  ← Excel file
    ├── orphanage_data.ods   ← ODS file
    ├── backups/          ← Automated backups folder
    └── reports/          ← Generated PDF reports

logs/
├── app_20240604.log      ← Application logs
└── ...

```

---

## Linux/Mac Setup

### Step 1: Create Virtual Environment

```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

### Step 2: Build the Executable

```bash
chmod +x run_build.sh
./run_build.sh
```

---

## Distribution to NPO

### For Windows Users

1. **Copy the folder**: Give the NPO a copy of the `dist/` folder
2. **Run the app**: They double-click `Kahatayn.exe`
3. **Data location**: All data stays in the `dist/data/` folder

### File Structure on NPO Computer

```
Kahatayn/
├── Kahatayn.exe
├── _internal/
└── data/
    ├── orphanage.db
    ├── orphanage_data.xlsx
    ├── orphanage_data.ods
    ├── backups/
    │   ├── orphanage_backup_20240604_150000.db
    │   ├── orphanage_backup_20240604_150000.xlsx
    │   ├── orphanage_backup_20240604_150000.ods
    │   └── orphanage_backup_20240604_150000.manifest
    └── reports/
        ├── family_assessment_20240604_150000.pdf
        └── ...
```

---

## Managing Data: Backup & Export

### Automatic Backup on App Close

When the manager closes the application:
1. All data files are automatically backed up
2. Backups saved to: `data/backups/`
3. Each backup includes:
   - SQLite database (.db)
   - Excel file (.xlsx)
   - ODS spreadsheet (.ods)
   - Manifest with metadata

### Manual Database Backup

Within the app (Manager → Settings):
- Click "Backup Data"
- Creates timestamped backup: `orphanage_backup_20240604_150000.*`
- All 3 formats backed up together

### NPO Can Modify External Files

The NPO can work with the data directly:

#### Modifying Excel File
```
1. Close the Kahatayn app
2. Open data/orphanage_data.xlsx in Excel
3. Make changes (add families, update assessments, etc.)
4. Save and close Excel
5. Reopen Kahatayn - changes are loaded
```

#### Modifying ODS File
```
1. Close the Kahatayn app
2. Open data/orphanage_data.ods in LibreOffice/OpenOffice
3. Make changes
4. Save and close
5. Reopen Kahatayn - changes are loaded
```

#### Modifying SQLite Database
```
For advanced users:
1. Close Kahatayn
2. Use SQLite tools (SQLiteStudio, DBeaver, etc.)
3. Connect to data/orphanage.db
4. Make changes
5. Save changes
6. Reopen Kahatayn
```

---

## Restoring from Backup

### Via the Application

1. Manager → Settings → "Restore Backup"
2. Select a backup file from `data/backups/`
3. Choose backup type (SQLite, Excel, ODS)
4. Confirm restore
5. Application auto-restarts with restored data

### Manual Restore

1. Navigate to `data/backups/`
2. Copy the `.db`, `.xlsx`, or `.ods` file you want to restore
3. Paste into `data/` folder (overwriting current file)
4. Reopen Kahatayn

---

## Export Data for External Use

### Generate PDF Reports

Manager → Reports & Analytics:
- Family Assessment Summary → PDF
- Volunteer Activity Report → PDF
- Financial Overview → PDF

Reports saved to: `data/reports/`

### Export to External Formats

From Settings:
- Export to CSV
- Export to Excel (custom format)
- Export full backup package (all files + metadata)

---

## Troubleshooting

### .exe Won't Start
- Verify `_internal/` folder exists
- Check Windows antivirus isn't blocking it
- Look in logs folder for error details

### Data Not Saving
- Ensure app is closed before modifying files externally
- Check file permissions on data folder
- Backup will restore if needed

### Missing Data Files
- Check `data/` subfolder exists
- Restore from `data/backups/` if available
- Contact support with issue details

### Building .exe Issues

#### Python Not Found
```
error: Python is not installed or not in PATH
```
Solution: Install Python 3.8+ and add to PATH

#### PyInstaller Error
```
pip install pyinstaller --upgrade
```

#### Build Folder Too Large
- Normal: .exe is ~100-200 MB
- Includes Python, all libraries, and data
- Easier to distribute than managing dependencies separately

---

## NPO Operations Workflow

### Daily Use
```
1. Manager opens Kahatayn.exe
2. Uses system for case management
3. Closes application (automatic backup)
4. Staff can optionally edit Excel/ODS files
```

### Weekly
```
1. Generate Family Assessment Summary
2. Export PDF for donor reports
3. Share with stakeholders
```

### Monthly
```
1. Generate comprehensive reports
2. Backup to external drive
3. Review data quality
4. Archive monthly backup
```

### Data Migration
```
1. Old system → Export to Excel
2. Excel imported into Kahatayn
3. Test data integrity
4. Full backup created
5. Manual backups archived monthly
```

---

## Technical Notes

### Portable .exe Advantages
- No installation needed
- Self-contained Python environment
- All dependencies included
- Works on air-gapped networks
- Easy USB/USB stick distribution

### Data File Locations
- **SQLite**: `data/orphanage.db`
- **Excel**: `data/orphanage_data.xlsx`
- **ODS**: `data/orphanage_data.ods`
- **Backups**: `data/backups/` (kept infinitely)
- **Reports**: `data/reports/`
- **Logs**: `logs/` (application logs)

### Backup Strategy
- **Automatic**: Every app close (all formats)
- **Manual**: Any time via Settings
- **External**: NPO can copy `data/backups/` to USB/cloud
- **Retention**: All backups kept indefinitely
- **Recovery**: 1-click restore from any backup

---

## Version Updates

When you release a new version:

1. **Test thoroughly** on Windows/Linux/Mac
2. **Update version** in main.py/config.py
3. **Create new build** using `run_build.bat`
4. **Give NPO new dist/ folder** (or just .exe)
5. **Old data persists** - they keep their `data/` folder

---

## Support

For issues:
1. Check logs in `logs/` folder
2. Review `FEATURES_GUIDE.md` for detailed feature docs
3. See `QUICKSTART.md` for user workflows
4. Contact developer with `logs/` folder contents

---

## File Checklist for Distribution

EXE Package should include:
- [ ] kahatayn.exe
- [ ] _internal/ folder
- [ ] data/ folder with initial files
- [ ] README.md (user documentation)
- [ ] QUICKSTART.md (quick start guide)
- [ ] FEATURES_GUIDE.md (feature documentation)

Optional:
- [ ] setup_guide.txt (this file, printed)
- [ ] backup_folder.zip (initial backup copy)
