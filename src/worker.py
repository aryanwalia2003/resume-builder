import time
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project root to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import Database
from src.config import Config
from src.generator import ResumeGenerator
from src.compiler import PDFCompiler
from src.auth import default_credentials
from src.drive import DriveUploader

class ResumeWorker:
    def __init__(self):
        self.config = Config.get_instance()
        Database.connect()
        self.db = Database.get_db()
        self.generator = ResumeGenerator()
        self.compiler = PDFCompiler()
        
        # Init Drive Uploader if credentials exist
        creds = default_credentials()
        self.uploader = DriveUploader(creds) if creds else None
        if not self.uploader:
            print("[WARN] Google Drive credentials not found. Uploads will be skipped.")

    def run(self):
        """Starts the worker loop."""
        print("\n[START] Resume Engine Worker Started")
        print("===============================\n")

        # 1. Sweep backlog (jobs missed while worker was down)
        self._sweep_backlog()

        # 2. Start watching Change Streams for live inserts
        self._watch_live_jobs()

    def _sweep_backlog(self):
        """Finds any existing PENDING jobs and processes them."""
        print("[SWEEP] Sweeping for backlog PENDING jobs...")
        count = 0
        while True:
            # Atomic find and claim
            job = self.db.generations.find_one_and_update(
                {"status": "PENDING"},
                {"$set": {"status": "PROCESSING", "updatedAt": datetime.utcnow()}},
                sort=[("createdAt", 1)]
            )
            if not job:
                break
                
            count += 1
            print(f"\n[BACKLOG] Found matching job: {job['output_filename']}")
            self._process_job(job)
            
        print(f"[DONE] Swept {count} backlog jobs.\n")

    def _watch_live_jobs(self):
        """Uses Change Streams to instantly react to new PENDING jobs."""
        print("[WATCH] Watching for live inserts via Change Stream...\n")
        
        pipeline = [
            {"$match": {"operationType": "insert", "fullDocument.status": "PENDING"}}
        ]
        
        while True:
            try:
                # This blocks until a new document is inserted
                with self.db.generations.watch(pipeline) as stream:
                    for change in stream:
                        job_id = change["documentKey"]["_id"]
                        
                        # Atomically claim it (in case multiple workers received the event)
                        job = self.db.generations.find_one_and_update(
                            {"_id": job_id, "status": "PENDING"},
                            {"$set": {"status": "PROCESSING", "updatedAt": datetime.utcnow()}}
                        )
                        
                        if job:
                            print(f"\n[LIVE] New job arrived: {job.get('output_filename', 'Unknown')}")
                            self._process_job(job)
                            print("\n[WATCH] Resuming watch...")
                            
            except Exception as e:
                # If connection drops, wait and reconnect
                print(f"[WARN] Change stream error (sleeping 5s): {e}")
                time.sleep(5)

    def _process_job(self, job: dict):
        """Full pipeline: JSON -> LaTeX -> PDF -> Drive -> Update DB"""
        job_id = job["_id"]
        filename = job["output_filename"]
        data = job["resume_data"]
        meta_code = job.get("meta_code", "RES")
        
        print(f"[JOB] Processing: {filename} (ID: {job_id})")
        
        try:
            # 1. Render LaTeX
            tex_content = self.generator.generate_tex_from_data(data)
            
            # Write LaTeX to temporary output file
            tex_path = self.config.OUTPUT_DIR / f"{filename}.tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)
                
            # 2. Compile PDF
            pdf_path = self.compiler.compile_tex(tex_path)
            
            # Optional: Move to clean naming convention relative to output folder
            # compiler.compile_tex already places it in self.config.OUTPUT_DIR
            relative_pdf_path = f"/output/{pdf_path.name}"
            
            # Clean up the .tex file since we only need the PDF
            if tex_path.exists():
                tex_path.unlink()
                
            print(f"   [OK] Compiled: {relative_pdf_path}")
                
            # 3. Upload to Google Drive (if configured)
            drive_link = None
            if self.uploader:
                print("   [UPLOAD] Uploading to Drive...")
                drive_link = self.uploader.upload_pdf(pdf_path, meta_code=meta_code)
                print(f"   [OK] Drive Link: {drive_link}")
                
            # 4. Mark Completed
            self.db.generations.update_one(
                {"_id": job_id},
                {"$set": {
                    "status": "COMPLETED",
                    "pdf_path": relative_pdf_path,
                    "drive_link": drive_link,
                    "updatedAt": datetime.utcnow()
                }}
            )
            print(f"[SUCCESS] Job COMPLETED: {filename}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Job FAILED: {filename} - {error_msg}")
            
            # Log full traceback for debugging
            import traceback
            traceback.print_exc()
            
            self.db.generations.update_one(
                {"_id": job_id},
                {"$set": {
                    "status": "FAILED",
                    "error_log": error_msg,
                    "updatedAt": datetime.utcnow()
                }}
            )

if __name__ == "__main__":
    try:
        worker = ResumeWorker()
        worker.run()
    except KeyboardInterrupt:
        print("\n[EXIT] Worker shut down gracefully.")
        sys.exit(0)
