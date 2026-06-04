import uno
import traceback
from com.sun.star.beans import PropertyValue
# instructions:
"""
The most important fixes before production are:

Fix FK resolution order.
Implement real audit logging (field, old value, new value).
Add rollback for multi-record operations.
Cache FK lookups.
Move computed fields (like income totals) into business logic instead of manual entry.

Foreign Key Resolution Has A Design Bug

You have:

ENTITY_PERSON = {
    "foreign_keys": {
        "city": {
            "ref_sheet":"City",
            "ref_header":"name",
            "target_header":"city_id"
        }
    }
}

Then:

_validate_foreign_keys()

runs before:

_resolve_fk_fields()

Problem:

User enters:

Tripoli

Validation runs.

Validation searches:

id == Tripoli

Fails.

Then resolution never happens.

The order should be:

values = _resolve_fk_fields()

_validate()

_validate_foreign_keys()

not the reverse.

This is probably the biggest actual bug in the current system.
Audit Log Isn't Really An Audit Log Yet

You write:

_audit_log(
    entity,
    sid,
    "UPDATE",
    form_field,
    old_val,
    new_val
)

but inside:

_audit_log()

you ignore:

field
old_value
new_value

Completely.

You only save:

created_at
table_name
action
record_id

Meaning:

Person 55 updated

is logged

but

What changed?

is not logged.

That defeats the purpose.

I would add:

timestamp
table_name
record_id
field
old_value
new_value
user
Validation Engine Needs Rules

Currently:

required
int
float

only.

Eventually you'll need:

"max_length": 100

"min_value": 0

"regex": r"^\d+$"

"choices": [
   "Orphan",
   "Donor",
   "Representative"
]

Example:

"national_id": {
    "type":"text",
    "length":12
}
Transactions Are Missing

This is the most dangerous issue.

Example:

register_person()

creates:

Person

then

Orphan

What if:

Person inserted

and

Orphan insert fails

?

You get:

Person exists
Orphan missing

Data corruption.

You need a rollback mechanism.

Example:

try:
    create person
    create orphan
except:
    delete created person

Spreadsheet databases don't give you transactions automatically.

You must simulate them.
Performance Problem Still Exists

You improved ID lookup.

Excellent.

But FK validation still does:

while True:

over entire sheets.

Every time.

Example:

_validate_foreign_keys()

is still O(n).

You need:

FK_INDEX_CACHE

similar to:

_ID_INDEX_CACHE.
Missing Computed Fields

Assessment contains:

salary
side_income

gov_support_daman

gov_support_tadamun

gov_support_child

rent

total_income

net_income

Users should never enter:

total_income
net_income

manually.

Those should be computed.

Example:

total_income =
salary
+ side_income
+ daman
+ tadamun
+ child_support

net_income =
total_income - rent

The system should calculate it.
"""
# ============================================================
# CONFIGURATION LAYER
# ============================================================
# ENTITY CONFIGS (data schema, not UI)
# ============================================================

# Document storage — folders mirror DB table names
DOCUMENT_ROOT = "documents"
ENTITY_DIRS = {
    "person": "Persons",
    "employee": "Employees",
    "family": "Families",
    "family_member": "Family_Members",
    "representative": "Representatives",
    "orphan": "Orphans",
    "donor": "Donors",
    "deposit": "Deposits",
    "payment": "Payments",
    "sponsorship": "Sponsorships",
    "assessment": "Assessments",
    "bank": "Banks",
    "bank_branch": "Bank_Branches",
    "bank_account": "Bank_Accounts",
    "contact": "Contacts",
    "school": "Schools",
    "document_type": "Document_Types",
    "deposit_type": "Deposit_Types",
    "sponsorship_type": "Sponsorship_Types",
    "criteria": "Criteria",
}

ENTITY_PERSON = {
    "sheet": "Persons",
    "required": ["first_name", "last_name"],
    "field_types": {
        "first_name": "text", "middle_name": "text", "last_name": "text",
        "birth_date": "date", "national_id": "text", "city": "text",
    },
    "constraints": {
        "national_id": {"max_length": 20, "regex": r"^\d*$"},
    },
    "foreign_keys": {
        "city": {"ref_sheet": "City", "ref_header": "name", "target_header": "city_id"},
    },
    "field_map": {
        "first_name": "first_name", "middle_name": "middle_name",
        "last_name": "last_name", "birth_date": "birth_date",
        "national_id": "national_id", "city": "city_id",
    },
}

ENTITY_ORPHAN = {
    "sheet": "Orphans",
    "required": [],
    "field_types": {"person_id": "int"},
    "foreign_keys": {
        "person_id": {"ref_sheet": "Persons", "ref_header": "id", "target_header": "person_id"},
    },
    "field_map": {"person_id": "person_id"},
}

