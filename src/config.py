import os
from pathlib import Path

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()

        # Base directory is the parent of the src directory
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        
        # Database Config
        self.ENV = os.getenv("ENV", "local")
        self.DB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/resume_builder")

        self.TEMPLATE_DIR = self.BASE_DIR / 'templates'
        self.OUTPUT_DIR = self.BASE_DIR / 'output'

        # Ensure output directory exists
        if not self.OUTPUT_DIR.exists():
            self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance
