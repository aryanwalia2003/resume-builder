# Project Context: Resume Builder System

## Goal
Build a robust, containerized Python application that dynamically generates PDF resumes. The system decouples **Content** (JSON) from **Presentation** (LaTeX).

## Core Workflow
1.  **Input:** A granular JSON file (`data/resume.json`) containing user profile, work history, skills, etc.
2.  **Process:** 
    *   Parse and validate JSON.
    *   Sanitize data (escape LaTeX special characters like `&`, `%`, `$`).
    *   Render a `.tex` string using the Jinja2 templating engine.
    *   Compile the `.tex` file into PDF using `pdflatex` inside a Docker container.
3.  **Output:** A clean `resume.pdf` in the `output/` directory.

## Constraints
*   **Infrastructure:** strictly Docker-based. No local installations.
*   **Language:** Python 3.11+.
*   **Templating:** Jinja2 with custom delimiters (e.g., `\VAR{}`) to avoid LaTeX syntax conflicts.
*   **Architecture:** Modular, following Single Responsibility Principle (SRT).