ENTITY_DEPOSIT = {
    "sheet": "Deposits",
    "required": ["donor_id", "amount"],
    "field_types": {"donor_id": "int", "amount": "float", "type_id": "int"},
    "constraints": {"amount": {"min_value": 0}},
    "foreign_keys": {
        "donor_id": {"ref_sheet": "Donors", "ref_header": "id", "target_header": "donor_id"},
        "type_id": {"ref_sheet": "deposit type", "ref_header": "id", "target_header": "type_id"},
    },
    "field_map": {
        "donor_id": "donor_id", "amount": "amount",
        "currency": "currency", "date_deposited": "date_deposited",
        "type_id": "type_id", "reference": "reference",
    },
}

ENTITY_REP = {
    "sheet": "Reps",
    "required": ["person_id", "family_id"],
    "field_types": {"person_id": "int", "family_id": "int"},
    "foreign_keys": {
        "person_id": {"ref_sheet": "Persons", "ref_header": "id", "target_header": "person_id"},
        "family_id": {"ref_sheet": "Families", "ref_header": "id", "target_header": "family_id"},
    },
    "field_map": {"person_id": "person_id", "family_id": "family_id"},
}

ENTITY_FAMILY_MEMBER = {
    "sheet": "Family_member",
    "required": ["family_id", "person_id"],
    "field_types": {"family_id": "int", "person_id": "int"},
    "foreign_keys": {
        "family_id": {"ref_sheet": "Families", "ref_header": "id", "target_header": "family_id"},
        "person_id": {"ref_sheet": "Persons", "ref_header": "id", "target_header": "person_id"},
    },
    "field_map": {"family_id": "family_id", "person_id": "person_id"},
}

ENTITY_DONOR = {
    "sheet": "Donors",
    "required": ["person_id"],
    "field_types": {"person_id": "int"},
    "foreign_keys": {
        "person_id": {"ref_sheet": "Persons", "ref_header": "id", "target_header": "person_id"},
    },
    "field_map": {"person_id": "person_id"},
}

ENTITY_SPONSORSHIP = {
    "sheet": "Sponsorships",
    "required": ["orphan_id"],
    "field_types": {"orphan_id": "int", "family_id": "int", "type_id": "int", "deposit_id": "int"},
    "constraints": {"type_id": {"min_value": 1}},
    "foreign_keys": {
        "orphan_id": {"ref_sheet": "Orphans", "ref_header": "id", "target_header": "orphan_id"},
        "family_id": {"ref_sheet": "Families", "ref_header": "id", "target_header": "family_id"},
        "deposit_id": {"ref_sheet": "Deposits", "ref_header": "id", "target_header": "deposit_id"},
    },
    "field_map": {
        "orphan_id": "orphan_id", "family_id": "family_id",
        "start_date": "start_date", "end_date": "end_date",
        "type_id": "type_id", "deposit_id": "deposit_id",
    },
}

ENTITY_DOCUMENT = {
    "sheet": "Documents",
    "required": [],
    "field_types": {"type_id": "int"},
    "foreign_keys": {
        "type_id": {"ref_sheet": "document type", "ref_header": "id", "target_header": "type_id"},
    },
    "field_map": {"type_id": "type_id"},
}

ENTITY_ASSESSMENT = {
    "sheet": "Assessments",
    "required": ["family_id"],
    "field_types": {
        "family_id": "int", "rep_id": "int",
        "salary": "float", "side_income": "float",
        "gov_support_daman": "float", "gov_support_tadamun": "float",
        "gov_support_child": "float", "rent": "float",
        "total_income": "float", "net_income": "float",
    },
    "constraints": {
        "salary": {"min_value": 0},
        "rent": {"min_value": 0},
        "net_income": {"min_value": 0},
    },
    "computed": {
        "total_income": {
            "op": "sum",
            "fields": ["salary", "side_income", "gov_support_daman",
                       "gov_support_tadamun", "gov_support_child"],
        },
        "net_income": {
            "op": "sub",
            "from": "total_income",
            "minus": "rent",
        },
    },
    "foreign_keys": {
        "family_id": {"ref_sheet": "Families", "ref_header": "id", "target_header": "family_id"},
        "rep_id": {"ref_sheet": "Reps", "ref_header": "id", "target_header": "rep_id"},
    },
    "field_map": {
        "family_id": "family_id", "rep_id": "rep_id",
        "date": "date", "salary": "salary",
        "side_income": "side_income", "gov_support_daman": "gov_support_daman",
        "gov_support_tadamun": "gov_support_tadamun", "gov_support_child": "gov_support_child",
        "rent": "rent", "total_income": "total_income", "net_income": "net_income",
    },
}

