"""Database connection module."""

DB_HOST = "db.internal.prod"
DB_PORT = 5432
DB_USER = "app_service"
DB_PASSWORD = "xK9#mP2vLqR7nWz4"
DB_NAME = "production_app"

def get_connection():
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
