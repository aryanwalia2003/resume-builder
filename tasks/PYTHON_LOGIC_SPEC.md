### File 3: `PYTHON_LOGIC_SPEC.md`
*This tells the agent exactly how to write the Python code to bridge the JSON and the LaTeX.*

```markdown
# Python Logic Specification

## Directory Structure
Ensure your code is in `src/`.

## Class 1: `Config` (Singleton)
*   **File:** `src/config.py`
*   **Responsibility:** Define `BASE_DIR`, `DATA_DIR` (data/), `TEMPLATE_DIR` (templates/), `OUTPUT_DIR` (output/).
*   **Method:** `get_instance()` to ensure only one config object exists.

## Class 2: `LatexSanitizer` (Static Utility)
*   **File:** `src/utils.py`
*   **Responsibility:** 
    1.  Recursively traverse the loaded JSON dictionary.
    2.  If a value is a string, replace reserved characters:
        *   `&` -> `\&`
        *   `%` -> `\%`
        *   `$` -> `\$`
        *   `#` -> `\#`
        *   `_` -> `\_`
*   **Why:** If you don't do this, "C++ & Python" in the JSON will crash the LaTeX compiler.

## Class 3: `ResumeGenerator`
*   **File:** `src/generator.py`
*   **Dependencies:** `jinja2`, `json`, `os`
*   **Method:** `generate_tex(json_path: str, template_name: str) -> str`
    1.  Load JSON.
    2.  Sanitize JSON.
    3.  Initialize Jinja2 Environment with **LaTeX Delimiters** (See Task Spec).
    4.  Render template.
    5.  Return the string.

## Main Execution
*   **File:** `src/main.py`
*   **Logic:**
    1.  Initialize Config.
    2.  Call `ResumeGenerator.generate_tex()`.
    3.  Write the result to `output/resume_generated.tex`.
    4.  Print "Success: LaTeX file generated at output/resume_generated.tex".