# create_db.py
"""
This script manages the database for the Library Management System.
It can either:
1. Create tables if they don't exist.
2. Drop ALL tables and recreate them (useful for testing / resetting).
"""

from app import app, db

def create_tables():
    """Create all tables defined in models.py"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print("❌ Error while creating tables:", e)

def reset_database():
    """Drop ALL tables and recreate them"""
    with app.app_context():
        try:
            db.drop_all()
            print("⚠️ All tables dropped.")
            db.create_all()
            print("✅ Database tables recreated successfully!")
        except Exception as e:
            print("❌ Error while resetting database:", e)

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Create tables")
    print("2. Drop & Recreate tables")
    choice = input("Enter 1 or 2: ")

    if choice == "1":
        create_tables()
    elif choice == "2":
        reset_database()
    else:
        print("❌ Invalid choice. Exiting.")


