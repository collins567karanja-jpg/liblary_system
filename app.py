from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Book, Loan

app = Flask(__name__)

# Secret key for sessions
app.config["SECRET_KEY"] = "yoursecretkey"
# MySQL database connection
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:FiNN-2187@localhost/library_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirects to login if not authenticated

# ---------------------------
# User Loader (Flask-Login)
# ---------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------------
# Dashboard (list books & loans)
# ---------------------------
@app.route("/")
@login_required
def dashboard():
    books = Book.query.all()
    loans = Loan.query.filter_by(user_id=current_user.id).all() if current_user.role == "User" else []
    return render_template("dashboard.html", books=books, loans=loans, user=current_user)

@app.route('/search', methods=['GET', 'POST'])
def search_books():
    books = []
    if request.method == 'POST':
        query = request.form.get('query')
        books = Book.query.filter(
            (Book.title.like(f"%{query}%")) |
            (Book.author.like(f"%{query}%")) |
            (Book.category.like(f"%{query}%"))
        ).all()
    return render_template('search.html', books=books)


# ---------------------------
# Borrow a Book (User)
# ---------------------------
@app.route("/borrow/<int:book_id>")
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)

    if not book.available:
        flash("This book is not available.", "danger")
        return redirect(url_for("dashboard"))

    # Create a Loan request (Pending approval by Admin)
    new_loan = Loan(user_id=current_user.id, book_id=book.id, status="Pending")
    db.session.add(new_loan)
    db.session.commit()

    flash("Borrow request submitted. Awaiting admin approval.", "info")
    return redirect(url_for("dashboard"))

# ---------------------------
# View Borrow Requests (Admin only)
# ---------------------------
@app.route("/borrow_requests")
@login_required
def borrow_requests():
    if current_user.role != "Admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    # Show all loans (Pending or Approved)
    requests = Loan.query.order_by(Loan.loan_date.desc()).all()
    return render_template("borrow_requests.html", requests=requests)

# ---------------------------
# Approve Borrow Request (Admin)
# ---------------------------
@app.route("/approve/<int:loan_id>")
@login_required
def approve_request(loan_id):
    if current_user.role != "Admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    loan = Loan.query.get_or_404(loan_id)
    book = Book.query.get_or_404(loan.book_id)

    # Mark loan as Approved
    loan.status = "Approved"
    book.available = False  # Book becomes unavailable
    db.session.commit()

    flash(f"Borrow request approved for '{book.title}'.", "success")
    return redirect(url_for("borrow_requests"))

# ---------------------------
# Mark Book as Returned (Admin)
# ---------------------------
@app.route("/return/<int:loan_id>")
@login_required
def return_book(loan_id):
    if current_user.role != "Admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    loan = Loan.query.get_or_404(loan_id)
    book = Book.query.get_or_404(loan.book_id)

    # Mark as returned
    loan.status = "Returned"
    loan.return_date = datetime.utcnow()
    book.available = True  # Book is available again

    # Calculate late fee if returned after due date
    if loan.return_date > loan.due_date:
        days_late = (loan.return_date - loan.due_date).days
        loan.late_fee = days_late * 1.0  # $1 per day late

    db.session.commit()
    flash(f"Book '{book.title}' returned. Late fee: ${loan.late_fee:.2f}", "warning" if loan.late_fee > 0 else "success")
    return redirect(url_for("borrow_requests"))

# ---------------------------
# User Authentication (Register, Login, Logout)
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        new_user = User( email=email, password=hashed_password, role="User"  )

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")
    return render_template("login.html")

# --- NEW ROUTE (Homepage/Dashboard) ---
@app.route('/')
def index():
    # later you can render a template, but for now:
    return "Welcome to the Library Management System!"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------------------
# Run the App
# ---------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)
