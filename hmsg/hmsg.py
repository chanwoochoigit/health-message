"""Health Message Application - Main App."""

import reflex as rx

# Import pages
from .pages.auth import auth_page
from .pages.dashboard import dashboard_page
from .pages.patients import patients_page
from .pages.register import register_page

# Import services for initialization
from .services.database import create_tables


def init_db():
    """Initialize database tables."""
    try:
        if create_tables():
            print("Database tables created successfully!")
        else:
            print("Database table creation failed!")
    except Exception as e:
        print(f"Database initialization error: {e}")


# Initialize database
init_db()

# Create app
app = rx.App()

# Add routes
app.add_page(auth_page, route="/")
app.add_page(register_page, route="/register")
app.add_page(dashboard_page, route="/dashboard")
app.add_page(patients_page, route="/patients")
