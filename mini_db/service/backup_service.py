import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from config import (
    BACKUP_DIR, SQLITE_DB_PATH, AUTO_EMPTY_AFTER_BACKUP, BACKUP_ENABLED, 
    BACKUP_ON_APP_CLOSE, BACKUP_RETENTION_ENABLED, MAX_BACKUP_RETENTION_DAYS, SQLITE_URL,
    EXCEL_FILE_PATH, ODS_FILE_PATH
)
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class BackupService:
    """Manages database backup and archival operations."""
    
    def __init__(self):
        """Initialize backup service."""
        self.backup_dir = BACKUP_DIR
        self.sqlite_db_path = SQLITE_DB_PATH
        self.backup_enabled = BACKUP_ENABLED
        self.auto_empty = AUTO_EMPTY_AFTER_BACKUP
        self.backup_on_close = BACKUP_ON_APP_CLOSE
        self.retention_enabled = BACKUP_RETENTION_ENABLED
        self.max_retention_days = MAX_BACKUP_RETENTION_DAYS
        
        logger.info(f"BackupService initialized. Backup directory: {self.backup_dir}")
        logger.info(f"Backup on app close: {self.backup_on_close}")
    
    def manual_backup(self) -> bool:
        """
        Perform a manual backup immediately (SQLite + XLSX + ODS).
        
        Returns:
            True if backup successful
        """
        try:
            if not self.backup_enabled:
                logger.warning("Backup is disabled in configuration")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup SQLite
            backup_filename = f"orphanage_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            if self.sqlite_db_path.exists():
                shutil.copy2(self.sqlite_db_path, backup_path)
                logger.info(f"SQLite backup created: {backup_path}")
            
            # Backup XLSX
            xlsx_backup = self.backup_dir / f"orphanage_{timestamp}.xlsx"
            if EXCEL_FILE_PATH.exists():
                shutil.copy2(EXCEL_FILE_PATH, xlsx_backup)
                logger.info(f"XLSX backup created: {xlsx_backup}")
            
            # Backup ODS
            ods_backup = self.backup_dir / f"orphanage_{timestamp}.ods"
            if ODS_FILE_PATH.exists():
                shutil.copy2(ODS_FILE_PATH, ods_backup)
                logger.info(f"ODS backup created: {ods_backup}")
            
            # Create manifest file
            manifest_path = self.backup_dir / f"orphanage_{timestamp}.manifest"
            with open(manifest_path, 'w') as f:
                f.write(f"Backup Date: {datetime.now().isoformat()}\n")
                f.write(f"Backup Type: Manual\n")
                f.write(f"Files Backed Up:\n")
                if self.sqlite_db_path.exists():
                    f.write(f"  - {backup_filename}\n")
                if EXCEL_FILE_PATH.exists():
                    f.write(f"  - {xlsx_backup.name}\n")
                if ODS_FILE_PATH.exists():
                    f.write(f"  - {ods_backup.name}\n")
            
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def daily_backup(self) -> bool:
        """
        Perform a backup (typically on app close) - SQLite + XLSX + ODS.
        
        Returns:
            True if backup successful
        """
        try:
            if not self.backup_enabled:
                logger.warning("Backup is disabled in configuration")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup SQLite
            backup_filename = f"orphanage_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            if self.sqlite_db_path.exists():
                shutil.copy2(self.sqlite_db_path, backup_path)
                logger.info(f"SQLite backup created: {backup_path}")
            
            # Backup XLSX
            xlsx_backup = self.backup_dir / f"orphanage_backup_{timestamp}.xlsx"
            if EXCEL_FILE_PATH.exists():
                shutil.copy2(EXCEL_FILE_PATH, xlsx_backup)
                logger.info(f"XLSX backup created: {xlsx_backup}")
            
            # Backup ODS
            ods_backup = self.backup_dir / f"orphanage_backup_{timestamp}.ods"
            if ODS_FILE_PATH.exists():
                shutil.copy2(ODS_FILE_PATH, ods_backup)
                logger.info(f"ODS backup created: {ods_backup}")
            
            # Create manifest
            manifest_path = self.backup_dir / f"orphanage_backup_{timestamp}.manifest"
            with open(manifest_path, 'w') as f:
                f.write(f"Backup Date: {datetime.now().isoformat()}\n")
                f.write(f"Backup Type: Application Close\n")
                f.write(f"Files Backed Up:\n")
                if self.sqlite_db_path.exists():
                    f.write(f"  - {backup_filename} ({backup_path.stat().st_size / 1024:.2f} KB)\n")
                if EXCEL_FILE_PATH.exists():
                    f.write(f"  - {xlsx_backup.name} ({xlsx_backup.stat().st_size / 1024:.2f} KB)\n")
                if ODS_FILE_PATH.exists():
                    f.write(f"  - {ods_backup.name} ({ods_backup.stat().st_size / 1024:.2f} KB)\n")
            
            # Empty the database if configured
            if self.auto_empty:
                if self._empty_database():
                    logger.info("Database emptied after successful backup")
            
            # Clean old backups (only if retention is enabled)
            if self.retention_enabled:
                self._cleanup_old_backups()
            
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def _empty_database(self) -> bool:
        """
        Empty the SQLite database while keeping the schema.
        
        Returns:
            True if successful
        """
        try:
            engine = create_engine(SQLITE_URL)
            with engine.connect() as conn:
                # Get all table names
                tables_query = text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = conn.execute(tables_query).fetchall()
                
                # Delete all records from each table
                for (table_name,) in tables:
                    try:
                        delete_query = text(f"DELETE FROM {table_name}")
                        conn.execute(delete_query)
                        logger.info(f"Cleared table: {table_name}")
                    except Exception as e:
                        logger.warning(f"Could not clear table {table_name}: {e}")
                
                conn.commit()
            
            logger.info("Database emptied successfully (schema preserved)")
            return True
        except Exception as e:
            logger.error(f"Error emptying database: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Remove backups older than MAX_BACKUP_RETENTION_DAYS (only if enabled)."""
        if not self.retention_enabled:
            logger.debug("Backup retention cleanup is disabled - keeping all backups")
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.max_retention_days)
            
            for backup_file in self.backup_dir.glob("orphanage*.db"):
                # Parse date from filename (YYYYMMDD)
                try:
                    date_str = backup_file.name.split("_")[2]  # orphanage_backup_20240101_120000.db
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if file_date < cutoff_date:
                        backup_file.unlink()
                        # Also remove manifest
                        manifest = backup_file.with_suffix('.manifest')
                        if manifest.exists():
                            manifest.unlink()
                        logger.info(f"Removed old backup: {backup_file.name}")
                except (IndexError, ValueError) as e:
                    logger.debug(f"Could not parse date from {backup_file.name}: {e}")
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def list_backups(self) -> list:
        """
        List all available backups (all formats combined).
        
        Returns:
            List of backup file paths (SQLite, XLSX, ODS)
        """
        try:
            if not self.backup_dir.exists():
                return []
            
            backups = sorted(
                [f for f in self.backup_dir.glob("orphanage*") 
                 if f.suffix in ['.db', '.xlsx', '.ods']],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            return backups
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def list_sqlite_backups(self) -> list:
        """List only SQLite database backups."""
        try:
            if not self.backup_dir.exists():
                return []
            backups = sorted(
                list(self.backup_dir.glob("orphanage*.db")),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            return backups
        except Exception as e:
            logger.error(f"Error listing SQLite backups: {e}")
            return []
    
    def list_xlsx_backups(self) -> list:
        """List only XLSX backups."""
        try:
            if not self.backup_dir.exists():
                return []
            backups = sorted(
                list(self.backup_dir.glob("orphanage*.xlsx")),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            return backups
        except Exception as e:
            logger.error(f"Error listing XLSX backups: {e}")
            return []
    
    def list_ods_backups(self) -> list:
        """List only ODS backups."""
        try:
            if not self.backup_dir.exists():
                return []
            backups = sorted(
                list(self.backup_dir.glob("orphanage*.ods")),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            return backups
        except Exception as e:
            logger.error(f"Error listing ODS backups: {e}")
            return []
    
    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restore a database/file from a backup.
        
        Args:
            backup_path: Path to the backup file (.db, .xlsx, or .ods)
            
        Returns:
            True if restore successful
        """
        try:
            if not Path(backup_path).exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            backup_path = Path(backup_path)
            suffix = backup_path.suffix.lower()
            
            # Handle SQLite restore
            if suffix == '.db':
                # Create backup of current DB before restoring
                current_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                if self.sqlite_db_path.exists():
                    shutil.copy2(self.sqlite_db_path, current_backup)
                    logger.info(f"Current database backed up to: {current_backup}")
                
                # Restore backup
                shutil.copy2(backup_path, self.sqlite_db_path)
                logger.info(f"SQLite database restored from: {backup_path}")
                return True
            
            # Handle Excel restore
            elif suffix == '.xlsx':
                # Create backup of current file
                current_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                if EXCEL_FILE_PATH.exists():
                    shutil.copy2(EXCEL_FILE_PATH, current_backup)
                    logger.info(f"Current Excel file backed up to: {current_backup}")
                
                # Restore backup
                shutil.copy2(backup_path, EXCEL_FILE_PATH)
                logger.info(f"Excel file restored from: {backup_path}")
                return True
            
            # Handle ODS restore
            elif suffix == '.ods':
                # Create backup of current file
                current_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ods"
                if ODS_FILE_PATH.exists():
                    shutil.copy2(ODS_FILE_PATH, current_backup)
                    logger.info(f"Current ODS file backed up to: {current_backup}")
                
                # Restore backup
                shutil.copy2(backup_path, ODS_FILE_PATH)
                logger.info(f"ODS file restored from: {backup_path}")
                return True
            
            else:
                logger.warning(f"Unsupported backup file type: {suffix}")
                return False
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def get_backup_stats(self) -> dict:
        """
        Get statistics about current backups.
        
        Returns:
            Dictionary with backup statistics
        """
        try:
            backups = self.list_backups()
            sqlite_backups = self.list_sqlite_backups()
            xlsx_backups = self.list_xlsx_backups()
            ods_backups = self.list_ods_backups()
            
            total_size = sum(b.stat().st_size for b in backups) / (1024 * 1024)  # MB
            
            return {
                'total_backups': len(backups),
                'sqlite_backups': len(sqlite_backups),
                'xlsx_backups': len(xlsx_backups),
                'ods_backups': len(ods_backups),
                'total_size_mb': round(total_size, 2),
                'latest_backup': backups[0].stat().st_mtime if backups else None,
                'backup_directory': str(self.backup_dir),
                'auto_empty_enabled': self.auto_empty,
                'backup_on_close': self.backup_on_close,
                'retention_enabled': self.retention_enabled,
                'retention_days': self.max_retention_days if self.retention_enabled else 'Infinite'
            }
        except Exception as e:
            logger.error(f"Error getting backup stats: {e}")
            return {}
