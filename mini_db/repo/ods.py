import pandas as pd
import os
import json
from pathlib import Path
from .base import BaseRepository
from typing import List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ODSRepository(BaseRepository):
    """Open Document Spreadsheet (.ods) repository using pandas."""
    
    def __init__(self, file_path: str):
        """
        Initialize ODS repository.
        
        Args:
            file_path: Path to the ODS file
        """
        self.file_path = Path(file_path)
        self._id_counter = {}
        self._load_id_counter()
        logger.info(f"ODSRepository initialized: {file_path}")
    
    def add(self, entity: Any) -> int:
        """Add a new entity (save to ODS sheet)."""
        try:
            sheet_name = entity.__tablename__
            entity_dict = self._entity_to_dict(entity)
            
            if self.file_path.exists():
                try:
                    df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='odf')
                except (ValueError, FileNotFoundError):
                    df = pd.DataFrame([entity_dict])
                else:
                    df = pd.concat([df, pd.DataFrame([entity_dict])], ignore_index=True)
            else:
                df = pd.DataFrame([entity_dict])
            
            with pd.ExcelWriter(self.file_path, engine='odf', mode='a' if self.file_path.exists() else 'w',
                              if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"Added {sheet_name} record to ODS")
            return len(df) - 1
        except Exception as e:
            logger.error(f"Error adding entity to ODS: {e}")
            raise
    
    def update(self, entity: Any) -> bool:
        """Update an entity in ODS."""
        try:
            sheet_name = entity.__tablename__
            entity_dict = self._entity_to_dict(entity)
            
            if not self.file_path.exists():
                logger.warning(f"ODS file not found: {self.file_path}")
                return False
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='odf')
            
            if hasattr(entity, 'id') and 'id' in df.columns:
                mask = df['id'] == entity.id
                for col, val in entity_dict.items():
                    df.loc[mask, col] = val
            else:
                df = pd.DataFrame([entity_dict])
            
            with pd.ExcelWriter(self.file_path, engine='odf', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"Updated {sheet_name} record in ODS")
            return True
        except Exception as e:
            logger.error(f"Error updating entity in ODS: {e}")
            raise
    
    def delete(self, entity_id: int, model_class) -> bool:
        """Delete an entity from ODS."""
        try:
            sheet_name = model_class.__tablename__
            
            if not self.file_path.exists():
                return False
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='odf')
            
            if 'id' in df.columns:
                df = df[df['id'] != entity_id]
                with pd.ExcelWriter(self.file_path, engine='odf', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                logger.info(f"Deleted record from {sheet_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting entity from ODS: {e}")
            raise
    
    def get(self, entity_id: int, model_class) -> Optional[Any]:
        """Get a single entity from ODS."""
        try:
            sheet_name = model_class.__tablename__
            
            if not self.file_path.exists():
                return None
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='odf')
            
            if 'id' in df.columns:
                row = df[df['id'] == entity_id]
                if not row.empty:
                    return row.to_dict('records')[0]
            return None
        except Exception as e:
            logger.error(f"Error getting entity from ODS: {e}")
            return None
    
    def get_all(self, model_class) -> List[Any]:
        """Get all entities from an ODS sheet."""
        try:
            sheet_name = model_class.__tablename__
            
            if not self.file_path.exists():
                return []
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='odf')
            return df.where(pd.notnull(df), None).to_dict('records')
        except Exception as e:
            logger.error(f"Error getting all entities from ODS: {e}")
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
                df = pd.read_excel(self.file_path, sheet_name='_metadata', engine='odf')
                self._id_counter = json.loads(df.to_dict('records')[0].get('id_counter', '{}'))
        except:
            self._id_counter = {}
    
    def _save_id_counter(self):
        """Save ID counter to a meta sheet."""
        try:
            df = pd.DataFrame([{'id_counter': json.dumps(self._id_counter)}])
            with pd.ExcelWriter(self.file_path, engine='odf', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='_metadata', index=False)
        except:
            pass
