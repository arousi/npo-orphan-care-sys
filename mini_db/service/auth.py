import hashlib
import logging
from datetime import datetime
from typing import Optional, List
from models.models import SystemUser, Person, Base
from repo.files import RepositoryFactory
from config import PRIMARY_BACKEND, EXCEL_FILE_PATH, ROLES

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages user authentication and authorization."""
    
    def __init__(self, repository):
        """
        Initialize authentication manager.
        
        Args:
            repository: Repository instance for accessing users
        """
        self.repo = repository
        self._current_user = None
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, role: str, 
                   person_id: Optional[int] = None) -> bool:
        """
        Create a new system user.
        
        Args:
            username: Username
            password: Plain text password (will be hashed)
            role: User role (manager, volunteer, staff)
            person_id: Associated person record ID
            
        Returns:
            True if user was created
        """
        try:
            if role not in ROLES:
                logger.warning(f"Invalid role: {role}")
                return False
            
            # Check if user already exists
            existing = self.get_user_by_username(username)
            if existing:
                logger.warning(f"User already exists: {username}")
                return False
            
            user = SystemUser(
                username=username,
                password_hash=self.hash_password(password),
                role=role,
                person_id=person_id,
                is_active=True
            )
            
            self.repo.add(user)
            logger.info(f"Created user: {username} with role {role}")
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional['SystemUser']:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            SystemUser if authenticated, None otherwise
        """
        try:
            user = self.get_user_by_username(username)
            if not user:
                logger.warning(f"User not found: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"User is inactive: {username}")
                return None
            
            if user.password_hash != self.hash_password(password):
                logger.warning(f"Invalid password for user: {username}")
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.repo.update(user)
            self._current_user = user
            
            logger.info(f"User authenticated: {username}")
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional['SystemUser']:
        """Get user by username."""
        try:
            users = self.repo.get_all(SystemUser)
            for user in users:
                if isinstance(user, dict):
                    if user.get('username') == username:
                        return user
                elif user.username == username:
                    return user
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_current_user(self) -> Optional['SystemUser']:
        """Get the currently authenticated user."""
        return self._current_user
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if current user has a specific permission.
        
        Args:
            permission: Permission name
            
        Returns:
            True if user has permission
        """
        if not self._current_user:
            return False
        
        user_role = self._current_user.role if isinstance(self._current_user, SystemUser) else self._current_user.get('role')
        if user_role not in ROLES:
            return False
        
        permissions = ROLES[user_role]['permissions']
        return permission in permissions
    
    def logout(self):
        """Logout the current user."""
        if self._current_user:
            logger.info(f"User logged out: {self._current_user.username if hasattr(self._current_user, 'username') else self._current_user.get('username')}")
        self._current_user = None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return False
            
            if isinstance(user, dict):
                if user['password_hash'] != self.hash_password(old_password):
                    return False
                user['password_hash'] = self.hash_password(new_password)
            else:
                if user.password_hash != self.hash_password(old_password):
                    return False
                user.password_hash = self.hash_password(new_password)
            
            self.repo.update(user)
            logger.info(f"Password changed for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False
    
    def reset_password(self, username: str, new_password: str) -> bool:
        """Reset user password (admin only)."""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return False
            
            if isinstance(user, dict):
                user['password_hash'] = self.hash_password(new_password)
            else:
                user.password_hash = self.hash_password(new_password)
            
            self.repo.update(user)
            logger.info(f"Password reset for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False
