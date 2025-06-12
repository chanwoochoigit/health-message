#!/usr/bin/env python3
"""
Database setup script for Health Message Application

This script helps set up the PostgreSQL database for the application.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from hmsg.services.database import create_tables, SessionLocal
from hmsg.services.patient_service import create_sample_patients


def create_database_if_not_exists():
    """Create the PostgreSQL database if it doesn't exist."""
    import getpass
    default_user = getpass.getuser()
    
    try:
        print(f"🔌 Connecting to PostgreSQL as user: {default_user}")
        # Try to connect without specifying a database to create the database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user=default_user,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'health_message_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'health_message_db'...")
            cursor.execute("CREATE DATABASE health_message_db")
            print("✅ Database 'health_message_db' created successfully!")
        else:
            print("✅ Database 'health_message_db' already exists")
            
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Failed to create database: {e}")
        return False


def main():
    """Main setup function."""
    print("Health Message App - Database Setup")
    print("=" * 40)
    
    # Set up DATABASE_URL for seamless initialization
    import getpass
    default_user = getpass.getuser()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Set default DATABASE_URL for this session
        default_database_url = f"postgresql://{default_user}@localhost:5432/health_message_db"
        os.environ["DATABASE_URL"] = default_database_url
        print(f"\n🔧 Setting DATABASE_URL: {default_database_url}")
    else:
        print(f"\n✅ Using existing DATABASE_URL: {database_url}")
    
    print("\n💡 PostgreSQL Setup Instructions (if needed):")
    print("1. Install PostgreSQL:")
    print("   - macOS: brew install postgresql@14")
    print("   - Ubuntu: sudo apt-get install postgresql postgresql-contrib")
    print("   - Windows: Download from https://postgresql.org/download/")
    print("\n2. Start PostgreSQL service:")
    print("   brew services start postgresql@14  # macOS")
    print("   sudo systemctl start postgresql    # Ubuntu/Linux")
    print("\n3. The script will automatically create the database for you!")
    
    try:
        print("\n📦 Setting up database...")
        
        # Ensure DATABASE_URL is available for database operations
        from hmsg.services.database import engine
        print(f"🔗 Database engine initialized: {str(engine.url).split('@')[0]}@...")
        
        # First, try to create the PostgreSQL database
        if create_database_if_not_exists():
            print("✅ Using PostgreSQL database")
        else:
            print("⚠️  PostgreSQL unavailable, using SQLite fallback")
        
        # Then create tables
        print("\n🏗️  Creating database tables...")
        if create_tables():
            print("✅ Database tables created successfully!")
        else:
            raise Exception("Failed to create database tables")
        
        # Ask if user wants to create sample patient data for testing
        response = input("\n🔧 Do you want to create sample patients for testing? (y/n): ").lower()
        if response in ['y', 'yes']:
            # Create sample patients (safe - no login credentials)
            print("\n📊 Creating sample patients...")
            db = SessionLocal()
            try:
                create_sample_patients(db)
                print("✅ Sample patients created successfully!")
            except Exception as e:
                print(f"❌ Error creating sample patients: {e}")
            finally:
                db.close()
        
        print("\n🎉 Database setup complete!")
        print("\nTo run the application:")
        print("   reflex run")
        
    except Exception as e:
        print(f"\n❌ Database setup failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. Database exists")
        print("3. DATABASE_URL is correctly set")
        sys.exit(1)


if __name__ == "__main__":
    main() 