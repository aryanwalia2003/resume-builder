#!/usr/bin/env python3
"""
scripts/migrate.py
-------------------
A simple MongoDB migration runner.
It checks the `migrations` collection and runs any scripts
in the `migrations/` folder that haven't been applied yet.

Usage (inside Docker):
    docker-compose run --rm builder python scripts/migrate.py
"""

import sys
import importlib.util
from pathlib import Path
from datetime import datetime

# Resolve project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.db import Database


def load_module(filepath: Path):
    """Dynamically loads a python module from a filepath."""
    module_name = filepath.stem
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    print("=" * 50)
    print("  MongoDB Migrations Runner")
    print("=" * 50)
    
    Database.connect()
    db = Database.get_db()

    # 1. Get applied migrations from DB
    applied_docs = db.migrations.find({}, {"name": 1})
    applied_names = {doc["name"] for doc in applied_docs}
    
    # 2. Find migration scripts
    migrations_dir = PROJECT_ROOT / "migrations"
    migrations_dir.mkdir(exist_ok=True)
    
    script_files = sorted(migrations_dir.glob("*.py"))
    
    if not script_files:
        print("No migration scripts found in migrations/ folder.")
        sys.exit(0)

    # 3. Apply missing migrations sequentially
    run_count = 0
    for file_path in script_files:
        name = file_path.name
        if name in applied_names:
            continue
            
        print(f"\n→ Running migration: {name}")
        try:
            mod = load_module(file_path)
            # Each script must have an 'up(db)' function
            if not hasattr(mod, "up"):
                raise ValueError(f"Migration {name} is missing 'up(db)' function.")
                
            mod.up(db)
            
            # Record success
            db.migrations.insert_one({
                "name": name,
                "applied_at": datetime.utcnow()
            })
            print(f"✓ Migration {name} successful.")
            run_count += 1
            
        except Exception as e:
            print(f"✗ Migration {name} FAILED: {e}")
            sys.exit(1)
            
    if run_count == 0:
        print("\nAll migrations are already up to date.")
    else:
        print(f"\nCompleted {run_count} migrations.")
        
    Database.close()


if __name__ == "__main__":
    main()
