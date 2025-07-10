import hashlib
import streamlit as st
import os

def hash_email(email):
    """Create a hash of the email for anonymity"""
    return hashlib.sha256(email.encode()).hexdigest()

def verify_admin(email, password):
    """Verify admin credentials"""
    # Get admin credentials from environment variables
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    # Check if environment variables are set
    if not admin_email or not admin_password:
        return False
    
    return email == admin_email and password == admin_password

def get_user_team(email, data_manager):
    """Get the team assigned to a user"""
    return data_manager.get_user_team(email)

def is_valid_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
