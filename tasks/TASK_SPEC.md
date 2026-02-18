# Task Specification: Resume Generator (Phase 1)

## Objective
Develop a Python module that reads a JSON data file and a LaTeX template, renders the content using Jinja2, and outputs a raw `.tex` file. 

**Note:** We are NOT compiling to PDF yet. We are only generating the source LaTeX code.

## Inputs
1.  **Data Source:** `data/fs_resume.json` (The structured data).
2.  **Template:** `templates/base_resume.tex` (The Jinja2-ready LaTeX file).

## Outputs
1.  **Generated File:** `output/generated_resume.tex`

## Constraints & Requirements
1.  **Strict Separation:** The Python script must NOT contain hardcoded LaTeX strings. All layout must reside in the `.tex` template file.
2.  **Jinja2 Configuration:** You must configure Jinja2 to use **LaTeX-safe delimiters** to avoid conflicts with LaTeX's native `{}` syntax.
    *   Variable: `\VAR{ variable_name }`
    *   Block: `\BLOCK{ % if ... % }`
    *   Comment: `\#{ comment }`
3.  **Sanitization:** All strings coming from JSON must be passed through a sanitizer function to escape special LaTeX characters (`&`, `$`, `%`, `_`, etc.) before rendering.
4.  **Modularity:** Follow the `Architecture Design` (SRT, DRY). Use a `Config` singleton.