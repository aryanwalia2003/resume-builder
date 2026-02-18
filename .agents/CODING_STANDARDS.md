# Coding Standards

## General
*   **Type Hinting:** All function signatures must use Python type hints (`def func(a: str) -> int:`).
*   **Docstrings:** Google-style docstrings for classes and complex methods only. No obvious comments (e.g., avoid `# This prints hello`).
*   **Error Handling:** Use custom exceptions (e.g., `TemplateNotFoundError`, `CompilationError`) rather than generic `Exception`.

## Docker & Paths
*   **Relative Paths:** Never use hardcoded absolute paths. Use `pathlib.Path` relative to the project root.
*   **Logging:** Use the standard `logging` module. Do not use `print()` statements in production code.

## LaTeX Specifics
*   **Delimiter Safety:** Jinja2 MUST be configured with:
    *   Variable: `\VAR{...}`
    *   Block: `\BLOCK{...}`
    *   Comment: `\#{...}`