# ============================================================
# UI FORM CONFIGS (position + entity link)
# ============================================================

FORM_REGISTER_PERSON = {
    "entity": ENTITY_PERSON,
    "sheet": "input_dashboards",
    "label_col": 0, "input_col": 1,
    "rows": range(2, 14),
    "fields": [
        "first_name", "middle_name", "last_name", "national_id",
        "city", "type", "family_paper_number", "birth_date",
        "bank_account_id", "bank_account_iban", "bank_id", "branch",
    ],
    "search_field": "id",
    "sub_creates": [
        {
            "trigger_field": "type",
            "trigger_value": "Orphan",
            "entity": ENTITY_ORPHAN,
            "link_field": "person_id",
            "use_created_id": True,
        },
    ],
}

FORM_PATCH_PERSON = {
    "entity": ENTITY_PERSON,
    "sheet": "input_dashboards",
    "label_col": 0, "input_col": 1,
    "rows": range(23, 31),
    "fields": [
        "id", "first_name", "middle_name", "last_name",
        "national_id", "city", "type", "family_paper_number", "birth_date",
    ],
    "search_field": "id",
}

FORM_ADD_PAYMENT = {
    "entity": ENTITY_DEPOSIT,
    "sheet": "input_dashboards",
    "label_col": 4, "input_col": 5,
    "rows": range(2, 9),
    "fields": ["id", "donor_id", "amount", "currency", "date_deposited", "type_id", "reference"],
    "search_field": "id",
}

FORM_ADD_REPRESENTATIVE = {
    "entity": ENTITY_REP,
    "sheet": "input_dashboards",
    "label_col": 9, "input_col": 10,
    "rows": range(2, 5),
    "fields": ["id", "person_id", "family_id"],
    "search_field": "id",
    "multi_targets": [ENTITY_FAMILY_MEMBER],
}

FORM_ADD_DONOR = {
    "entity": ENTITY_DONOR,
    "sheet": "input_dashboards",
    "label_col": 14, "input_col": 15,
    "rows": range(2, 10),
    "fields": ["id", "person_id", "family_id", "school_id", "health", "is_adult", "rep_id", "sponsorhip_id"],
    "search_field": "id",
}

FORM_PATCH_DONOR = {
    "entity": ENTITY_DONOR,
    "sheet": "input_dashboards",
    "label_col": 14, "input_col": 15,
    "rows": range(17, 25),
    "fields": ["id", "field1", "field2", "field3", "field4", "field5", "field6", "field7"],
    "search_field": "id",
}

FORM_ADD_SPONSORSHIP = {
    "entity": ENTITY_SPONSORSHIP,
    "sheet": "input_dashboards",
    "label_col": 4, "input_col": 5,
    "rows": range(18, 27),
    "fields": ["id", "orphan_id", "family_id", "type_id", "amount", "start_date", "end_date", "method", "deposit_id"],
    "search_field": "id",
}

FORM_ADD_DOCUMENT = {
    "entity": ENTITY_DOCUMENT,
    "sheet": "input_dashboards",
    "label_col": 9, "input_col": 10,
    "rows": range(17, 20),
    "fields": ["id", "type_id"],
    "search_field": "id",
}

FORM_ADD_ASSESSMENT = {
    "entity": ENTITY_ASSESSMENT,
    "sheet": "input_dashboards",
    "label_col": 0, "input_col": 1,
    "rows": range(39, 51),
    "fields": [
        "id", "family_id", "date", "salary", "side_income",
        "gov_support_daman", "gov_support_tadamun", "gov_support_child",
        "rent", "total_income", "net_income", "rep_id",
    ],
    "search_field": "id",
}

# ============================================================
# HELPERS: LOW-LEVEL UNO
# ============================================================

_ID_INDEX_CACHE = {}

def _get_doc():
    return XSCRIPTCONTEXT.getDocument()

def _get_sheet(doc, name):
    try:
        return doc.Sheets.getByName(name)
    except Exception:
        raise Exception(f'Sheet "{name}" not found')

def _cell(sheet, col, row):
    return sheet.getCellByPosition(col, row)

def _read_cell(sheet, col, row):
    cell = _cell(sheet, col, row)
    t = cell.Type
    if t == 2:
        return cell.String.strip()
    if t == 1:
        v = cell.Value
        return str(int(v)) if v == int(v) else str(v)
    return ""

def _write_cell(sheet, col, row, value):
    cell = _cell(sheet, col, row)
    if value is None:
        value = ""
    if isinstance(value, (int, float)):
        cell.Value = value
    else:
        cell.String = str(value)

def _msgbox(text):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    mb = toolkit.createMessageBox(None, ctx, None, "infobox", 1, "Kahatayn Macro", str(text)[:2000])
    mb.execute()

