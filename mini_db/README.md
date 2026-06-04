# Kahatayn - Orphan Family Management System

A lightweight desktop application for managing orphan families, volunteers, donors, and assessments. Built with Python, Tkinter UI, and multi-backend support (Excel/SQLite).

## Features

### Core Functionality
- **Family Case Management** - Track families, orphans, and guardians
- **Volunteer Management** - Manage volunteer profiles, assignments, and activity logs
- **Sponsorship Tracking** - Link volunteers/donors to orphans for financial/educational support
- **Financial Assessments** - Record family income, expenses, and support calculations
- **Document Management** - Store and track important documents (birth certificates, IDs, etc.)

### User Roles
#### Manager
- Full system access
- Create and manage all case records
- Assign volunteers to families
- Generate reports and analytics
- Manage system users
- Access settings and backups

#### Volunteer
- View assigned cases
- Update case status and notes
- Create assessments
- Log activities
- Limited to assigned families only

#### Staff
- Create and edit case records
- Data entry and management
- Generate reports
- Document management
- No volunteer assignment permissions

### Multi-Backend Support
- **Excel (Primary)** - NPO staff work directly with XLSX files
- **SQLite** - Optional relational database backend
- **ODS** - Open Document Spreadsheet support

## Installation

### Prerequisites
- Python 3.8+ (tested with Python 3.13)
- Windows/Linux/Mac

### Setup Steps

1. **Clone or download the project**
```bash
cd mini_db
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize database and create demo users**
```bash
python setup.py
```

This creates:
- Data directory with archive files
- Logs directory for application logs
- Demo user accounts (see credentials below)

## Usage

### Starting the Application

```bash
python main.py
```

The application will launch with a login window.

### Demo Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Manager | `manager` | `password123` |
| Volunteer | `volunteer` | `password123` |
| Staff | `staff` | `password123` |

## Project Structure

```
mini_db/
├── config.py              # Configuration, roles, paths
├── main.py                # Application entry point
├── setup.py               # Database initialization
├── requirements.txt       # Python dependencies
│
├── models/
│   ├── __init__.py
│   └── models.py          # SQLAlchemy ORM models (22 tables)
│
├── repo/
│   ├── __init__.py
│   ├── base.py            # Abstract base repository
│   ├── sqlite.py          # SQLite implementation
│   ├── xsls.py            # Excel (.xlsx) implementation
│   ├── ods.py             # ODS implementation
│   ├── files.py           # File-based repository factory
│   └── factory.py         # Repository factory (deprecated)
│
├── service/
│   ├── __init__.py
│   ├── auth.py            # Authentication and authorization
│   └── migration_service.py  # Schema migration
│
├── ui/
│   ├── __init__.py
│   ├── ui_main.py         # Main window and login
│   ├── components.py      # Reusable UI components
│   └── dashboards.py      # Role-specific dashboards
│
├── data/                  # Data files
│   └── orphanage_data.xlsx  # Main data (Excel backend)
│
└── logs/                  # Application logs
    └── app_YYYYMMDD.log
```

## Data Models

### Core Tables (23 entities)

**Master Data:**
- `cities` - City/location master
- `schools` - School directory
- `document_types` - Document classification

**Person Management:**
- `persons` - Core person records
- `contacts` - Contact information
- `system_users` - Login accounts

**Family & Orphan:**
- `families` - Family cases
- `representatives` - Family guardians/parents
- `orphans` - Orphan/vulnerable child records
- `assessments` - Financial assessments

**Volunteer & Sponsorship:**
- `volunteers` - Volunteer profiles
- `volunteer_activities` - Activity logs
- `sponsorships` - Volunteer-to-orphan relationships
- `donors` - Donor profiles

**Documents:**
- `documents` - Document tracking

## Configuration

Edit `config.py` to customize:

```python
# Storage backend selection
PRIMARY_BACKEND = 'excel'  # or 'sqlite'

# File paths
EXCEL_FILE_PATH = "data/orphanage_data.xlsx"
SQLITE_DB_PATH = "data/orphanage.db"

# UI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Color scheme and fonts
COLORS = {...}  # Customize UI colors
```

## API & Extension Points

### Custom Repository Implementation

Extend `BaseRepository` to support additional backends:

```python
from repo.base import BaseRepository

class MyRepository(BaseRepository):
    def add(self, entity):
        # Your implementation
        pass
    
    def get(self, entity_id, model_class):
        # Your implementation
        pass
```

### Authentication Extension

Use `AuthManager` for custom auth logic:

```python
from service.auth import AuthManager

auth = AuthManager(repository)
user = auth.authenticate('username', 'password')
auth.has_permission('view_all_cases')  # Permission check
```

## Key Design Patterns

1. **Repository Pattern** - Abstraction over data persistence
2. **Factory Pattern** - Repository creation based on backend type
3. **Role-Based Access Control** - Permission system integrated with auth
4. **Separation of Concerns** - Models (SQLAlchemy), Services, UI layers

## Database Schema

### Relationships

- `Family` → `Orphan` → `Sponsorship` → `Volunteer`
- `Family` → `Representative` ← `Person`
- `Orphan` → `Person` ← `Volunteer`
- `Person` → `Contact` (one-to-one)
- `Orphan` → `School`
- `Person` → `City`

### Audit Tracking

All core tables include:
- `created_at` - Timestamp
- `updated_at` - Modification timestamp
- System versioning via `SystemUser` tracking

## Logging

Logs are written to:
- Console (INFO level)
- `logs/app_YYYYMMDD.log` (file)

Configure in `config.py`:

```python
LOG_LEVEL = logging.INFO
LOG_FILE = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
```

## Troubleshooting

### Import Errors
```bash
# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

### Excel File Locked
Close the file in Excel/Calc before running the application.

### Database Corruption
Delete the `data` directory and rerun `setup.py` to reset:

```bash
rm -rf data
python setup.py
```

### Unicode/Encoding Issues
The application uses UTF-8 by default. Set environment:

```bash
set PYTHONIOENCODING=utf-8  # Windows
export PYTHONIOENCODING=utf-8  # Linux/Mac
```

## Future Enhancements

- [ ] Web/mobile interface
- [ ] PDF report generation
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Sync between multiple locations
- [ ] Multi-language support (Arabic, English)
- [ ] Backup/restore utilities
- [ ] Data validation rules engine

## Contributing

1. Create a feature branch
2. Make changes following the existing patterns
3. Test with setup.py and main.py
4. Document changes in README

## License

This project is built for Kahatayn orphan support services.

## Support

For questions or issues, contact the development team.

---

**Version:** 1.0.0  
**Last Updated:** June 4, 2026  
**Built With:** Python 3.13, SQLAlchemy 2.0, Tkinter
