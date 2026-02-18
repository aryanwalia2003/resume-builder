import sys
import os

# Add the project root to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.generator import ResumeGenerator

def main():
    try:
        # 1. Initialize Config
        config = Config.get_instance()
        print(f"Configuration loaded. Output directory: {config.OUTPUT_DIR}")

        # 2. Generator Instance
        generator = ResumeGenerator()

        # 3. Generate LaTeX
        print("Generating LaTeX content...")
        tex_content = generator.generate_tex('fs_resume.json', 'base_resume.tex')

        # 4. Write to Output
        output_file = config.OUTPUT_DIR / 'generated_resume.tex'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tex_content)

        print(f"Success: LaTeX file generated at {output_file}")
        
        # 5. Compile to PDF
        from src.compiler import PDFCompiler
        compiler = PDFCompiler()
        pdf_path = compiler.compile_tex(output_file)
        
        print(f"🎉 Success: PDF generated at {pdf_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
