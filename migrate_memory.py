"""
Database migration script for memory tables
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.main import create_app
from src.models.models import db

def migrate():
    """Create memory tables"""
    app = create_app('development')
    
    with app.app_context():
        print("Creating memory tables...")
        db.create_all()
        print("✅ Memory tables created successfully!")
        
        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Database tables ({len(tables)}):")
        for table in sorted(tables):
            print(f"  - {table}")

if __name__ == '__main__':
    migrate()
