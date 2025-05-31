from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
import re
import logging

from models import User
from storage.data_manager import DataManager

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)
data_manager = DataManager()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        # Get user from storage
        user = User.get_by_username(username, data_manager)
        
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page if specified
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        
        if not email:
            errors.append('Email is required.')
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Please enter a valid email address.')
        
        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if username or email already exists
        if not errors:
            existing_user = User.get_by_username(username, data_manager)
            if existing_user:
                errors.append('Username already exists.')
            
            existing_email = data_manager.get_user_by_email(email)
            if existing_email:
                errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create new user
        try:
            user = User(username, email)
            user.set_password(password)
            
            if user.save(data_manager):
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Registration failed. Please try again.', 'error')
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout handler."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
