"""Authentication helpers: PBKDF2 password hashing, role checks, and secret resolution."""
import hashlib
import hmac
import os
import secrets
import sqlite3
from database import create_user, get_user, update_user_password

# Attempt to load local .env if python-dotenv is installed and .env exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def get_secret(key: str, default: str = "") -> str:
    """
    Retrieve credentials or configuration with full support for:
      1. OS environment variables (e.g., ADMIN_PASSWORD, admin_password)
      2. Streamlit Cloud Secrets (st.secrets["ADMIN_PASSWORD"], st.secrets.admin.password)
      3. Local .env file
    """
    # 1. Environment variable lookup (direct, uppercase, lowercase)
    for variant in (key, key.upper(), key.lower()):
        val = os.environ.get(variant)
        if val is not None and str(val).strip() != "":
            return str(val).strip()

    # 2. Streamlit Secrets lookup
    try:
        import streamlit as st
        # Direct key
        for variant in (key, key.upper(), key.lower()):
            if variant in st.secrets:
                val = st.secrets[variant]
                if val is not None and str(val).strip() != "":
                    return str(val).strip()

        # Section lookup: e.g. [admin] password = "..."
        if "admin" in st.secrets and isinstance(st.secrets["admin"], dict):
            sec = st.secrets["admin"]
            sub = key.lower().replace("admin_", "").replace("admin", "")
            if sub in sec and str(sec[sub]).strip() != "":
                return str(sec[sub]).strip()
            if key.lower() in sec and str(sec[key.lower()]).strip() != "":
                return str(sec[key.lower()]).strip()
    except Exception:
        # st.secrets raises StreamlitSecretNotFoundError when no secrets file exists
        pass

    return default


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 260000)
    return f'{salt.hex()}${digest.hex()}'


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split('$', 1)
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), 260000)
        return hmac.compare_digest(digest, bytes.fromhex(digest_hex))
    except (ValueError, AttributeError, TypeError):
        return False


def register_student(username, full_name, email, password):
    username = username.strip()
    full_name = full_name.strip()
    email = email.strip().lower()
    if len(username) < 3 or not username.replace('_', '').isalnum():
        raise ValueError('Username must have at least 3 letters/numbers (underscores allowed).')
    if not full_name or '@' not in email or '.' not in email.split('@')[-1]:
        raise ValueError('Enter a full name and valid email.')
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters.')
    try:
        return create_user(username, full_name, email, hash_password(password))
    except sqlite3.IntegrityError as exc:
        raise ValueError('Username or email already registered.') from exc


def authenticate(username, password):
    user = get_user(username.strip())
    if user and verify_password(password, user['password_hash']):
        return {key: user[key] for key in ('id', 'username', 'full_name', 'role')}
    return None


def seed_admin() -> bool:
    """
    Seed or synchronize the administrator account.
    Compatible with Streamlit Cloud secrets and OS environment variables.
    If ADMIN_PASSWORD is changed in secrets/env, updates the admin password hash.
    """
    username = get_secret('ADMIN_USERNAME', 'admin')
    password = get_secret('ADMIN_PASSWORD')
    full_name = get_secret('ADMIN_NAME', 'System Administrator')
    email = get_secret('ADMIN_EMAIL', 'admin@feedback.local')

    if not password or len(password) < 8:
        return False

    existing = get_user(username)
    if not existing:
        create_user(username, full_name, email, hash_password(password), role='admin')
        return True
    elif existing.get('role') == 'admin':
        # If admin exists but password in secrets/env changed, synchronize stored hash
        if not verify_password(password, existing['password_hash']):
            update_user_password(username, hash_password(password))
        return True
    return False


def is_admin_configured() -> bool:
    """Check if the admin user exists in the database."""
    username = get_secret('ADMIN_USERNAME', 'admin')
    user = get_user(username)
    return bool(user and user.get('role') == 'admin')