# ============================================================
# HELPERS: LOGGING
# ============================================================

_LOG_SHEET = "Log"

_LOG_LEVELS = {
    "DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3,
}

_USER_ERRORS = {
    "com.sun.star.uno.RuntimeException": "A system error occurred. Try reopening the file.",
    "com.sun.star.table.CellValueType": "A cell type mismatch was detected.",
    "KeyError": "A requested sheet or column was not found.",
    "AttributeError": "An unexpected attribute error occurred.",
    "TypeError": "A value had an unexpected type.",
}

def _ensure_log_sheet():
    doc = _get_doc()
    try:
        return doc.Sheets.getByName(_LOG_SHEET)
    except Exception:
        try:
            sheet = doc.createInstance("com.sun.star.sheet.Spreadsheet")
            sheet.setName(_LOG_SHEET)
            doc.Sheets.insertByName(_LOG_SHEET, sheet)
        except Exception:
            sheet = doc.Sheets.insertNewByName(_LOG_SHEET, 0)
        _write_cell(sheet, 0, 0, "timestamp")
        _write_cell(sheet, 1, 0, "level")
        _write_cell(sheet, 2, 0, "source")
        _write_cell(sheet, 3, 0, "message")
        _write_cell(sheet, 4, 0, "details")
        return sheet

def _log_entry(level, source, message, details=""):
    try:
        sheet = _ensure_log_sheet()
        row = 1
        while True:
            c = _cell(sheet, 0, row)
            if c.Type == 0:
                break
            row += 1
        import datetime
        _write_cell(sheet, 0, row, str(datetime.datetime.now()))
        _write_cell(sheet, 1, row, level)
        _write_cell(sheet, 2, row, str(source)[:40])
        _write_cell(sheet, 3, row, str(message)[:300])
        _write_cell(sheet, 4, row, str(details)[:1000])
    except Exception as log_err:
        pass  # don't crash when logging fails

def _log_info(source, message, details=""):
    _log_entry("INFO", source, message, details)

def _log_warn(source, message, details=""):
    _log_entry("WARN", source, message, details)

def _log_error(source, message, details=""):
    _log_entry("ERROR", source, message, details)

def _user_friendly_error(exc):
    """Return a user-friendly message for a given exception."""
    exc_type = type(exc).__name__
    msg = _USER_ERRORS.get(exc_type)
    if msg:
        return f"{msg}\n\nDetails: {exc}"
    msg = str(exc)
    return msg[:300]

# ============================================================
# HELPERS: DYNAMIC COLUMN MAPPING
# ============================================================

def _get_header_map(sheet):
    """Read header row (row 0) and return {header_name: column_index}."""
    hmap = {}
    col = 0
    while True:
        c = _cell(sheet, col, 0)
        t = c.Type
        if t == 0:
            break
        if t == 2 and c.String.strip():
            hmap[c.String.strip()] = col
        col += 1
    return hmap

def _resolve_col_map(entity):
    """Convert entity field_map (name -> name) to (name -> col_index) using live headers."""
    doc = _get_doc()
    sheet = _get_sheet(doc, entity["sheet"])
    hmap = _get_header_map(sheet)
    resolved = {}
    for form_field, header_name in entity["field_map"].items():
        if header_name in hmap:
            resolved[form_field] = hmap[header_name]
    return resolved

# ============================================================
# HELPERS: DATA TABLE ACCESS
# ============================================================

def _rebuild_index(entity):
    key = entity["sheet"]
    doc = _get_doc()
    sheet = _get_sheet(doc, entity["sheet"])
    hmap = _get_header_map(sheet)
    id_col = hmap.get("id", 0)
    idx = {}
    row = 1
    while True:
        c = _cell(sheet, id_col, row)
        if c.Type == 0:
            break
        if c.Type == 1:
            idx[str(int(c.Value))] = row
        elif c.Type == 2 and c.String.strip():
            idx[c.String.strip()] = row
        row += 1
    _ID_INDEX_CACHE[key] = idx
    return idx

def _invalidate_index(entity):
    _ID_INDEX_CACHE.pop(entity["sheet"], None)

def _find_row_by_id(entity, value):
    key = entity["sheet"]
    sval = str(value).strip()
    if not sval:
        return -1
    idx = _ID_INDEX_CACHE.get(key)
    if idx is not None:
        return idx.get(sval, -1)
    idx = _rebuild_index(entity)
    return idx.get(sval, -1)

