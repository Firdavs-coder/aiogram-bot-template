from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from .models import User
from .session import get_session

logger = logging.getLogger(__name__)


class UserCRUD:
    """CRUD operations for User model"""
    
    def __init__(self, session: Optional[Session] = None):
        """Initialize with optional session, create new one if not provided"""
        self.session = session or get_session()
        self._should_close = session is None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session if we created it"""
        if self._should_close:
            self.session.close()
    
    def create_user(self, user_id: int, name: str) -> User:
        """Create a new user or update existing one"""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_id(user_id)
            
            if existing_user:
                # Update existing user's name
                existing_user.name = name
                self.session.commit()
                # Refresh to load the latest data and then expunge
                self.session.refresh(existing_user)
                self.session.expunge(existing_user)
                logger.info(f"Updated user: ID={user_id}, Name={name}")
                return existing_user
            else:
                # Create new user
                user = User(user_id=user_id, name=name)
                self.session.add(user)
                self.session.commit()
                # Refresh to get the ID and then expunge to detach from session
                self.session.refresh(user)
                self.session.expunge(user)
                logger.info(f"Created new user: ID={user_id}, Name={name}")
                return user
                
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Integrity error creating user {user_id}: {e}")
            raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating user {user_id}: {e}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            user = self.session.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        try:
            users = self.session.query(User).all()
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def update_user(self, user_id: int, name: Optional[str] = None) -> Optional[User]:
        """Update user information"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for update")
                return None
            
            if name is not None:
                user.name = name
            
            self.session.commit()
            logger.info(f"Updated user {user_id}")
            return user
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            
            self.session.delete(user)
            self.session.commit()
            logger.info(f"Deleted user {user_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        try:
            count = self.session.query(User).count()
            return count
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        try:
            exists = self.session.query(User).filter(User.id == user_id).first() is not None
            return exists
        except Exception as e:
            logger.error(f"Error checking if user {user_id} exists: {e}")
            return False


# Convenience functions for quick operations
def create_user(user_id: int, name: str) -> User:
    """Create user with automatic session management"""
    with UserCRUD() as crud:
        return crud.create_user(user_id, name)


def get_user(user_id: int) -> Optional[User]:
    """Get user with automatic session management"""
    with UserCRUD() as crud:
        return crud.get_user_by_id(user_id)


def get_all_users() -> List[User]:
    """Get all users with automatic session management"""
    with UserCRUD() as crud:
        return crud.get_all_users()


def update_user(user_id: int, name: Optional[str] = None) -> Optional[User]:
    """Update user with automatic session management"""
    with UserCRUD() as crud:
        return crud.update_user(user_id, name)


def delete_user(user_id: int) -> bool:
    """Delete user with automatic session management"""
    with UserCRUD() as crud:
        return crud.delete_user(user_id)


def user_exists(user_id: int) -> bool:
    """Check if user exists with automatic session management"""
    with UserCRUD() as crud:
        return crud.user_exists(user_id)


def get_user_count() -> int:
    """Get user count with automatic session management"""
    with UserCRUD() as crud:
        return crud.get_user_count()
