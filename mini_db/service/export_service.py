"""
Data Export/Import Service for Kahatayn
Allows NPOs to export data for backup and modification
"""

import logging
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import DATA_DIR, BACKUP_DIR

logger = logging.getLogger(__name__)


class DataExportService:
    """Manages data export and import for external modification."""
    
    def __init__(self):
        """Initialize export service."""
        self.data_dir = DATA_DIR
        self.backup_dir = BACKUP_DIR
        self.export_dir = DATA_DIR / "exports"
        self.export_dir.mkdir(exist_ok=True)
        logger.info(f"DataExportService initialized. Export directory: {self.export_dir}")
    
    def export_all_data(self, filename: Optional[str] = None) -> Optional[Path]:
        """
        Export all data files (DB, XLSX, ODS) and backups as a ZIP.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to exported ZIP file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"kahatayn_export_{timestamp}.zip"
            
            export_path = self.export_dir / filename
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add current data files
                for file_ext in ['*.db', '*.xlsx', '*.ods']:
                    for file in self.data_dir.glob(file_ext):
                        zf.write(file, file.name)
                        logger.info(f"Added to export: {file.name}")
                
                # Add recent backups
                if self.backup_dir.exists():
                    for backup_file in self.backup_dir.glob("*"):
                        if backup_file.is_file():
                            zf.write(backup_file, f"backups/{backup_file.name}")
                    logger.info(f"Added backups to export")
            
            logger.info(f"Data export created: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return None
    
    def export_current_files(self, filename: Optional[str] = None) -> Optional[Path]:
        """
        Export only current data files (DB, XLSX, ODS).
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to exported ZIP file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"kahatayn_current_{timestamp}.zip"
            
            export_path = self.export_dir / filename
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add only current data files
                for file_ext in ['*.db', '*.xlsx', '*.ods']:
                    for file in self.data_dir.glob(file_ext):
                        zf.write(file, file.name)
                        logger.info(f"Exported: {file.name}")
            
            logger.info(f"Current data export created: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"Error exporting current data: {e}")
            return None
    
    def import_data(self, zip_path: Path) -> bool:
        """
        Import data from exported ZIP file.
        
        Args:
            zip_path: Path to ZIP file containing data
            
        Returns:
            True if import successful
        """
        try:
            if not Path(zip_path).exists():
                logger.error(f"ZIP file not found: {zip_path}")
                return False
            
            # Create backup before importing
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_dir / f"pre_import_{backup_timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # Backup current files
            for file_ext in ['*.db', '*.xlsx', '*.ods']:
                for file in self.data_dir.glob(file_ext):
                    shutil.copy2(file, backup_dir / file.name)
            
            logger.info(f"Created backup before import: {backup_dir}")
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for file in zf.namelist():
                    if file.endswith(('.db', '.xlsx', '.ods')):
                        # Extract directly to data folder
                        zf.extract(file, self.data_dir)
                        logger.info(f"Imported: {file}")
            
            logger.info(f"Data import completed from: {zip_path}")
            return True
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False
    
    def create_modification_package(self, filename: Optional[str] = None) -> Optional[Path]:
        """
        Create a package with data files for NPO to modify externally.
        Includes instructions and template.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to created package
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"kahatayn_modify_{timestamp}.zip"
            
            export_path = self.export_dir / filename
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add current data files
                for file_ext in ['*.xlsx', '*.ods']:
                    for file in self.data_dir.glob(file_ext):
                        zf.write(file, f"modify/{file.name}")
                
                # Add instructions
                instructions = """
KAHATAYN DATA MODIFICATION PACKAGE
===================================

This package contains your current data files for modification.

HOW TO USE:
1. Extract this ZIP file
2. Open modify/orphanage_data.xlsx in Excel OR
   Open modify/orphanage_data.ods in LibreOffice
3. Make your changes (add families, update assessments, etc.)
4. Save the file
5. Email this modified file back to the development team
6. They will import it back into your system

IMPORTANT:
- Only modify the spreadsheets, not the folder structure
- Keep file names the same (orphanage_data.xlsx or orphanage_data.ods)
- Do not modify database file (.db) - use Excel/ODS instead
- Back up your original files before modifying

For help, contact the system administrator.
"""
                zf.writestr("INSTRUCTIONS.txt", instructions)
                logger.info("Modification package created with instructions")
            
            logger.info(f"Modification package created: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"Error creating modification package: {e}")
            return None
    
    def list_exports(self) -> list:
        """
        List all exported files.
        
        Returns:
            List of export file paths
        """
        try:
            exports = sorted(
                list(self.export_dir.glob("*.zip")),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            return exports
        except Exception as e:
            logger.error(f"Error listing exports: {e}")
            return []
    
    def get_export_stats(self) -> dict:
        """
        Get statistics about exports.
        
        Returns:
            Dictionary with export information
        """
        try:
            exports = self.list_exports()
            total_size = sum(e.stat().st_size for e in exports) / (1024 * 1024)  # MB
            
            return {
                'total_exports': len(exports),
                'total_size_mb': round(total_size, 2),
                'latest_export': exports[0].stat().st_mtime if exports else None,
                'export_directory': str(self.export_dir)
            }
        except Exception as e:
            logger.error(f"Error getting export stats: {e}")
            return {}
    
    def cleanup_old_exports(self, days: int = 90) -> int:
        """
        Remove exports older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of files deleted
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for export_file in self.export_dir.glob("*.zip"):
                file_date = datetime.fromtimestamp(export_file.stat().st_mtime)
                if file_date < cutoff_date:
                    export_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old export: {export_file.name}")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up exports: {e}")
            return 0
