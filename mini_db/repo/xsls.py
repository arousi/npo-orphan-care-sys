import pandas as pd
import os
import json
from pathlib import Path
from .base import BaseRepository
from typing import List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class XLSXRepository(BaseRepository):
    """Excel (.xlsx) repository using pandas and openpyxl."""
    
    def __init__(self, file_path: str):
        """
        Initialize Excel repository.
        
        Args:
            file_path: Path to the Excel file
        """
        self.file_path = Path(file_path)
        self._id_counter = {}
        self._load_id_counter()
        logger.info(f"XLSXRepository initialized: {file_path}")
    
    def add(self, entity: Any) -> int:
        """Add a new entity (save to Excel sheet)."""
        try:
            sheet_name = entity.__tablename__
            entity_dict = self._entity_to_dict(entity)
            
            # Create parent directory if needed
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing data or create new
            if self.file_path.exists():
                try:
                    df_existing = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
                    df = pd.concat([df_existing, pd.DataFrame([entity_dict])], ignore_index=True)
                except (ValueError, FileNotFoundError, Exception):
                    # Sheet doesn't exist, create new dataframe
                    df = pd.DataFrame([entity_dict])
            else:
                df = pd.DataFrame([entity_dict])
            
            # Write to Excel - simple approach
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"Added {sheet_name} record to Excel")
            return len(df) - 1
        except Exception as e:
            logger.error(f"Error adding entity to Excel: {e}")
            raise
    
    def update(self, entity: Any) -> bool:
        """Update an entity in Excel."""
        try:
            sheet_name = entity.__tablename__
            entity_dict = self._entity_to_dict(entity)
            
            if not self.file_path.exists():
                logger.warning(f"Excel file not found: {self.file_path}")
                return False
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
            
            # Find and update by ID if it exists
            if hasattr(entity, 'id') and 'id' in df.columns:
                mask = df['id'] == entity.id
                for col, val in entity_dict.items():
                    df.loc[mask, col] = val
            else:
                # Replace entire sheet
                df = pd.DataFrame([entity_dict])
            
            with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"Updated {sheet_name} record in Excel")
            return True
        except Exception as e:
            logger.error(f"Error updating entity in Excel: {e}")
            raise
    
    def delete(self, entity_id: int, model_class) -> bool:
        """Delete an entity from Excel."""
        try:
            sheet_name = model_class.__tablename__
            
            if not self.file_path.exists():
                return False
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
            
            if 'id' in df.columns:
                df = df[df['id'] != entity_id]
                with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                logger.info(f"Deleted record from {sheet_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting entity from Excel: {e}")
            raise
    
    def get(self, entity_id: int, model_class) -> Optional[Any]:
        """Get a single entity from Excel."""
        try:
            sheet_name = model_class.__tablename__
            
            if not self.file_path.exists():
                return None
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
            
            if 'id' in df.columns:
                row = df[df['id'] == entity_id]
                if not row.empty:
                    return row.to_dict('records')[0]
            return None
        except Exception as e:
            logger.error(f"Error getting entity from Excel: {e}")
            return None
    
    def get_all(self, model_class) -> List[Any]:
        """Get all entities from an Excel sheet."""
        try:
            sheet_name = model_class.__tablename__
            
            if not self.file_path.exists():
                return []
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
            return df.where(pd.notnull(df), None).to_dict('records')
        except Exception as e:
            logger.error(f"Error getting all entities from Excel: {e}")
            return []
    
    def get_next_id(self, prefix: str) -> str:
        """Generate next sequential ID with prefix."""
        if prefix not in self._id_counter:
            self._id_counter[prefix] = 0
        
        self._id_counter[prefix] += 1
        self._save_id_counter()
        
        return f"{prefix}-{self._id_counter[prefix]:06d}"
    
    def _entity_to_dict(self, entity: Any) -> dict:
        """Convert SQLAlchemy entity to dictionary."""
        return {col.name: getattr(entity, col.name, None) 
                for col in entity.__table__.columns}
    
    def _load_id_counter(self):
        """Load ID counter from a meta sheet."""
        try:
            if self.file_path.exists():
                df = pd.read_excel(self.file_path, sheet_name='_metadata', engine='openpyxl')
                self._id_counter = json.loads(df.to_dict('records')[0].get('id_counter', '{}'))
        except:
            self._id_counter = {}
    
    def _save_id_counter(self):
        """Save ID counter to a meta sheet."""
        try:
            import json
            df = pd.DataFrame([{'id_counter': json.dumps(self._id_counter)}])
            with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='_metadata', index=False)
        except:
            pass
