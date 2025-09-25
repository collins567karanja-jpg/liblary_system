import os

class Config:
    # Secret key used by Flask for sessions and flash messages.
    # In production, set this as an environment variable for security.
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret_key_change_me"

    # SQLAlchemy DB URI for MySQL using pymysql driver.
    # Replace username, password, host, port and database name accordingly.
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:FiNN-2187@localhost:3306/library_db"
    )

    # Disable SQLAlchemy event system — it saves memory and is recommended.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
