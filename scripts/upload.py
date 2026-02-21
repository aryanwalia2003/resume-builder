#!/usr/bin/env python3
"""
scripts/upload.py
-----------------
Batch upload resume PDFs from output/ to Google Drive.

Reads meta.code from the filename pattern: Aryan_<CODE>_YYMM[_vN].pdf
Uploads each file to: My Drive/Resume/<CODE>/

Usage (inside Docker):
    # Upload a specific file
    docker-compose run --rm builder python scripts/upload.py output/Aryan_PI_2602.pdf

    # Upload multiple files
    docker-compose run --rm builder python scripts/upload.py output/Aryan_PI_2602.pdf output/Aryan_BE_2602.pdf

    # Upload ALL PDFs in output/
    docker-compose run --rm builder python scripts/upload.py --all
"""

import sys
import re
import argparse
from pathlib import Path

# Resolve project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.auth import default_credentials
from src.drive import DriveUploader


FILENAME_PATTERN = re.compile(r"^[A-Za-z]+_([A-Z]+)_\d{4}(?:_v\d+)?\.pdf$", re.IGNORECASE)


def infer_code(filename: str) -> str | None:
    """
    Extract meta.code from a filename like Aryan_PI_2602.pdf or Aryan_BE_2602_v1.pdf
    Returns the code string (e.g. 'PI') or None if pattern doesn't match.
    """
    match = FILENAME_PATTERN.match(filename)
    return match.group(1).upper() if match else None


def upload_file(uploader: DriveUploader, pdf_path: Path) -> bool:
    """
    Upload a single PDF. Returns True on success.
    """
    code = infer_code(pdf_path.name)
    if code is None:
        print(f"  ✗ Skipping '{pdf_path.name}' — could not infer role code from filename.")
        print(    "    Expected pattern: Aryan_<CODE>_YYMM.pdf  (e.g. Aryan_PI_2602.pdf)")
        return False

    print(f"  → Uploading '{pdf_path.name}' to Drive/Resume/{code}/ ...")
    try:
        link = uploader.upload_pdf(pdf_path, meta_code=code)
        print(f"  ✓ Done!  {link}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Upload resume PDFs from output/ to Google Drive.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/upload.py output/Aryan_PI_2602.pdf
  python scripts/upload.py output/Aryan_PI_2602.pdf output/Aryan_BE_2602.pdf
  python scripts/upload.py --all
        """
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="PDF file paths to upload."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Upload all PDFs found in the output/ directory."
    )
    args = parser.parse_args()

    if not args.files and not args.all:
        parser.print_help()
        sys.exit(1)

    # Resolve files to upload
    if args.all:
        output_dir = PROJECT_ROOT / "output"
        pdf_files = sorted(output_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {output_dir}/")
            sys.exit(0)
        print(f"Found {len(pdf_files)} PDF(s) in output/:\n")
    else:
        pdf_files = [Path(f) for f in args.files]

    # Get credentials
    print("Connecting to Google Drive...")
    creds = default_credentials()
    if creds is None:
        print()
        print("ERROR: Drive token not found.")
        print("Run this on your host machine first:")
        print("  python scripts/drive_setup.py")
        sys.exit(1)

    uploader = DriveUploader(creds)
    print("✓ Connected.\n")

    # Upload each file
    success, failed = 0, 0
    for pdf_path in pdf_files:
        pdf_path = PROJECT_ROOT / pdf_path if not pdf_path.is_absolute() else pdf_path
        ok = upload_file(uploader, pdf_path)
        if ok:
            success += 1
        else:
            failed += 1

    # Summary
    print()
    print(f"Upload complete — {success} succeeded, {failed} failed.")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
