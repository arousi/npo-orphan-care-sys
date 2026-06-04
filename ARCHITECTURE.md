# Architecture

The system has three layers that share the same data model but serve
different workflows.

```
┌─────────────────────────────────────────────────────────┐
│                    main.ods (25 sheets)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ input_       │  │ Persons,     │  │ City, Banks,   │ │
│  │ dashboards   │  │ Families,    │  │ document type, │ │
│  │ (9 forms)    │  │ Orphans, …   │  │ … (lookups)    │ │
│  └──────────────┘  └──────────────┘  └────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────────┐ ┌──────────┐ ┌──────────────┐
│  convert.py     │ │ mini_db  │ │ LibreOffice  │
│  (scanner)      │ │ (app)    │ │ macros       │
│                 │ │          │ │              │
│  Reads ODS via  │ │ Tkinter  │ │ 16 Python    │
│  pandas,        │ │ GUI      │ │ UNO macros   │
│  exports JSON   │ │ 3 roles  │ │ for CRUD     │
│  structure      │ │ PDF/backup│ │ via APSO     │
└─────────────────┘ └──────────┘ └──────────────┘
```

## Layer 1 — LibreOffice Workbook (`main.ods`)

The single source of truth. 25 sheets organized into three groups:

### Dashboard sheets (form UI)
- **input_dashboards** — 9 data-entry forms arranged in a grid:
  Register Person, Add Payment, Add Representative, Add Donor,
  Add Sponsorship, Add Document, Patch Donor, Patch Person,
  Add Assessment.
- **view_dashboards** — (reserved for read-only views)

Each form occupies a column group (A–D, E–H, J–M, O–R) with:
- **Row 1 / Row 16 / Row 22 / Row 38** — form header cell
  (e.g. "Register Person Form")
- **Rows below** — field labels in the first column of the group,
  input cells in the second column
- **Buttons** — shape objects assigned to macros via right-click
  → Assign Macro

### Entity sheets (data tables)
One sheet per entity: Persons, Employees, Families, Family_member,
Reps, Orphans, Donors, Deposits, Documents, Sponsorships,
Assessments, Payments, Banks, Bank Branches, Bank_account, Contact,
Audit, criteria.

Each has a header row (column names) followed by data rows.

### Reference sheets (lookup tables)
City, Schools, deposit type, document type, spons_type.
Small tables with ≤20 rows, used for dropdown values in forms.

## Layer 2 — Scanner (`convert.py`)

A pure-python batch tool that reads `main.ods` and writes the
`exports/` directory. No UI, no dependencies on LibreOffice.

### Pipeline

```
main.ods ──► pandas (odf engine) ──► per-sheet DataFrames
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            parse_spatial_forms   extract_table_data   detect_relationships
                    │                   │                   │
                    ▼                   ▼                   ▼
              forms.json          schema.json +        relationships.json
                                 data/*.json
```

### Design decisions

- **`header=None`** — reads raw cell positions without pandas interpreting
  headers. Allows the scanner to detect both form layouts (where row 1
  contains "Register Person Form") and data tables (where row 1 contains
  "id, first_name, …").
- **Form detection** uses `FORM_PREFIXES` (register, add, patch, …) combined
  with `endswith("form")` to avoid false positives on cells that happen to
  contain "form" as a substring.
- **Field walking** traverses downward from the form header, collecting
  non-empty cells as field labels. A gap of 10+ consecutive empty rows
  terminates the walk (configurable via `FORM_FIELD_EMPTY_GAP`).
- **Button scanning** searches all remaining cells below the form for text
  matching `BUTTON_KEYWORDS`. Because LibreOffice buttons are typically
  shape-assigned macros (not text cells), the scanner notes their absence
  rather than warning.
- **FK resolution** uses a hardcoded `FK_ALIASES` dict (e.g. `"rep" → "Reps"`)
  with a fallback pluralization heuristic. Columns in `FK_SKIP_PATTERNS`
  (`national_id`, `type_id`) are excluded from relationship detection.

## Layer 3 — Desktop App (`mini_db/`)

A full Tkinter application with SQLAlchemy ORM and multi-backend
persistence. See `mini_db/ARCHITECTURE.md` for details (or read the
source — `mini_db/repo/`, `mini_db/service/`, `mini_db/ui/`).

### Key architectural features

| Pattern | Implementation |
|---|---|
| Repository | `BaseRepository` → `SQLiteRepository`, `XLSXRepository`, `ODSRepository` |
| Service layer | `AuthManager`, `BackupService`, `DataExportService`, `PDFReportService`, `I18nService` |
| Role-based UI | `ManagerDashboard`, `VolunteerDashboard`, `StaffDashboard` |
| Auto-backup | On every app close, multi-format (SQLite + XLSX + ODS) |

### Data flow

```
User (Tkinter) ──► Dashboard ──► Service ──► Repository ──► File/DB
                                                              │
                                              ┌───────────────┴───────────────┐
                                              ▼                               ▼
                                        data/orphanage_data.xlsx      data/orphanage.db
                                        (primary — editable by NPO)   (optional SQLite)
```

## Layer 4 — LibreOffice Macros (`mini_db/kahatayn_macros.py`)

16 Python functions (7 create, 7 search, 2 update) deployed to
`%APPDATA%\LibreOffice\4\user\Scripts\python\` and assigned to buttons
on `input_dashboards`. Uses the UNO API via APSO.

### Architecture

```python
# Generic CRUD engine — one function for all entities
def create_record(form_config):
    values = _read_input_cells(form_config)
    values = _resolve_fk_fields(values)      # "Tripoli" → city_id=3
    _validate_constraints(values, entity)
    _validate_foreign_keys(values, entity)
    sid = _get_next_id(entity["sheet"])
    _write_record(sheet, sid, values)
    _audit_log(entity, sid, "CREATE", …)
```

### Config-driven design

Each entity has a config dict describing its sheet, fields, types,
foreign keys, constraints, and computed columns. Each form has a
separate config dict describing its cell positions. The engine code
never references specific entities or forms — it reads everything
from these dicts.

```
FORM_REGISTER_PERSON  ──references──►  ENTITY_PERSON
FORM_ADD_PAYMENT      ──references──►  ENTITY_DEPOSIT
…
```

## Data model

### Core relationships

```
Person ──1:1──► Contact
Person ──*:1──► City
Person ──1:1──► Bank_account
Person ──1:1──► Employee
Person ──1:1──► Representative
Person ──*:1──► Donor

Family ──1:1──► Representative
Family ──1:*──► Family_member ──*:1──► Person
Family ──1:*──► Orphan ──*:1──► Person
Family ──1:*──► Assessment

Orphan ──*:1──► School
Orphan ──*:1──► Sponsorship ──*:1──► Donor
Orphan ──*:1──► Representative

Sponsorship ──*:1──► Deposit
Deposit ──*:1──► Donor

Bank ──1:*──► Bank Branch
```

### Type discriminator columns

`type_id` appears in Deposits, Documents, and Sponsorships.
These reference separate lookup tables (deposit type, document type,
spons_type) rather than a unified type table.

## File storage

The `documents/` directory mirrors table names:

```
documents/
├── Persons/<person_id>/national_id.jpg
├── Orphans/<orphan_id>/medical_report.pdf
├── Sponsorships/<sponsorship_id>/agreement.pdf
…
```

The `Documents` table's `path` column stores relative paths like
`"Persons/42/national_id.jpg"`. The `DOCUMENT_ROOT` and `ENTITY_DIRS`
config dicts in `kahatayn_macros.py` map entity names to directory names.
