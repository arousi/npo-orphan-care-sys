# Quick Start Guide - Kahatayn System

## Getting Started in 3 Steps

### Step 1: Install
```bash
pip install -r requirements.txt
python setup.py
```

### Step 2: Run
```bash
python main.py
```

### Step 3: Login
Use one of the demo accounts:
- **Manager**: `manager` / `password123`
- **Volunteer**: `volunteer` / `password123`  
- **Staff**: `staff` / `password123`

---

## Using the System

### Manager: Full Access
1. **Cases Tab** - Create and manage family cases
   - View all families
   - Create new case
   - Assign to volunteers
   - Update status

2. **Volunteers Tab** - Manage volunteer team
   - Add volunteers
   - Track activity
   - Assign sponsorships

3. **Reports Tab** - Analytics and reporting
   - Family assessment summary
   - Volunteer activity reports
   - Financial overview
   - Sponsorship status

4. **Settings Tab** - System administration
   - Backup data
   - Manage users
   - System configuration

### Volunteer: Limited Access
1. **My Assignments** - View assigned families
   - See family details
   - Track orphans under care
   - View last updates

2. **Activity Log** - Record activities
   - Log visits
   - Submit assessments
   - Record calls/communications

### Staff: Data Entry
1. **Data Entry** - Quick data input
   - Create new families
   - Update assessments
   - Add documents
   - Record activities

2. **Reports** - Daily reporting
   - Track entries made
   - Report completion status

---

## Common Tasks

### Create a New Family Case
1. Go to **Manager** → **Cases**
2. Click **+ New Case**
3. Fill in family details:
   - Family code (auto-generated)
   - Guardian information
   - Number of children
4. Click **Save**

### Assign a Volunteer
1. Select family from cases list
2. Click **Edit**
3. From volunteers dropdown, select volunteer
4. Click **Assign**

### Record Family Assessment
1. Staff/Volunteer → Enter case
2. Go to **Assessment** section
3. Enter:
   - Income sources
   - Expenses
   - Government support
4. Click **Calculate** (auto-calculates sums)
5. Click **Save**

### Log Volunteer Activity
1. Volunteer is logged in
2. Click **Activity Log**
3. Select activity type
   - Visit
   - Assessment
   - Report
   - Call
   - Other
4. Add description and date
5. Click **Save Activity**

### Generate Report
1. Manager → **Reports**
2. Select report type:
   - Family Assessment Summary
   - Volunteer Activity Report
   - Financial Overview
   - Sponsorship Status
3. Click to generate
4. View or export as needed

---

## Data Storage

### Default: Excel File
- File: `data/orphanage_data.xlsx`
- NPO staff can open directly in Excel/LibreOffice
- Automatically synced when app saves

### Alternative: SQLite Database
Edit `config.py` to switch:
```python
PRIMARY_BACKEND = 'sqlite'  # Instead of 'excel'
```

---

## Important Notes

✓ **Multi-user Safe** - Each user role has limited access  
✓ **Live Data** - Excel file is updated in real-time  
✓ **No Internet** - Works completely offline  
✓ **Lightweight** - Minimal system requirements  
✓ **Backup** - Check `logs/` for activity logs  

⚠️ **Keep Excel Closed** - Don't edit orphanage_data.xlsx while app is running  
⚠️ **Change Passwords** - Update demo passwords before production use  
⚠️ **Regular Backups** - Copy `data/` folder regularly  

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Login | Enter (from password field) |
| Logout | Click Logout button |
| Search | Type in search box (real-time filter) |
| Refresh | Close and reopen tab |

---

## Troubleshooting

**Q: Application won't start**  
A: Run `pip install -r requirements.txt` again, then `python main.py`

**Q: Excel file says "access denied"**  
A: Close Excel/Calc and restart the app

**Q: Demo users not working**  
A: Delete `data/` folder, rerun `python setup.py`

**Q: Can't see saved data**  
A: Check `data/orphanage_data.xlsx` - file should have data sheets

**Q: Need to change a password**  
A: Edit `setup.py` and rerun, OR delete user from Excel manually

---

## Technical Stack

- **Language**: Python 3.13
- **UI**: Tkinter (built-in, no extra installation)
- **Database**: SQLAlchemy ORM  
- **Data**: Excel (openpyxl), SQLite, ODS
- **Storage**: File-based, multi-backend support

---

## Support

For issues or questions:
1. Check the logs in `logs/app_YYYYMMDD.log`
2. Review `README.md` for detailed documentation
3. Check code comments in source files
4. Reset database: Delete `data/` folder and rerun setup

---

**Version**: 1.0.0  
**Last Update**: June 4, 2026  
**Organization**: Kahatayn Orphan Support
