#!/usr/bin/env python
"""
Setup and initialization script for Kahatayn system.
Creates demo users and initializes the database.
"""

import logging
import sys
from config import logger, PRIMARY_BACKEND, EXCEL_FILE_PATH, SQLITE_URL
from repo.files import RepositoryFactory
from service.auth import AuthManager
from models.models import Base, SystemUser

def init_database():
    """Initialize database with demo data."""
    try:
        logger.info("Initializing database...")
        
        # Create repository
        if PRIMARY_BACKEND == 'sqlite':
            repo = RepositoryFactory.get_repository(SQLITE_URL, 'sqlite')
            # Create tables
            try:
                repo.init_db(Base.metadata)
            except Exception as e:
                logger.warning(f"Database initialization: {e}")
        else:
            repo = RepositoryFactory.get_repository(str(EXCEL_FILE_PATH), 'excel')
        
        logger.info(f"[OK] Repository initialized ({PRIMARY_BACKEND})")
        
        # Create auth manager
        auth = AuthManager(repo)
        
        # Create demo users
        demo_users = [
            ('manager', 'password123', 'manager', 'Manager User'),
            ('volunteer', 'password123', 'volunteer', 'Volunteer User'),
            ('staff', 'password123', 'staff', 'Staff User'),
        ]
        
        logger.info("Creating demo users...")
        for username, password, role, desc in demo_users:
            # Check if user exists
            existing = auth.get_user_by_username(username)
            if not existing:
                auth.create_user(username, password, role)
                logger.info(f"[OK] Created user: {username} ({role})")
            else:
                logger.info(f"[SKIP] User already exists: {username}")
        
        logger.info("[OK] Database initialization complete!")
        logger.info("\n" + "="*60)
        logger.info("Demo Login Credentials:")
        logger.info("="*60)
        for username, password, role, _ in demo_users:
            logger.info(f"  {role.upper()}: {username} / {password}")
        logger.info("="*60 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
