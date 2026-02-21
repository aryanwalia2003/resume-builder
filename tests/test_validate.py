"""
tests/test_validate.py
-----------------------
pytest suite for the JSON schema validator.

Run: pytest tests/test_validate.py -v
"""

import json
import copy
import pytest
from pathlib import Path

# Resolve project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / "schema" / "resume.schema.json"
DATA_DIR = PROJECT_ROOT / "data"

# Import the validator function
import importlib.util
spec = importlib.util.spec_from_file_location(
    "validate", PROJECT_ROOT / "scripts" / "validate.py"
)
validate_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_mod)
validate_resume = validate_mod.validate_resume


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_tmp_json(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "test_resume.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return p


# -----------------------------------------------------------------------
# 1. All existing data files must pass validation
# -----------------------------------------------------------------------

@pytest.mark.parametrize("json_file", [
    "fs_resume.json",
    "backend_resume.json",
    "applied_ai_resume.json",
    "data_engineer_resume.json",
])
def test_existing_files_are_valid(json_file):
    """Every JSON in data/ must pass with zero errors."""
    json_path = DATA_DIR / json_file
    if not json_path.exists():
        pytest.skip(f"{json_file} does not exist in data/")
    errors = validate_resume(json_path, SCHEMA_PATH)
    assert errors == [], f"{json_file} has validation errors:\n" + "\n".join(errors)


# -----------------------------------------------------------------------
# 2. Missing required fields → error reported
# -----------------------------------------------------------------------

def test_missing_meta_code(tmp_path):
    """Missing meta.code should produce an error."""
    data = load_json(DATA_DIR / "backend_resume.json")
    del data["meta"]["code"]
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0
    assert any("code" in e for e in errors)


def test_missing_work_company(tmp_path):
    """Missing work[0].company should produce an error."""
    data = load_json(DATA_DIR / "backend_resume.json")
    del data["work"][0]["company"]
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0
    assert any("company" in e for e in errors)


def test_missing_basics_email(tmp_path):
    """Missing basics.contact.email should produce an error."""
    data = load_json(DATA_DIR / "backend_resume.json")
    del data["basics"]["contact"]["email"]
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0
    assert any("email" in e for e in errors)


def test_missing_education_institution(tmp_path):
    """Missing education[0].institution should produce an error."""
    data = load_json(DATA_DIR / "backend_resume.json")
    del data["education"][0]["institution"]
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0
    assert any("institution" in e for e in errors)


# -----------------------------------------------------------------------
# 3. Wrong types → error reported
# -----------------------------------------------------------------------

def test_highlights_must_be_array(tmp_path):
    """highlights as a string instead of an array should fail."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["work"][0]["highlights"] = "This is a string, not an array"
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0


def test_keywords_must_be_array(tmp_path):
    """skills[0].keywords as a string instead of array should fail."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["skills"][0]["keywords"] = "Node.js, Python"
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0


# -----------------------------------------------------------------------
# 4. Empty arrays → error reported
# -----------------------------------------------------------------------

def test_empty_highlights_fails(tmp_path):
    """highlights: [] should fail (minItems: 1)."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["work"][0]["highlights"] = []
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0


def test_empty_keywords_fails(tmp_path):
    """skills[0].keywords: [] should fail (minItems: 1)."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["skills"][0]["keywords"] = []
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0


def test_empty_work_fails(tmp_path):
    """work: [] should fail (minItems: 1)."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["work"] = []
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0


# -----------------------------------------------------------------------
# 5. Optional fields absent → should still pass
# -----------------------------------------------------------------------

def test_missing_summary_is_ok(tmp_path):
    """Removing optional basics.summary should still pass validation."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["basics"].pop("summary", None)
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert errors == [], f"Unexpected errors: {errors}"


def test_missing_profiles_is_ok(tmp_path):
    """Removing optional basics.profiles should still pass validation."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["basics"].pop("profiles", None)
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert errors == [], f"Unexpected errors: {errors}"


def test_missing_edu_score_is_ok(tmp_path):
    """Removing optional education[0].score should still pass validation."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["education"][0].pop("score", None)
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert errors == [], f"Unexpected errors: {errors}"


def test_missing_work_location_is_ok(tmp_path):
    """Removing optional work[0].location should still pass validation."""
    data = load_json(DATA_DIR / "backend_resume.json")
    data["work"][0].pop("location", None)
    p = write_tmp_json(tmp_path, data)
    errors = validate_resume(p, SCHEMA_PATH)
    assert errors == [], f"Unexpected errors: {errors}"


# -----------------------------------------------------------------------
# 6. Invalid JSON → error reported
# -----------------------------------------------------------------------

def test_invalid_json_file(tmp_path):
    """A file with broken JSON syntax should return an error."""
    p = tmp_path / "broken.json"
    p.write_text("{ this is not valid json }", encoding="utf-8")
    errors = validate_resume(p, SCHEMA_PATH)
    assert len(errors) > 0
    assert any("Invalid JSON" in e or "JSON" in e for e in errors)


def test_schema_not_found(tmp_path):
    """A missing schema file should return a clear error."""
    data = load_json(DATA_DIR / "backend_resume.json")
    p = write_tmp_json(tmp_path, data)
    fake_schema = tmp_path / "nonexistent.schema.json"
    errors = validate_resume(p, fake_schema)
    assert len(errors) > 0
    assert any("not found" in e.lower() or "schema" in e.lower() for e in errors)
