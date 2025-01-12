import os
import uuid
from passlib.hash import sha256_crypt
from functools import wraps
from flask import request, jsonify
from flask_login import UserMixin
from . import app, login_manager

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

class APIKey:
    def __init__(self, key, description=None):
        self.key = key
        self.description = description

def verify_password(password, password_hash):
    """Verify a password against its hash."""
    try:
        return sha256_crypt.verify(password, password_hash)
    except:
        # If the hash is not in sha256_crypt format, treat as plain text for backward compatibility
        return password == password_hash

def hash_password(password):
    """Hash a password using sha256_crypt."""
    return sha256_crypt.hash(password)

def generate_api_key():
    """Generate a new API key."""
    return str(uuid.uuid4())

def migrate_passwords():
    """Migrate plain text passwords to sha256_crypt hashes."""
    config = app.wrapper.config
    modified = False

    # Check root password
    root_password = config["dashboard"].get("root-password")
    if root_password and not root_password.startswith("$5$"):  # sha256_crypt prefix
        config["dashboard"]["root-password"] = hash_password(root_password)
        modified = True

    # Check user passwords
    users = config["dashboard"].get("users", {})
    for username, password in users.items():
        if password and not password.startswith("$5$"):
            users[username] = hash_password(password)
            modified = True

    if modified:
        config.save()

def load_users():
    """Load users from config."""
    users = {}
    config = app.wrapper.config.get('dashboard', {})
    
    # Add root user if enabled
    root_password = config.get('root-password')
    if root_password:
        users['root'] = User('root', 'root')
    
    # Add other users
    for username in config.get('users', {}):
        users[username] = User(username, username)
    
    return users

def load_api_keys():
    """Load API keys from config."""
    api_keys = {}
    config = app.wrapper.config.get('dashboard', {})
    for key, description in config.get('api_keys', {}).items():
        api_keys[key] = APIKey(key, description)
    return api_keys

def verify_user(username, password):
    """Verify user credentials."""
    config = app.wrapper.config.get('dashboard', {})
    
    # Check root user
    if username == 'root':
        root_password = config.get('root-password')
        if not root_password:  # Root account disabled
            return False
        return verify_password(password, root_password)
    
    # Check other users
    users = config.get('users', {})
    if username in users:
        return verify_password(password, users[username])
    
    return False

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    users = load_users()
    return users.get(user_id)

def check_auth_header():
    """Check for valid API key in Authorization header."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        auth_type, token = auth_header.split(' ', 1)
        if auth_type.lower() != 'bearer':
            return None
        
        api_keys = load_api_keys()
        if token in api_keys:
            return True
    except:
        pass
    
    return None

def require_auth(f):
    """Decorator that requires either login or valid API key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if check_auth_header():
            return f(*args, **kwargs)
        return login_manager.unauthorized()
    return decorated 