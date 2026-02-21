"""
scripts/validate.py
-------------------
Standalone CLI to validate a resume JSON file against schema/resume.schema.json.

Usage:
    python scripts/validate.py data/fs_resume.json
    python scripts/validate.py data/backend_resume.json --schema schema/resume.schema.json

Exit codes:
    0 — file is valid
    1 — validation errors found or file not found
"""

import sys
import json
import argparse
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft7Validator, FormatChecker
except ImportError:
    print("ERROR: 'jsonschema' is not installed. Run: pip install jsonschema")
    sys.exit(1)


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def _friendly_path(error: jsonschema.ValidationError) -> str:
    """
    Convert a jsonschema error's absolute path into a readable string.
    e.g. deque(['work', 0, 'highlights']) -> "work[0].highlights"
    """
    parts = []
    for part in error.absolute_path:
        if isinstance(part, int):
            parts.append(f"[{part}]")
        else:
            if parts:
                parts.append(f".{part}")
            else:
                parts.append(str(part))
    return "".join(parts) if parts else "(root)"


def validate_resume(json_path: Path, schema_path: Path) -> list[str]:
    """
    Validate a resume JSON file against the schema.

    Returns a list of human-readable error strings.
    An empty list means the file is valid.
    """
    # Load schema
    if not schema_path.exists():
        return [f"Schema file not found: {schema_path}"]

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Load resume JSON
    if not json_path.exists():
        return [f"Resume file not found: {json_path}"]

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            return [f"Invalid JSON — {e}"]

    # Validate
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))

    messages = []
    for error in errors:
        path = _friendly_path(error)
        messages.append(f"  ✗  {path}  →  {error.message}")

    return messages


# -----------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------

def main():
    # Resolve project root relative to this script's location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    parser = argparse.ArgumentParser(
        description="Validate a resume JSON file against the schema.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate.py data/fs_resume.json
  python scripts/validate.py data/backend_resume.json
  python scripts/validate.py data/fs_resume.json --schema schema/resume.schema.json
        """
    )
    parser.add_argument(
        "input",
        help="Path to the resume JSON file (relative to project root or absolute)."
    )
    parser.add_argument(
        "--schema",
        default=str(project_root / "schema" / "resume.schema.json"),
        help="Path to the schema file (default: schema/resume.schema.json)."
    )
    args = parser.parse_args()

    json_path = Path(args.input)
    # If relative, resolve from project root
    if not json_path.is_absolute():
        json_path = project_root / json_path

    schema_path = Path(args.schema)
    if not schema_path.is_absolute():
        schema_path = project_root / schema_path

    print(f"Validating: {json_path.name}")
    print(f"Schema:     {schema_path.relative_to(project_root)}")
    print()

    errors = validate_resume(json_path, schema_path)

    if not errors:
        print("✓ Valid — no errors found.")
        sys.exit(0)
    else:
        print(f"✗ Found {len(errors)} error(s):\n")
        for msg in errors:
            print(msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
