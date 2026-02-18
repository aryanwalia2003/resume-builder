# System & Infrastructure

## Docker Environment
*   **Base:** `python:3.11-slim`
*   **System Dependencies:** 
    *   `texlive-latex-base`
    *   `texlive-fonts-recommended`
    *   `texlive-latex-extra` (Critical for resume formatting)
    *   `texlive-fonts-extra` (Critical for FontAwesome icons)

## Addressing the "FontAwesome Not Found" Log
The logs indicated `fontawesome.sty` was missing. 
1.  **Fix:** Ensure `texlive-fonts-extra` is installed in the Dockerfile.
2.  **Fallback:** If the package manager is slow or missing it, the Python `PDFCompiler` should verify existence via `kpsewhich fontawesome.sty` before compiling. If missing, raise a `EnvironmentError` suggesting a Docker rebuild.

## Volume Mapping
*   **Read-Only:** `/app/src`, `/app/templates`, `/app/data` (Container should not modify source code).
*   **Read-Write:** `/app/output` (Container must write artifacts here).