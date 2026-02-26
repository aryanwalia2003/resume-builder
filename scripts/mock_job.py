import json
import time
from datetime import datetime
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/resume_builder?directConnection=true")
db = client.get_database("resume_builder")

# Read a sample payload
with open("data/data_engineer_resume.json", "r", encoding="utf-8") as f:
    resume_data = json.load(f)

print("Inserting a mock PENDING job into 'generations'...")

# Insert mock job
result = db.generations.insert_one({
    "resume_id": "test_resume_001",
    "version_number": 1,
    "status": "PENDING",
    "output_filename": "TestUser_DE_2602_v1",
    "resume_data": resume_data,
    "meta_code": "DE",
    "drive_link": None,
    "pdf_path": None,
    "error_log": None,
    "createdAt": datetime.utcnow(),
    "updatedAt": datetime.utcnow()
})

print(f"Inserted Job ID: {result.inserted_id}")
print("Waiting 10 seconds to allow the worker to pick it up...")

time.sleep(10)

# Check the job status
job = db.generations.find_one({"_id": result.inserted_id})
print(f"\n--- Job Status After 10s ---")
if job:
    print(f"Status: {job.get('status')}")
    print(f"PDF Path: {job.get('pdf_path')}")
    print(f"Error Log: {job.get('error_log')}")
else:
    print("Job not found in database!")
