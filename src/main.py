import sys
import os
import json
from pathlib import Path

# Add the project root to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.generator import ResumeGenerator

def get_unique_output_path(output_dir, base_name, ext):
    """
    Generates a unique filename: base_name.ext, base_name_v1.ext, base_name_v2.ext...
    """
    counter = 0
    while True:
        suffix = f"_v{counter}" if counter > 0 else ""
        filename = f"{base_name}{suffix}{ext}"
        path = output_dir / filename
        if not path.exists():
            return path
        counter += 1

def main():
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Generate PDF Resume from JSON")
    parser.add_argument('--input', '-i', default='fs_resume.json', help="Input JSON filename (in data/ directory)")
    args = parser.parse_args()

    try:
        # 1. Initialize Config
        config = Config.get_instance()
        print(f"Configuration loaded. Output directory: {config.OUTPUT_DIR}")

        # 2. Generator Instance
        generator = ResumeGenerator()

        # 3. Load Data & Determine Filename
        json_filename = args.input
        json_path = config.DATA_DIR / json_filename
        
        # Fallback for absolute paths
        if not json_path.exists():
             if os.path.exists(json_filename):
                 json_path = Path(json_filename)
                 # If using absolute path, we might need to adjust how generator loads it.
                 # For now, let's assume it's in data dir as per default usage.
             else:
                 raise FileNotFoundError(f"Input file not found: {json_path}")

        # Read JSON for Meta
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        code = data.get('meta', {}).get('code', 'RESUME')
        date_str = datetime.now().strftime("%y%m")
        base_name = f"Aryan_{code}_{date_str}"
        
        # Get unique output path
        output_file = get_unique_output_path(config.OUTPUT_DIR, base_name, ".tex")
        pdf_file = output_file.with_suffix('.pdf')

        print(f"Target Output: {pdf_file.name}")

        # 4. Generate LaTeX
        print("Generating LaTeX content...")
        # Note: generator.generate_tex currently expects a filename *relative to DATA_DIR*
        # If args.input is just a filename, this works perfect.
        tex_content = generator.generate_tex(json_path.name, 'base_resume.tex')

        # 5. Write to Output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tex_content)

        print(f"Success: LaTeX file generated at {output_file}")
        
        # 6. Compile to PDF
        from src.compiler import PDFCompiler
        compiler = PDFCompiler()
        pdf_path = compiler.compile_tex(output_file)
        
        print(f"🎉 Success: PDF generated at {pdf_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
