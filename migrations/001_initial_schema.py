"""
Migration 001: Initial Schema & Indexes
---------------------------------------
Creates the necessary indexes for the 5 core collections
implementing Option A (microservice decoupled uploads).
"""

from pymongo.database import Database
import pymongo


def up(db: Database):
    """
    Run the migrations to create indexes.
    MongoDB is schema-less, so creating the index implicitly
    creates the collection and enforces data constraints.
    """
    
    print("  - Creating indexes for matching schema pattern...")
    
    # 1. Users
    # ------------------
    # Every user needs a unique email.
    db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
    
    # 2. Resumes (Active)
    # ------------------
    # For querying a user's active resumes quickly.
    db.resumes.create_index([
        ("user_id", pymongo.ASCENDING),
        ("updated_at", pymongo.DESCENDING)
    ])
    
    # 3. ResumeVersions (Time Machine Snapshot)
    # ----------------------------------------
    # Ensure no duplicate versions exist for the same resume.
    db.resume_versions.create_index([
        ("resume_id", pymongo.ASCENDING),
        ("version_number", pymongo.DESCENDING)
    ], unique=True)
    
    # 4. Generations (PDF build jobs)
    # --------------------------------
    # Quick lookup for recent builds per resume.
    db.generations.create_index([
        ("resume_id", pymongo.ASCENDING),
        ("created_at", pymongo.DESCENDING)
    ])
    
    # 5. Uploads (Drive sync jobs)
    # -----------------------------
    # Each PDF generation has exactly one Drive upload job.
    db.uploads.create_index([("generation_id", pymongo.ASCENDING)], unique=True)
    # For finding jobs that are still pending.
    db.uploads.create_index([("status", pymongo.ASCENDING)])
    
    print("  - All indexes created successfully.")
