"""Authentication helpers: PBKDF2 password hashing and role checks."""
import hashlib
import hmac
import secrets
import sqlite3
import os
from database import create_user, get_user


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 260000)
    return f'{salt.hex()}${digest.hex()}'


def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split('$', 1)
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), 260000)
        return hmac.compare_digest(digest, bytes.fromhex(digest_hex))
    except (ValueError, AttributeError, TypeError):
        return False


def register_student(username, full_name, email, password):
    username, full_name, email = username.strip(), full_name.strip(), email.strip().lower()
    if len(username) < 3 or not username.replace('_','').isalnum():
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
        return {key:user[key] for key in ('id','username','full_name','role')}
    return None


def seed_admin():
    password = os.environ.get('ADMIN_PASSWORD')
    if not password:
        try:
            import streamlit as st
            password = st.secrets.get('ADMIN_PASSWORD')
        except Exception:
            pass
    if not get_user('admin') and password and len(password) >= 8:
        create_user('admin', 'System Administrator', 'admin@local.test', hash_password(password), 'admin')
