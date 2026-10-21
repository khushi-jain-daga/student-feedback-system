"""Authentication and credential management for the Student Feedback Management System.
Includes PBKDF2 password hashing, user registration, role validation, and secret resolution.
"""
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from typing import Optional, Dict, Any

from database import (
    create_user,
    get_user_by_id,
    get_user_by_username_or_email,
    get_user_by_identifier,
    update_user_password,
    get_engine,
    fetch_one,
    execute_query
)

# Attempt to load local .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def get_secret(key: str, default: str = "") -> str:
    """
    Retrieve credentials or configuration with full support for:
      1. OS environment variables (e.g. ADMIN_PASSWORD, DATABASE_URL)
      2. Streamlit Cloud Secrets (st.secrets["ADMIN_PASSWORD"], st.secrets.admin.password)
      3. Local .env file
    """
    # 1. Environment variable lookup
    for variant in (key, key.upper(), key.lower()):
        val = os.environ.get(variant)
        if val is not None and str(val).strip() != "":
            return str(val).strip()

    # 2. Streamlit Secrets lookup
    try:
        import streamlit as st
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
        pass

    return default


def hash_password(password: str) -> str:
    """Hash password using PBKDF2 with SHA-256 and a cryptographically secure random salt."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 260000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored salt$digest with timing-safe comparison."""
    try:
        salt_hex, digest_hex = stored.split('$', 1)
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), 260000)
        return hmac.compare_digest(digest, bytes.fromhex(digest_hex))
    except (ValueError, AttributeError, TypeError):
        return False


def register_user(
    name: str,
    username: str,
    email: str,
    password: str,
    role: str = 'user',
    registration_no: Optional[str] = None
) -> int:
    """
    Register a new user account with validation.
    Ensures role is 'user' or 'admin', and username/email are unique.
    Optionally associates with a student registration number.
    """
    name = name.strip()
    username = username.strip()
    email = email.strip().lower()
    reg_clean = registration_no.strip().upper() if registration_no and registration_no.strip() else None

    if len(name) < 2:
        raise ValueError("Please provide a valid full name (at least 2 characters).")

    if len(username) < 3 or not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError("Username must have at least 3 letters/numbers (underscores allowed).")

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        raise ValueError("Please provide a valid email address (e.g., student@university.edu).")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    # Check for duplicate username or email
    existing_user = fetch_one("SELECT id FROM users WHERE LOWER(username) = ?", (username.lower(),))
    if existing_user:
        raise ValueError(f"Username '{username}' is already registered.")

    existing_email = fetch_one("SELECT id FROM users WHERE LOWER(email) = ?", (email.lower(),))
    if existing_email:
        raise ValueError(f"Email '{email}' is already associated with an account.")

    # Check duplicate registration number if provided
    if reg_clean:
        existing_reg = fetch_one("SELECT id FROM users WHERE UPPER(registration_no) = ?", (reg_clean,))
        if existing_reg:
            raise ValueError(f"Registration number '{reg_clean}' is already linked to another account.")

    pwd_hash = hash_password(password)
    user_id = create_user(
        name=name,
        username=username,
        email=email,
        password_hash=pwd_hash,
        role=role,
        registration_no=reg_clean
    )

    # Verification: Ensure account was created and exists in database
    if not user_id or user_id <= 0:
        raise ValueError("Failed to create account. Please check your details and try again.")

    created_user = get_user_by_id(user_id)
    if not created_user:
        raise ValueError("Account creation verification failed. Please try again.")

    # Automatically link person record in `people` if registration number or name matches
    try:
        if reg_clean:
            execute_query(
                'UPDATE people SET linked_user_id = ? WHERE UPPER(registration_no) = ?',
                (user_id, reg_clean)
            )
        else:
            execute_query(
                'UPDATE people SET linked_user_id = ? WHERE linked_user_id IS NULL AND LOWER(name) = ?',
                (user_id, name.lower())
            )
    except Exception:
        pass

    return user_id


def register_student(username: str, full_name: str, email: str, password: str, registration_no: Optional[str] = None) -> int:
    """Backward-compatible registration helper for tests and legacy callers."""
    return register_user(
        name=full_name,
        username=username,
        email=email,
        password=password,
        role='user',
        registration_no=registration_no
    )


def authenticate(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user by username, email, OR registration number and password.
    Returns safe user dictionary on success, or None on failure.
    """
    if not identifier or not password:
        return None

    user = get_user_by_identifier(identifier.strip())
    if user and verify_password(password, user['password_hash']):
        # Map legacy 'student' role to 'user'
        role = 'user' if user.get('role') == 'student' else user.get('role', 'user')
        return {
            'id': user['id'],
            'name': user.get('name') or user.get('full_name') or user['username'],
            'username': user['username'],
            'email': user['email'],
            'role': role,
            'registration_no': user.get('registration_no')
        }
    return None


def change_user_password(user_id: int, current_password: str, new_password: str) -> bool:
    """Verify current password and update to new password (min 8 characters)."""
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found.")

    if not verify_password(current_password, user['password_hash']):
        raise ValueError("Incorrect current password.")

    if len(new_password) < 8:
        raise ValueError("New password must be at least 8 characters long.")

    update_user_password(user_id, hash_password(new_password))
    return True


def seed_admin() -> bool:
    """
    Seed or synchronize the administrator account.
    Compatible with Streamlit Cloud secrets and OS environment variables.
    If ADMIN_PASSWORD is changed in secrets/env, updates the admin password hash.
    """
    try:
        username = get_secret('ADMIN_USERNAME', 'admin')
        password = get_secret('ADMIN_PASSWORD')
        name = get_secret('ADMIN_NAME', 'System Administrator')
        email = get_secret('ADMIN_EMAIL', 'admin@feedback.local')

        if not password or len(password) < 8:
            print("[INIT] Admin account synchronized.")
            return False

        existing = get_user_by_username_or_email(username)
        if not existing:
            create_user(name=name, username=username, email=email, password_hash=hash_password(password), role='admin')
            print("[INIT] Admin account synchronized.")
            return True
        elif existing.get('role') == 'admin':
            # If admin exists but password in secrets/env changed, synchronize stored hash
            if not verify_password(password, existing['password_hash']):
                update_user_password(existing['id'], hash_password(password))
            print("[INIT] Admin account synchronized.")
            return True
        return False
    except Exception as e:
        print(f"[INIT ERROR] Admin synchronization encountered {type(e).__name__}")
        raise


def is_admin_configured() -> bool:
    """Check if the administrator user exists in the database."""
    username = get_secret('ADMIN_USERNAME', 'admin')
    user = get_user_by_username_or_email(username)
    if user and user.get('role') == 'admin':
        return True
    # Also check if any admin exists
    admin_row = fetch_one("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    return bool(admin_row)
