import pandas as pd
import os
from sqlalchemy import inspect

class MigrationService:
    def __init__(self, file_path, base_models):
        self.file_path = file_path
        self.base_models = base_models  # List of SQLAlchemy classes

    def run_migrations(self):
        """Checks if Excel structure matches SQLAlchemy models."""
        if not os.path.exists(self.file_path):
            self._create_fresh_file()
            return

        for model in self.base_models:
            sheet_name = model.__tablename__
            
            # 1. Get expected columns from SQLAlchemy model
            expected_columns = [c.name for c in inspect(model).columns]
            
            # 2. Load existing Excel sheet
            try:
                df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            except ValueError:
                # Sheet doesn't exist, create it
                self._add_sheet_to_file(sheet_name, expected_columns)
                continue

            # 3. Identify missing columns
            missing_cols = [c for c in expected_columns if c not in df.columns]

            # 4. Append missing columns as NaN/Empty
            if missing_cols:
                print(f"Migrating {sheet_name}: Adding {missing_cols}")
                for col in missing_cols:
                    df[col] = None
                self._save_df(df, sheet_name)

    def _save_df(self, df, sheet_name):
        """Helper to save back to Excel without losing other sheets."""
        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)