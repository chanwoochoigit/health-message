"""Application configuration settings."""
import os

class Settings:
    """Main settings class for the application."""
    # Read the DATABASE_URL from the environment variable provided by docker-compose.
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    
    # If the environment variable is not set, raise an error to fail fast.
    if not DATABASE_URL:
        raise ValueError("FATAL: DATABASE_URL environment variable is not set.")

# Create a single settings instance to be used throughout the app
settings = Settings()

print(f"✅ [config.py] DATABASE_URL loaded from environment: {settings.DATABASE_URL.split('@')[0]}...") 