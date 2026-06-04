from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, inspect
from .base import BaseRepository
from typing import List, Any, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteRepository(BaseRepository):
    """SQLite repository using SQLAlchemy ORM."""
    
    def __init__(self, db_url: str):
        """
        Initialize SQLite repository.
        
        Args:
            db_url: SQLAlchemy database URL (e.g., sqlite:///path/to/db.sqlite)
        """
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._id_counter = self._load_id_counter()
        logger.info(f"SQLiteRepository initialized: {db_url}")
    
    def init_db(self, base_metadata):
        """Create all tables based on SQLAlchemy models."""
        try:
            base_metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def add(self, entity: Any) -> int:
        """Add a new entity to the database."""
        session = self.SessionLocal()
        try:
            session.add(entity)
            session.commit()
            entity_id = entity.id
            logger.info(f"Added {entity.__class__.__name__} with ID {entity_id}")
            return entity_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding entity: {e}")
            raise
        finally:
            session.close()
    
    def update(self, entity: Any) -> bool:
        """Update an existing entity."""
        session = self.SessionLocal()
        try:
            session.merge(entity)
            session.commit()
            logger.info(f"Updated {entity.__class__.__name__} with ID {entity.id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating entity: {e}")
            raise
        finally:
            session.close()
    
    def delete(self, entity_id: int, model_class) -> bool:
        """Delete an entity by ID."""
        session = self.SessionLocal()
        try:
            entity = session.query(model_class).filter(model_class.id == entity_id).first()
            if entity:
                session.delete(entity)
                session.commit()
                logger.info(f"Deleted {model_class.__name__} with ID {entity_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting entity: {e}")
            raise
        finally:
            session.close()
    
    def get(self, entity_id: int, model_class) -> Optional[Any]:
        """Get an entity by ID."""
        session = self.SessionLocal()
        try:
            return session.query(model_class).filter(model_class.id == entity_id).first()
        except Exception as e:
            logger.error(f"Error getting entity: {e}")
            raise
        finally:
            session.close()
    
    def get_all(self, model_class) -> List[Any]:
        """Get all entities of a type."""
        session = self.SessionLocal()
        try:
            return session.query(model_class).all()
        except Exception as e:
            logger.error(f"Error getting all entities: {e}")
            raise
        finally:
            session.close()
    
    def query(self, model_class) -> Session:
        """Get a query session for advanced queries."""
        return self.SessionLocal().query(model_class)
    
    def get_next_id(self, prefix: str) -> str:
        """Generate next sequential ID with prefix."""
        if prefix not in self._id_counter:
            self._id_counter[prefix] = 0
        
        self._id_counter[prefix] += 1
        self._save_id_counter()
        
        return f"{prefix}-{self._id_counter[prefix]:06d}"
    
    def _load_id_counter(self) -> dict:
        """Load ID counter from memory (can be extended to persist to file)."""
        return {}
    
    def _save_id_counter(self):
        """Save ID counter (can be extended to persist to file)."""
        pass

    
    