def _find_in_ref_sheet(fk_config, value):
    """Check if a value exists in a reference sheet, using cached index.
    Returns True if found, False otherwise.
    For name-based lookups, also returns the resolved ID.
    """
    sval = str(value).strip()
    if not sval:
        return False, ""
    doc = _get_doc()
    sheet = _get_sheet(doc, fk_config["ref_sheet"])
    hmap = _get_header_map(sheet)
    ref_col = hmap.get(fk_config["ref_header"], -1)
    if ref_col < 0:
        return False, ""
    id_col = hmap.get("id", 0)
    cache_key = fk_config["ref_sheet"]
    idx = _ID_INDEX_CACHE.get(cache_key)
    if idx is None:
        idx = {}
        row = 1
        while True:
            c = _cell(sheet, id_col, row)
            if c.Type == 0:
                break
            if c.Type == 1:
                rid = str(int(c.Value))
                name_cell = _cell(sheet, ref_col, row)
                if name_cell.Type == 2 and name_cell.String.strip():
                    idx[name_cell.String.strip().lower()] = rid
                idx[rid] = rid
            elif c.Type == 2 and c.String.strip():
                raw = c.String.strip()
                name_cell = _cell(sheet, ref_col, row)
                if name_cell.Type == 2 and name_cell.String.strip():
                    idx[name_cell.String.strip().lower()] = raw
                idx[raw] = raw
            row += 1
        _ID_INDEX_CACHE[cache_key] = idx
    if sval.lower() in idx:
        return True, idx[sval.lower()]
    if sval in idx:
        return True, idx[sval]
    return False, ""

def _get_next_id(entity):
    doc = _get_doc()
    sheet = _get_sheet(doc, entity["sheet"])
    hmap = _get_header_map(sheet)
    id_col = hmap.get("id", 0)
    row = 1
    while True:
        c = _cell(sheet, id_col, row)
        if c.Type == 0:
            break
        row += 1
    if row == 1:
        return 1
    return int(_cell(sheet, id_col, row - 1).Value) + 1

def _get_next_row(entity):
    doc = _get_doc()
    sheet = _get_sheet(doc, entity["sheet"])
    hmap = _get_header_map(sheet)
    id_col = hmap.get("id", 0)
    row = 1
    while True:
        c = _cell(sheet, id_col, row)
        if c.Type == 0:
            return row
        row += 1

# ============================================================
# HELPERS: VALIDATION
# ============================================================

def _validate(entity, values):
    """Check required fields and field types. Return error string or None."""
    for field in entity.get("required", []):
        if not values.get(field, "").strip():
            return f"'{field}' is required"
    ftypes = entity.get("field_types", {})
    for field, ftype in ftypes.items():
        val = values.get(field, "").strip()
        if not val:
            continue
        if ftype == "int":
            try:
                int(val)
            except ValueError:
                return f"'{field}' must be a whole number (got '{val}')"
        elif ftype == "float":
            try:
                float(val)
            except ValueError:
                return f"'{field}' must be a number (got '{val}')"
    return None

def _validate_constraints(entity, values):
    """Check extended constraints: max_length, min_value, regex, choices."""
    for field, rules in entity.get("constraints", {}).items():
        val = values.get(field, "").strip()
        if not val:
            continue
        if "max_length" in rules and len(val) > rules["max_length"]:
            return f"'{field}' exceeds max length ({rules['max_length']})"
        if "min_value" in rules:
            try:
                if float(val) < rules["min_value"]:
                    return f"'{field}' must be >= {rules['min_value']} (got {val})"
            except ValueError:
                return f"'{field}' must be a number for min_value check"
        if "max_value" in rules:
            try:
                if float(val) > rules["max_value"]:
                    return f"'{field}' must be <= {rules['max_value']} (got {val})"
            except ValueError:
                return f"'{field}' must be a number for max_value check"
        if "regex" in rules:
            import re
            if not re.match(rules["regex"], val):
                return f"'{field}' format is invalid (got '{val}')"
        if "choices" in rules:
            if val.lower() not in [c.lower() for c in rules["choices"]]:
                return f"'{field}' must be one of: {rules['choices']} (got '{val}')"
    return None

def _validate_foreign_keys(entity, values):
    """Check FK fields reference existing records (uses cached index)."""
    for field, fk in entity.get("foreign_keys", {}).items():
        val = values.get(field, "").strip()
        if not val:
            continue
        found, _ = _find_in_ref_sheet(fk, val)
        if not found:
            return f"'{field}' = {val} not found in {fk['ref_sheet']}"
    return None

# ============================================================
# HELPERS: FOREIGN KEY RESOLUTION (name -> ID)
# ============================================================

def _resolve_fk_fields(entity, values):
    """Replace text values (e.g. city name) with IDs for FK fields (uses cached index)."""
    resolved = dict(values)
    for field, fk in entity.get("foreign_keys", {}).items():
        val = resolved.get(field, "").strip()
        if not val:
            continue
        try:
            int(val)
            continue
        except ValueError:
            pass
        found, rid = _find_in_ref_sheet(fk, val)
        if found and rid:
            resolved[field] = rid
    return resolved

