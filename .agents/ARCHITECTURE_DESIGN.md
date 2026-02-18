# Architecture & Design Patterns

## Design Principles
1.  **Single Responsibility Principle (SRT):** Each class handles exactly one part of the pipeline (Config, Parsing, Rendering, or Compiling).
2.  **Don't Repeat Yourself (DRY):** specialized utility functions for repetitive tasks like character escaping.
3.  **Singleton Pattern:** Used for `Configuration` to ensure environment settings are loaded only once.

## Class Structure

### 1. `Config` (Singleton)
*   **Responsibility:** Loads environment variables and defines constants (paths to data, templates, output).
*   **Behavior:** 
    *   Must verify paths exist upon initialization.
    *   Provides global access to `DATA_DIR`, `OUTPUT_DIR`, etc.

### 2. `DataManager`
*   **Responsibility:** Handles JSON file operations.
*   **Methods:**
    *   `load_json(path: str) -> dict`: Reads the file.
    *   *Future:* Can add schema validation here.

### 3. `LaTeXSanitizer` (Static Utility)
*   **Responsibility:** protecting the LaTeX compiler from crashing.
*   **Methods:**
    *   `escape(text: str) -> str`: Replaces special chars (`&`, `%`, `$`, `#`, `_`, `{`, `}`) with LaTeX escape sequences (e.g., `\&`).
    *   `sanitize_payload(data: dict) -> dict`: Recursively traverses the JSON dictionary and escapes all string values.

### 4. `TemplateEngine`
*   **Responsibility:** Wraps Jinja2 logic.
*   **Configuration:** 
    *   Must configure Jinja2 to use LaTeX-safe delimiters (e.g., `\BLOCK{}`, `\VAR{}`).
*   **Methods:**
    *   `render(template_name: str, context: dict) -> str`: Returns the raw `.tex` string.

### 5. `PDFCompiler`
*   **Responsibility:** Interacts with the OS/Shell.
*   **Methods:**
    *   `compile(tex_content: str, output_filename: str) -> Path`: Writes the `.tex` file to disk and runs `pdflatex`.
    *   **Logic:** Must run `pdflatex` **twice** to resolve references/page numbers.
    *   **Cleanup:** Must remove `.aux`, `.log`, `.out` files after success.

### 6. `ResumeBuilder` (Facade)
*   **Responsibility:** The main entry point that orchestrates the flow.
*   **Logic:**
    1.  `Config` -> Get paths.
    2.  `DataManager` -> Get JSON.
    3.  `LaTeXSanitizer` -> Clean JSON.
    4.  `TemplateEngine` -> Get String.
    5.  `PDFCompiler` -> Generate PDF.