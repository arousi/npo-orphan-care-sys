from pathlib import Path
from .xsls import XLSXRepository
from .ods import ODSRepository
from .sqlite import SQLiteRepository
import logging

logger = logging.getLogger(__name__)

class RepositoryFactory:
    """Factory for creating repository instances based on file type."""
    
    @staticmethod
    def get_repository(file_path: str, db_type: str = None):
        """
        Get the appropriate repository based on file type.
        
        Args:
            file_path: Path to the data file or database
            db_type: Optional explicit type ('excel', 'ods', 'sqlite')
            
        Returns:
            A repository instance
            
        Raises:
            ValueError: If file type is not supported
        """
        try:
            file_path_obj = Path(file_path) if db_type != 'sqlite' else file_path
            
            if db_type == 'sqlite':
                logger.info(f"Creating SQLiteRepository: {file_path}")
                return SQLiteRepository(file_path)
            elif db_type == 'ods' or str(file_path_obj).endswith('.ods'):
                logger.info(f"Creating ODSRepository: {file_path}")
                return ODSRepository(str(file_path_obj))
            elif db_type == 'excel' or str(file_path_obj).endswith(('.xlsx', '.xls')):
                logger.info(f"Creating XLSXRepository: {file_path}")
                return XLSXRepository(str(file_path_obj))
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            raise
