from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

# Initialize SQLAlchemy
db = SQLAlchemy()

# ---------------------------
# User Model
# ---------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default="User")  # "Admin" or "User"

    # Relationships
    loans = db.relationship("Loan", backref="user", lazy=True)

# ---------------------------
# Book Model
# ---------------------------
class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    available = db.Column(db.Boolean, default=True)  # True = available, False = borrowed

    # Relationships
    loans = db.relationship("Loan", backref="book", lazy=True)

# ---------------------------
# Loan Model
# ---------------------------
class Loan(db.Model):
    __tablename__ = "loans"
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys to User & Book
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)

    # Dates
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)       # When borrowed
    due_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))  # 2 weeks from loan
    return_date = db.Column(db.DateTime, nullable=True)               # When returned

    # Status
    status = db.Column(db.String(20), default="Pending")  
    # "Pending" = waiting admin approval, "Approved" = borrowed, "Returned" = completed

    # Late Fee
    late_fee = db.Column(db.Float, default=0.0)