# ============================================================
# HELPERS: COMPUTED FIELDS
# ============================================================

def _compute_fields(entity, values):
    """Compute derived fields (e.g. total_income, net_income) from raw form values."""
    computed = entity.get("computed", {})
    if not computed:
        return values
    result = dict(values)
    for field, formula in computed.items():
        op = formula.get("op", "")
        if op == "sum":
            total = 0.0
            for src in formula.get("fields", []):
                try:
                    total += float(result.get(src, 0) or 0)
                except (ValueError, TypeError):
                    pass
            result[field] = str(total)
        elif op == "sub":
            try:
                a = float(result.get(formula.get("from", ""), 0) or 0)
                b = float(result.get(formula.get("minus", ""), 0) or 0)
                result[field] = str(max(0, a - b))
            except (ValueError, TypeError):
                result[field] = "0"
    return result

# ============================================================
# HELPERS: ROLLBACK
# ============================================================

_ROLLBACK_LOG = []

def _track_rollback(entity, record_id):
    """Record a created record so it can be undone on failure."""
    _ROLLBACK_LOG.append((entity["sheet"], record_id))

def _undo_rollback():
    """Clear all tracked records in reverse order."""
    doc = _get_doc()
    for sheet_name, rid in reversed(_ROLLBACK_LOG):
        try:
            sheet = _get_sheet(doc, sheet_name)
            hmap = _get_header_map(sheet)
            id_col = hmap.get("id", 0)
            row = 1
            while True:
                c = _cell(sheet, id_col, row)
                if c.Type == 0:
                    break
                if c.Type == 1 and str(int(c.Value)) == str(rid):
                    for col in range(20):
                        _cell(sheet, col, row).String = ""
                    _cell(sheet, id_col, row).String = ""
                    break
                row += 1
            _invalidate_index({"sheet": sheet_name})
        except Exception:
            pass
    _ROLLBACK_LOG.clear()

# ============================================================
# HELPERS: AUDIT LOG
# ============================================================

def _audit_log(entity, record_id, action, field, old_value, new_value):
    """Append a row to the Audit sheet with full field-level detail."""
    doc = _get_doc()
    try:
        sheet = _get_sheet(doc, "Audit")
    except Exception:
        return
    import datetime
    row = _get_next_row({"sheet": "Audit"})
    hmap = _get_header_map(sheet)
    missing_cols = []
    for needed in ["created_at", "table_name", "action", "record_id", "field", "old_value", "new_value"]:
        if needed not in hmap:
            missing_cols.append(needed)
    if missing_cols:
        next_col = len(hmap)
        for needed in missing_cols:
            _write_cell(sheet, next_col, 0, needed)
            hmap[needed] = next_col
            next_col += 1
    cols = {
        "created_at": str(datetime.datetime.now()),
        "table_name": entity["sheet"],
        "action": action,
        "record_id": str(record_id),
        "field": str(field) if field else "",
        "old_value": str(old_value)[:300] if old_value else "",
        "new_value": str(new_value)[:300] if new_value else "",
    }
    for hname, col in hmap.items():
        if hname in cols:
            _write_cell(sheet, col, row, cols[hname])

# ============================================================
# HELPERS: FORM I/O
# ============================================================

def _read_form(config):
    doc = _get_doc()
    sheet = _get_sheet(doc, config["sheet"])
    ic = config["input_col"]
    values = {}
    for i, r in enumerate(config["rows"]):
        if i < len(config["fields"]):
            values[config["fields"][i]] = _read_cell(sheet, ic, r - 1)
    return values

def _clear_form(config, keep_fields=frozenset({"id"})):
    doc = _get_doc()
    sheet = _get_sheet(doc, config["sheet"])
    ic = config["input_col"]
    for i, r in enumerate(config["rows"]):
        if i < len(config["fields"]):
            fname = config["fields"][i]
            if fname not in keep_fields:
                _write_cell(sheet, ic, r - 1, "")

def _populate_form(config, data):
    doc = _get_doc()
    sheet = _get_sheet(doc, config["sheet"])
    ic = config["input_col"]
    for i, r in enumerate(config["rows"]):
        if i < len(config["fields"]):
            fname = config["fields"][i]
            if fname in data:
                _write_cell(sheet, ic, r - 1, data[fname])

# ============================================================
# GENERIC CRUD ENGINE
# ============================================================

