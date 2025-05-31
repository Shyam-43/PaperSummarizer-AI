from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

class User(UserMixin):
    def __init__(self, username, email, password_hash=None, user_id=None):
        self.id = user_id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.utcnow().isoformat()
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary for storage."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user object from dictionary."""
        user = cls(data['username'], data['email'], data['password_hash'], data['id'])
        user.created_at = data.get('created_at', datetime.utcnow().isoformat())
        return user
    
    @classmethod
    def get(cls, user_id, data_manager):
        """Get user by ID."""
        user_data = data_manager.get_user_by_id(user_id)
        if user_data:
            return cls.from_dict(user_data)
        return None
    
    @classmethod
    def get_by_username(cls, username, data_manager):
        """Get user by username."""
        user_data = data_manager.get_user_by_username(username)
        if user_data:
            return cls.from_dict(user_data)
        return None
    
    def save(self, data_manager):
        """Save user to storage."""
        return data_manager.save_user(self.to_dict())

class Summary:
    def __init__(self, user_id, input_type, content, summary, original_filename=None, summary_id=None):
        self.id = summary_id or str(uuid.uuid4())
        self.user_id = user_id
        self.input_type = input_type  # 'text', 'url', 'pdf', 'batch_pdf'
        self.content = content
        self.summary = summary
        self.original_filename = original_filename
        self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self):
        """Convert summary object to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'input_type': self.input_type,
            'content': self.content,
            'summary': self.summary,
            'original_filename': self.original_filename,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create summary object from dictionary."""
        return cls(
            data['user_id'],
            data['input_type'],
            data['content'],
            data['summary'],
            data.get('original_filename'),
            data['id']
        )
    
    def save(self, data_manager):
        """Save summary to storage."""
        return data_manager.save_summary(self.to_dict())
