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


def run_validation(json_path: Path, schema_path: Path) -> bool:
    """
    Validate the resume JSON against the schema.
    Prints friendly messages and returns True if valid, False otherwise.
    """
    # Import inline so the rest of main.py doesn't break if jsonschema isn't installed yet
    try:
        from scripts.validate import validate_resume
    except ImportError:
        # Fallback: resolve path relative to project root
        import importlib.util
        project_root = Path(__file__).resolve().parent.parent
        spec = importlib.util.spec_from_file_location(
            "validate", project_root / "scripts" / "validate.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        validate_resume = mod.validate_resume

    errors = validate_resume(json_path, schema_path)
    if errors:
        print(f"✗ Validation failed — {len(errors)} error(s) in {json_path.name}:\n")
        for msg in errors:
            print(msg)
        return False
    else:
        print(f"✓ {json_path.name} is valid.")
        return True


def main():
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Generate PDF Resume from JSON")
    parser.add_argument(
        "--input", "-i",
        default="fs_resume.json",
        help="Input JSON filename (in data/ directory)"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Only validate the JSON file against the schema; do not generate a PDF."
    )
    parser.add_argument(
        "--schema",
        default=None,
        help="Path to schema file (default: schema/resume.schema.json in project root)."
    )
    args = parser.parse_args()

    try:
        # 1. Initialize Config
        config = Config.get_instance()

        # Resolve paths
        json_filename = args.input
        json_path = config.DATA_DIR / json_filename

        # Fallback for absolute paths
        if not json_path.exists():
            if os.path.exists(json_filename):
                json_path = Path(json_filename)
            else:
                raise FileNotFoundError(f"Input file not found: {json_path}")

        # Resolve schema path
        project_root = Path(__file__).resolve().parent.parent
        schema_path = Path(args.schema) if args.schema else project_root / "schema" / "resume.schema.json"

        # ----------------------------------------------------------------
        # --lint mode: validate only, no build
        # ----------------------------------------------------------------
        if args.lint:
            print(f"Linting: {json_path.name}")
            print()
            is_valid = run_validation(json_path, schema_path)
            sys.exit(0 if is_valid else 1)

        # ----------------------------------------------------------------
        # Build mode: validate first, then generate PDF
        # ----------------------------------------------------------------
        print(f"Configuration loaded. Output directory: {config.OUTPUT_DIR}")
        print("Validating JSON...")

        if schema_path.exists():
            is_valid = run_validation(json_path, schema_path)
            if not is_valid:
                print("\nBuild aborted. Fix the errors above and try again.")
                sys.exit(1)
        else:
            print(f"  (Schema not found at {schema_path}, skipping validation)")

        print()

        # 2. Generator Instance
        generator = ResumeGenerator()

        # 3. Load Data & Determine Filename
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        code = data.get("meta", {}).get("code", "RESUME")
        date_str = datetime.now().strftime("%y%m")
        base_name = f"Aryan_{code}_{date_str}"

        # Get unique output path
        output_file = get_unique_output_path(config.OUTPUT_DIR, base_name, ".tex")
        pdf_file = output_file.with_suffix(".pdf")

        print(f"Target Output: {pdf_file.name}")

        # 4. Generate LaTeX
        print("Generating LaTeX content...")
        tex_content = generator.generate_tex(json_path.name, "base_resume.tex")

        # 5. Write to Output
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(tex_content)

        print(f"Success: LaTeX file generated at {output_file}")

        # 6. Compile to PDF
        from src.compiler import PDFCompiler
        compiler = PDFCompiler()
        pdf_path = compiler.compile_tex(output_file)

        print(f"🎉 Success: PDF generated at {pdf_path}")

        # 7. Optionally upload to Google Drive
        _maybe_upload_to_drive(pdf_path, code)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def _maybe_upload_to_drive(pdf_path: Path, meta_code: str):
    """
    Ask the user if they want to upload the freshly generated PDF to Drive.
    Silently skips if the token isn't present — never crashes the build.
    """
    from src.auth import default_credentials

    creds = default_credentials()
    if creds is None:
        # Token not set up yet — inform once, don't block
        print()
        print("ℹ️  Tip: Upload to Google Drive by running:")
        print("       python scripts/drive_setup.py  (on your host machine, once)")
        return

    try:
        answer = input(
            f"\n📁 Upload to Google Drive (Resume/{meta_code.upper()}/)? [y/N]: "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        # Non-interactive environment (e.g. piped input)
        return

    if answer != "y":
        return

    print(f"   Uploading {pdf_path.name} ...")
    try:
        from src.drive import DriveUploader
        uploader = DriveUploader(creds)
        link = uploader.upload_pdf(pdf_path, meta_code=meta_code)
        print(f"   ✓ Uploaded!  {link}")
    except Exception as e:
        print(f"   ✗ Upload failed: {e}")
        print("     The PDF is still saved locally. Try: python scripts/upload.py --all")


if __name__ == "__main__":
    main()