def create_record(config):
    entity = config["entity"]
    values = _read_form(config)

    err = _validate(entity, values)
    if err:
        _log_warn("create_record", f"Validation failed: {err}", str(values))
        _msgbox(f"Validation error: {err}")
        return

    values = _resolve_fk_fields(entity, values)

    values = _compute_fields(entity, values)

    err = _validate_foreign_keys(entity, values)
    if err:
        _log_warn("create_record", f"FK check failed: {err}", str(values))
        _msgbox(f"FK error: {err}")
        return

    err = _validate_constraints(entity, values)
    if err:
        _log_warn("create_record", f"Constraint failed: {err}", str(values))
        _msgbox(f"Constraint error: {err}")
        return

    _ROLLBACK_LOG.clear()

    resolved_col_map = _resolve_col_map(entity)
    row_data = {}
    for form_field, target_col in resolved_col_map.items():
        if form_field in values and values[form_field]:
            row_data[target_col] = values[form_field]

    try:
        pid = _append_data_row(entity, row_data)
        _track_rollback(entity, pid)
        _audit_log(entity, pid, "CREATE", "", "", str(values))
        _log_info("create_record", f"Created {entity['sheet']} ID={pid}", str(values))

        for sub in config.get("sub_creates", []):
            tf = sub["trigger_field"]
            if values.get(tf, "").strip().lower() == sub["trigger_value"].strip().lower():
                sub_entity = sub["entity"]
                sub_vals = {}
                if sub.get("use_created_id") and sub.get("link_field"):
                    sub_vals[sub["link_field"]] = pid
                sub_row_data = {}
                sub_resolved = _resolve_col_map(sub_entity)
                for ff, tc in sub_resolved.items():
                    if ff in sub_vals and sub_vals[ff] is not None:
                        sub_row_data[tc] = sub_vals[ff]
                sub_id = _append_data_row(sub_entity, sub_row_data)
                _track_rollback(sub_entity, sub_id)
                _audit_log(sub_entity, sub_id, "CREATE", "", "", str(sub_vals))
                _log_info("create_record", f"Sub-create {sub_entity['sheet']} ID={sub_id} (parent={pid})")

        for extra in config.get("multi_targets", []):
            extra_resolved = _resolve_col_map(extra)
            extra_row_data = {}
            for ff, tc in extra_resolved.items():
                if ff in values and values[ff]:
                    extra_row_data[tc] = values[ff]
            eid = _append_data_row(extra, extra_row_data)
            _track_rollback(extra, eid)
            _audit_log(extra, eid, "CREATE", "", "", str(extra_row_data))
            _log_info("create_record", f"Extra create {extra['sheet']} ID={eid} (parent={pid})")

    except Exception as exc:
        _log_error("create_record", f"Rolling back after failure: {exc}", traceback.format_exc())
        _undo_rollback()
        raise

    _clear_form(config)
    _msgbox(f"Record created in {entity['sheet']} with ID: {pid}")
    return pid

def _append_data_row(entity, col_value_map):
    doc = _get_doc()
    sheet = _get_sheet(doc, entity["sheet"])
    new_id = _get_next_id(entity)
    row = _get_next_row(entity)
    hmap = _get_header_map(sheet)
    id_col = hmap.get("id", 0)
    _write_cell(sheet, id_col, row, new_id)
    for col_idx, val in col_value_map.items():
        _write_cell(sheet, col_idx, row, val)
    _invalidate_index(entity)
    return new_id

def update_record(config):
    entity = config["entity"]
    values = _read_form(config)
    sid = values.get("id", "").strip()
    if not sid:
        _log_warn("update_record", "No ID provided", str(values))
        _msgbox(f"Enter a value in 'id' to update")
        return

    err = _validate(entity, values)
    if err:
        _log_warn("update_record", f"Validation failed: {err}", str(values))
        _msgbox(f"Validation error: {err}")
        return

    values = _resolve_fk_fields(entity, values)

    values = _compute_fields(entity, values)

    err = _validate_foreign_keys(entity, values)
    if err:
        _log_warn("update_record", f"FK check failed: {err}", str(values))
        _msgbox(f"FK error: {err}")
        return

    err = _validate_constraints(entity, values)
    if err:
        _log_warn("update_record", f"Constraint failed: {err}", str(values))
        _msgbox(f"Constraint error: {err}")
        return

    doc = _get_doc()
    sheet = _get_sheet(doc, entity["sheet"])
    row = _find_row_by_id(entity, sid)
    if row < 0:
        _log_warn("update_record", f"ID {sid} not found in {entity['sheet']}", str(values))
        _msgbox(f"Record ID {sid} not found in {entity['sheet']}")
        return

    _ROLLBACK_LOG.clear()

    resolved = _resolve_col_map(entity)
    try:
        for form_field, target_col in resolved.items():
            if form_field in values and values[form_field]:
                old_val = _read_cell(sheet, target_col, row)
                new_val = values[form_field]
                if str(old_val) != str(new_val):
                    _write_cell(sheet, target_col, row, new_val)
                    _audit_log(entity, sid, "UPDATE", form_field, old_val, new_val)
                    _track_rollback(entity, sid)
    except Exception as exc:
        _log_error("update_record", f"Rolling back after update failure: {exc}", traceback.format_exc())
        _undo_rollback()
        raise

    _invalidate_index(entity)
    _log_info("update_record", f"Updated {entity['sheet']} ID={sid}", str(values))
    _clear_form(config)
    _msgbox(f"Record ID {sid} updated in {entity['sheet']}")

