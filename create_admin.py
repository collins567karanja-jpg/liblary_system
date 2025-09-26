# create_admin.py
# Run this script once to create an Admin account

from app import db
from models import User
from werkzeug.security import generate_password_hash

def create_admin(username, email, password):
    # Hash password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    # Create Admin user
    admin = User(username=username, email=email, password=hashed_password, role="Admin")

    # Add to database
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user '{username}' created successfully!")

# Example: Change these values before running
create_admin("admin", "admin@example.com", "admin123")
