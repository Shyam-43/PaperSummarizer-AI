import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DataManager:
    """Handles data persistence using JSON files."""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self.summaries_file = os.path.join(data_dir, 'summaries.json')
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._init_data_files()
    
    def _init_data_files(self):
        """Initialize JSON data files if they don't exist."""
        if not os.path.exists(self.users_file):
            self._save_json(self.users_file, {})
        
        if not os.path.exists(self.summaries_file):
            self._save_json(self.summaries_file, [])
    
    def _load_json(self, file_path):
        """Load data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return {} if 'users' in file_path else []
    
    def _save_json(self, file_path, data):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {str(e)}")
            return False
    
    # User management methods
    def save_user(self, user_data):
        """Save user data to storage."""
        users = self._load_json(self.users_file)
        users[user_data['id']] = user_data
        return self._save_json(self.users_file, users)
    
    def get_user_by_id(self, user_id):
        """Get user by ID."""
        users = self._load_json(self.users_file)
        return users.get(user_id)
    
    def get_user_by_username(self, username):
        """Get user by username."""
        users = self._load_json(self.users_file)
        for user_data in users.values():
            if user_data.get('username') == username:
                return user_data
        return None
    
    def get_user_by_email(self, email):
        """Get user by email."""
        users = self._load_json(self.users_file)
        for user_data in users.values():
            if user_data.get('email') == email:
                return user_data
        return None
    
    # Summary management methods
    def save_summary(self, summary_data):
        """Save summary data to storage."""
        summaries = self._load_json(self.summaries_file)
        summaries.append(summary_data)
        return self._save_json(self.summaries_file, summaries)
    
    def get_user_summaries(self, user_id):
        """Get all summaries for a specific user."""
        summaries = self._load_json(self.summaries_file)
        user_summaries = [
            summary for summary in summaries 
            if summary.get('user_id') == user_id
        ]
        
        # Sort by creation date (newest first)
        user_summaries.sort(
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        
        return user_summaries
    
    def get_summary_by_id(self, summary_id):
        """Get summary by ID."""
        summaries = self._load_json(self.summaries_file)
        for summary in summaries:
            if summary.get('id') == summary_id:
                return summary
        return None
    
    def delete_summary(self, summary_id, user_id):
        """Delete a summary (only if it belongs to the user)."""
        summaries = self._load_json(self.summaries_file)
        updated_summaries = [
            summary for summary in summaries 
            if not (summary.get('id') == summary_id and summary.get('user_id') == user_id)
        ]
        
        if len(updated_summaries) < len(summaries):
            return self._save_json(self.summaries_file, updated_summaries)
        return False
    
    # Data statistics and cleanup methods
    def get_user_count(self):
        """Get total number of registered users."""
        users = self._load_json(self.users_file)
        return len(users)
    
    def get_summary_count(self):
        """Get total number of summaries."""
        summaries = self._load_json(self.summaries_file)
        return len(summaries)
    
    def cleanup_old_summaries(self, days=30):
        """Remove summaries older than specified days."""
        from datetime import datetime, timedelta
        
        summaries = self._load_json(self.summaries_file)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        filtered_summaries = []
        for summary in summaries:
            try:
                created_at = datetime.fromisoformat(summary.get('created_at', ''))
                if created_at > cutoff_date:
                    filtered_summaries.append(summary)
            except:
                # Keep summaries with invalid dates
                filtered_summaries.append(summary)
        
        if len(filtered_summaries) < len(summaries):
            self._save_json(self.summaries_file, filtered_summaries)
            logger.info(f"Cleaned up {len(summaries) - len(filtered_summaries)} old summaries")