def search_record(config):
    entity = config["entity"]
    values = _read_form(config)
    sid = values.get(config["search_field"], "").strip()
    if not sid:
        _log_warn("search_record", f"No search value in '{config['search_field']}'", str(values))
        _msgbox(f"Enter a value in '{config['search_field']}' to search")
        return

    doc = _get_doc()
    sheet = _get_sheet(doc, entity["sheet"])
    row = _find_row_by_id(entity, sid)
    if row < 0:
        _log_info("search_record", f"Not found: {config['search_field']}={sid} in {entity['sheet']}")
        _msgbox(f"No record found with {config['search_field']} = {sid}")
        return

    resolved = _resolve_col_map(entity)
    rev_map = {v: k for k, v in resolved.items()}
    result = {config["search_field"]: sid}
    for col_idx in sorted(rev_map.keys()):
        form_field = rev_map[col_idx]
        val = _read_cell(sheet, col_idx, row)
        if val:
            result[form_field] = val
    _populate_form(config, result)
    _log_info(f"search_record", f"Found in {entity['sheet']} ID={sid} at row {row + 1}")
    _msgbox(f"Found in {entity['sheet']} row {row + 1}")

# ============================================================
# MACRO FUNCTIONS (thin wrappers, keep old names for buttons)
# ============================================================

def _run_macro(action, form_config, action_name):
    """Execute a CRUD operation with unified error handling.
    Logs full tracebacks for devs, shows friendly messages for users.
    """
    try:
        action(form_config)
    except Exception as exc:
        tb = traceback.format_exc()
        _log_error(action_name, str(exc), tb)
        friendly = _user_friendly_error(exc)
        _msgbox(
            f"{action_name} encountered a problem.\n"
            f"\n{friendly}"
            f"\n\nFull details have been logged to the '{_LOG_SHEET}' sheet."
        )

def register_person(*args):
    _run_macro(create_record, FORM_REGISTER_PERSON, "Register Person")

def add_payment(*args):
    _run_macro(create_record, FORM_ADD_PAYMENT, "Add Payment")

def add_representative(*args):
    _run_macro(create_record, FORM_ADD_REPRESENTATIVE, "Add Representative")

def add_donor(*args):
    _run_macro(create_record, FORM_ADD_DONOR, "Add Donor")

def add_sponsorship(*args):
    _run_macro(create_record, FORM_ADD_SPONSORSHIP, "Add Sponsorship")

def add_document(*args):
    _run_macro(create_record, FORM_ADD_DOCUMENT, "Add Document")

def add_assessment(*args):
    _run_macro(create_record, FORM_ADD_ASSESSMENT, "Add Assessment")

def search_person(*args):
    _run_macro(search_record, FORM_REGISTER_PERSON, "Search Person")

def search_payment(*args):
    _run_macro(search_record, FORM_ADD_PAYMENT, "Search Payment")

def search_representative(*args):
    _run_macro(search_record, FORM_ADD_REPRESENTATIVE, "Search Representative")

def search_donor(*args):
    _run_macro(search_record, FORM_ADD_DONOR, "Search Donor")

def search_sponsorship(*args):
    _run_macro(search_record, FORM_ADD_SPONSORSHIP, "Search Sponsorship")

def search_document(*args):
    _run_macro(search_record, FORM_ADD_DOCUMENT, "Search Document")

def search_assessment(*args):
    _run_macro(search_record, FORM_ADD_ASSESSMENT, "Search Assessment")

def patch_person(*args):
    _run_macro(update_record, FORM_PATCH_PERSON, "Patch Person")

def patch_donor(*args):
    _run_macro(update_record, FORM_PATCH_DONOR, "Patch Donor")

# ============================================================
# EXPORTED SCRIPTS
# ============================================================

g_exportedScripts = (
    register_person,
    add_payment,
    add_representative,
    add_donor,
    add_sponsorship,
    add_document,
    add_assessment,
    search_person,
    search_payment,
    search_representative,
    search_donor,
    search_sponsorship,
    search_document,
    search_assessment,
    patch_person,
    patch_donor,
)
