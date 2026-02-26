import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class AIPipeline:
    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
        
        # Ensure API key exists
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment or .env file.")
            
        self.client = genai.Client(api_key=self.api_key)
        
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def parse_pdf_to_json(self, pdf_path: Path) -> dict:
        """
        Uploads a PDF to Gemini, extracts the resume, and guarantees a JSON 
        response conforming to our internal resume schema. Retries on failure.
        """
        print(f"Uploading {pdf_path.name} to Gemini File API...")
        uploaded_file = self.client.files.upload(file=str(pdf_path), config={'mime_type': 'application/pdf'})
        
        try:
            print("Extracting document features...")
            time.sleep(2)
            
            prompt = f"""
            You are an expert ATS resume parser and data extraction AI. 
            I have provided a PDF resume. Please extract all the information from this resume and output it as a valid JSON object.
            
            The JSON output MUST STRICTLY conform to the following JSON Schema:
            
            ```json
            {json.dumps(self.schema, indent=2)}
            ```
            
            Rules:
            1. Be extremely accurate with dates, companies, and roles.
            2. DO NOT make up any information. If something is missing (e.g., social links), omit the field or leave it empty as per the schema requirements.
            3. Break down work experience highlights into individual bullet points. Maintain any markdown formatting if present.
            4. Organize skills logically into categories (e.g. Languages, Frameworks, Tools).
            5. For `meta.code`, determine a short 2-3 letter uppercase code representing the main profession of the candidate (e.g., 'SWE', 'FS', 'BE', 'ROB', 'DATA', 'PHY').
            
            Return ONLY valid JSON.
            """
            
            print("Generating structured JSON using Gemini 2.0 Flash...")
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            return json.loads(response.text)
            
        except json.JSONDecodeError as e:
            print("Failed to decode JSON from Gemini. Raw response:")
            print(response.text)
            raise e
        finally:
            print("Cleaning up remote file...")
            self.client.files.delete(name=uploaded_file.name)
