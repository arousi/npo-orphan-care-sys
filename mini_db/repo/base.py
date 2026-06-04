from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BaseRepository(ABC):
    """Abstract base class for all repository implementations."""
    
    @abstractmethod
    def add(self, entity: Any) -> int:
        """
        Save a new entity.
        
        Args:
            entity: The entity to save
            
        Returns:
            The ID of the saved entity
        """
        pass
    
    @abstractmethod
    def update(self, entity: Any) -> bool:
        """
        Update an existing entity.
        
        Args:
            entity: The entity to update
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: int, model_class) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity
            model_class: The model class
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def get(self, entity_id: int, model_class) -> Optional[Any]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: The ID of the entity
            model_class: The model class
            
        Returns:
            The entity or None if not found
        """
        pass
    
    @abstractmethod
    def get_all(self, model_class) -> List[Any]:
        """
        Get all entities of a type.
        
        Args:
            model_class: The model class
            
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    def get_next_id(self, prefix: str) -> str:
        """
        Generate next sequential ID with prefix.
        
        Args:
            prefix: ID prefix (e.g., 'FAM', 'VOL')
            
        Returns:
            Generated ID (e.g., 'FAM-000001')
        """
        pass
