import argparse
import sys
import os
import json
from pathlib import Path

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_pipeline import AIPipeline
from scripts.validate import validate_resume

def main():
    parser = argparse.ArgumentParser(description="Parse a PDF resume into structured JSON using Gemini 1.5 Pro")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("--output", "-o", help="Path to save the output JSON. Defaults to data/parsed_RESUME.json")
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF File not found at {pdf_path}")
        sys.exit(1)
        
    project_root = Path(__file__).resolve().parent.parent
    schema_path = project_root / "schema" / "resume.schema.json"
    
    try:
        pipeline = AIPipeline(schema_path)
    except Exception as e:
        print(f"Failed to initialize AI Pipeline: {e}")
        sys.exit(1)
    
    try:
        print(f"\n🚀 Starting Gemini 1.5 Pro PDF extraction for {pdf_path.name}...\n")
        parsed_data = pipeline.parse_pdf_to_json(pdf_path)
        
        # Validate against schema
        print("\n🔎 Validating generated JSON against strict offline schema...")
        output_temp_path = project_root / "data" / "temp_validate.json"
        
        # Write temporarily
        with open(output_temp_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2)
            
        errors = validate_resume(output_temp_path, schema_path)
        
        if errors:
            print("\n⚠️ Warning: The generated JSON has schema validation errors:")
            for e in errors:
                print(f"   - {e}")
            print("\nYou may need to manually fix these in the output file.")
        else:
            print("✅ Success! The generated JSON is 100% compliant with the schema.")
            
        # Determine output path
        if args.output:
            final_output = Path(args.output)
        else:
            # Let the AI dictate the code if it found one
            code = parsed_data.get("meta", {}).get("code", "NEW")
            final_output = project_root / "data" / f"parsed_{code}_resume.json"
            
        # Move temp to final
        os.replace(output_temp_path, final_output)
        
        print(f"\n💾 Saved parsed JSON to: {final_output}\n")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
