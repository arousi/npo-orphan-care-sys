import os
import json
import logging
from pathlib import Path
import pandas as pd

# ============================================================
# LOGGING SETUP
# ============================================================
export_dir = Path("exports")
export_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(export_dir / "export.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ============================================================
# CONFIGURATION
# ============================================================
SUPPORTED_EXTENSIONS = (".ods", ".xlsx")

# Maps FK column base names (without "_id") to target table names
FK_ALIASES = {
    "rep": "Reps",
    "orphan": "Orphans",
    "family": "Families",
    "donor": "Donors",
    "school": "Schools",
    "city": "City",
    "sponsorhip": "Sponsorships",
}

# Column names that end with "_id" but are NOT foreign keys
FK_SKIP_PATTERNS = {"national_id", "type_id"}

# Words that identify a cell as a form header (must appear in the cell content)
FORM_PREFIXES = {"register", "add", "patch", "update", "search", "delete", "new", "edit"}

# Text keywords that indicate an action button cell
BUTTON_KEYWORDS = {"search", "add", "update", "register", "delete", "patch"}

# Maximum number of consecutive empty rows tolerated when walking form fields
FORM_FIELD_EMPTY_GAP = 10


def list_spreadsheets():
    return [
        f for f in os.listdir(".")
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]


def load_workbook(path):
    ext = Path(path).suffix.lower()
    engine = "odf" if ext == ".ods" else "openpyxl"
    return pd.read_excel(path, sheet_name=None, engine=engine, header=None)


def to_excel_coordinate(row_idx, col_idx):
    result = ""
    col = col_idx + 1
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        result = chr(65 + remainder) + result
    return f"{result}{row_idx + 1}"


# ============================================================
# TABLE SCHEMA & RECORD PARSER
# ============================================================
def extract_table_data(df):
    """
    Finds the first non-empty row to establish column headers,
    then processes subsequent records using those headers.
    """
    rows, cols = df.shape
    header_row_idx = None
    headers = []

    for r in range(rows):
        row_values = [str(df.iloc[r, c]).strip() for c in range(cols) if not pd.isna(df.iloc[r, c])]
        if any(v != "" for v in row_values):
            header_row_idx = r
            break

    if header_row_idx is None:
        return [], []

    for c in range(cols):
        val = df.iloc[header_row_idx, c]
        if pd.isna(val) or str(val).strip() == "":
            headers.append(f"Column_{c}")
        else:
            headers.append(str(val).strip())

    records = []
    for r in range(header_row_idx + 1, rows):
        row_raw = df.iloc[r]
        if row_raw.dropna().empty:
            continue

        record = {}
        for c, header in enumerate(headers):
            val = row_raw.iloc[c]
            record[header] = "" if pd.isna(val) else str(val).strip()
        records.append(record)

    columns_metadata = [{"name": h, "type": "text"} for h in headers]

    return columns_metadata, records


# ============================================================
# FORM PARSER
# ============================================================
def _is_form_header(cell_value):
    """Check if a cell value looks like a form header (e.g. 'Register Person Form')."""
    lowered = cell_value.lower()
    if not (lowered.endswith("form") or lowered.endswith("_form")):
        return False
    words = set(lowered.split())
    if words & FORM_PREFIXES:
        return True
    return False


def parse_spatial_forms(df, sheet_name):
    forms = []
    rows, cols = df.shape
    grid = df.fillna("").map(lambda x: str(x).strip())
    visited = set()
    has_forms = False

    for r in range(rows):
        for c in range(cols):
            cell_value = grid.iloc[r, c]

            if not _is_form_header(cell_value):
                continue
            if (r, c) in visited:
                continue

            has_forms = True
            form_header = cell_value
            form_start_row = r
            form_col = c

            fields = []
            buttons = []
            notes = []

            curr_row = form_start_row + 1
            while curr_row < rows:
                field_label = grid.iloc[curr_row, form_col]

                if _is_form_header(field_label):
                    break

                if not field_label and curr_row > form_start_row + FORM_FIELD_EMPTY_GAP:
                    break

                if field_label:
                    fields.append({
                        "label": field_label,
                        "label_coordinate": to_excel_coordinate(curr_row, form_col),
                        "value_coordinate": to_excel_coordinate(curr_row, form_col + 1),
                        "row_index": curr_row,
                        "column_index": form_col
                    })
                    visited.add((curr_row, form_col))
                curr_row += 1

            # Scan all remaining rows for button keywords (in the form column and adjacent)
            for br in range(form_start_row + 1, rows):
                for bc in range(form_col, min(cols, form_col + 4)):
                    b_val = grid.iloc[br, bc]
                    if b_val.lower() in BUTTON_KEYWORDS:
                        buttons.append({
                            "action": b_val.capitalize(),
                            "coordinate": to_excel_coordinate(br, bc),
                            "row_index": br,
                            "column_index": bc
                        })

            if not fields:
                notes.append("Form header discovered but contains zero data input fields underneath it.")

            if not buttons:
                notes.append(
                    "No action button cells detected by text scan. "
                    "Buttons may be assigned via shape macro binding (not inspectable via text scan)."
                )

            forms.append({
                "form_title": form_header,
                "header_coordinate": to_excel_coordinate(form_start_row, form_col),
                "is_valid": len(notes) == 0,
                "notes": notes,
                "fields": fields,
                "buttons": buttons
            })
            visited.add((form_start_row, form_col))

    return forms, has_forms


# ============================================================
# RELATIONSHIP DETECTION
# ============================================================
def detect_relationships(schema):
    relationships = []
    table_names = set(schema.keys())

    for table_name, table in schema.items():
        for column in table["columns"]:
            cname = column["name"]

            if not cname.endswith("_id") or cname == "id":
                continue
            if cname in FK_SKIP_PATTERNS:
                continue

            base = cname[:-3].lower()
            target_discovered = None

            if base in FK_ALIASES:
                alias_target = FK_ALIASES[base]
                if alias_target in table_names:
                    target_discovered = alias_target

            if not target_discovered:
                candidates = [base.capitalize(), base.capitalize() + "s", base.title(), base.title() + "s"]
                for candidate in candidates:
                    if candidate in table_names:
                        target_discovered = candidate
                        break

            if target_discovered:
                relationships.append({
                    "from_table": table_name,
                    "from_column": cname,
                    "to_table": target_discovered,
                    "to_column": "id"
                })
                logging.info(f"Relationship detected: {table_name}.{cname} -> {target_discovered}.id")
            else:
                logging.warning(f"Unresolved foreign key column footprint: '{cname}' inside Table '{table_name}'")

    return relationships


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


# ============================================================
# MAIN ENGINE
# ============================================================
def export_workbook(input_file):
    logging.info(f"Starting workbook analysis extraction pipeline for: {input_file}")
    try:
        workbook = load_workbook(input_file)
    except Exception as e:
        logging.error(f"CRITICAL FAULT: Could not read workbook file system target '{input_file}'. Reason: {e}")
        return

    extension = Path(input_file).suffix.lower()
    data_dir = export_dir / "data"
    data_dir.mkdir(exist_ok=True)

    workbook_metadata = {
        "file_name": Path(input_file).name,
        "file_extension": extension,
        "sheet_count": len(workbook),
        "sheets": list(workbook.keys())
    }

    schema, forms, lookups = {}, {}, {}

    for sheet_name, df in workbook.items():
        logging.info(f"Processing sheet container: [{sheet_name}]")

        try:
            # 1. Parse spatial forms
            detected_forms, has_forms = parse_spatial_forms(df, sheet_name)
            if detected_forms:
                forms[sheet_name] = {
                    "sheet_name": sheet_name,
                    "forms": detected_forms
                }
                logging.info(f"  Extracted {len(detected_forms)} form blocks out of [{sheet_name}]")

            # 2. Skip data-table export for form layout sheets
            if has_forms:
                logging.info(f"  Sheet identified as form layout interface. Skipping data table parsing.")
                continue

            # 3. Extract data records
            columns_metadata, records = extract_table_data(df)
            if not columns_metadata and not records:
                logging.info(f"  Sheet identified as structurally empty data grid. Skipping database parsing.")
                continue

            schema[sheet_name] = {
                "source_file": Path(input_file).name,
                "sheet_name": sheet_name,
                "row_count": len(records),
                "columns": columns_metadata
            }

            save_json(data_dir / f"{sheet_name}.json", {"records": records})

            if len(columns_metadata) <= 3 and any(c["name"].lower() == "id" for c in columns_metadata):
                lookups[sheet_name] = {"sheet_name": sheet_name, "values": records}
                logging.info(f"  Registered sheet [{sheet_name}] as data lookup table tracking vector.")

        except Exception as sheet_error:
            logging.error(f"Fault event managed processing sheet container [{sheet_name}]: {sheet_error}. Proceeding...")
            continue

    relationships = detect_relationships(schema)

    save_json(export_dir / "workbook_metadata.json", workbook_metadata)
    save_json(export_dir / "schema.json", schema)
    save_json(export_dir / "relationships.json", relationships)
    save_json(export_dir / "forms.json", forms)
    save_json(export_dir / "lookups.json", lookups)

    logging.info("Compilation complete. Structural output maps generated successfully inside /exports folder.")


def main():
    files = list_spreadsheets()
    if not files:
        logging.warning("No file sources matched .ods or .xlsx within directory boundaries.")
        return

    print()
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")
    print()

    choice = input("Select workbook: ")
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(files):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return

    export_workbook(files[idx])


if __name__ == "__main__":
    main()
