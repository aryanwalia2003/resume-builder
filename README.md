# 📄 Resume Builder — Automated PDF Generator

A Dockerized pipeline that takes a **JSON resume file** and produces a polished **PDF resume** using a **LaTeX template**. No LaTeX installation needed on your machine — everything runs inside Docker.

---

## 🗂️ Project Structure

```
resume-editor/
│
├── data/                        # ← JSON files (resume content)
│   ├── backend_resume.json      # Backend/SDE role resume
│   ├── fs_resume.json           # Full-stack role resume
│   ├── applied_ai_resume.json   # Applied AI role resume
│   └── data_engineer_resume.json
│
├── templates/
│   └── base_resume.tex          # ← THE LaTeX template (Jinja2-powered)
│
├── template_resume/
│   └── template.pdf             # ← The original PDF your resume was modelled after
│
├── output/                      # ← Generated PDFs land here (git-ignored)
│
├── src/
│   ├── main.py                  # Entrypoint — orchestrates everything
│   ├── config.py                # Path configuration (BASE_DIR, DATA_DIR, etc.)
│   ├── generator.py             # Loads JSON + renders LaTeX template via Jinja2
│   ├── compiler.py              # Runs pdflatex inside container → produces PDF
│   └── utils.py                 # LaTeX sanitizer (escapes special chars in JSON)
│
├── scripts/
│   └── health_check.sh          # Runs on container startup to verify environment
│
├── Dockerfile                   # Python 3.11 + texlive (pdflatex) image
└── docker-compose.yml           # Mounts volumes and orchestrates the container
```

---

## 🧠 What Exactly Happens (Step by Step)

```
You run a command
      ↓
docker-compose runs the container (resume_backend)
      ↓
main.py starts inside the container
      ↓
  1. Reads the specified --input JSON file from data/
  2. Extracts meta.code (e.g. "BE") + current date → builds output filename
     e.g. → Aryan_BE_2602.pdf
  3. generator.py loads the JSON and renders templates/base_resume.tex
     using Jinja2 (custom LaTeX-safe delimiters like \VAR{} and \BLOCK{})
  4. utils.py sanitizes all values (escapes &, %, #, etc. for LaTeX)
  5. The rendered .tex file is saved to output/
  6. compiler.py runs pdflatex twice on the .tex file
     (two passes to correctly resolve layout/references)
  7. Auxiliary files (.aux, .log, .out) are auto-deleted
  8. Final PDF appears in output/
```

---

## 📐 The Template

| Item | Location |
|---|---|
| **Original PDF sample** (the design you start from) | `template_resume/template.pdf` |
| **LaTeX template** (the Jinja2 file that generates resumes) | `templates/base_resume.tex` |

`base_resume.tex` uses **custom Jinja2 delimiters** to stay valid LaTeX:

| Jinja2 syntax | Purpose |
|---|---|
| `\VAR{basics.name.full}` | Insert a variable |
| `\BLOCK{ for job in work }` | Loop block |
| `\BLOCK{ endfor }` | End block |

The template renders: Header → Work Experience → Skills → Personal Projects → Education.

---

## 🔌 Which JSON Drives the PDF?

The JSON files in `data/` contain **all the resume content**. Each file targets a different job role:

| File | Role | Output PDF name |
|---|---|---|
| `backend_resume.json` | Backend / SDE | `Aryan_BE_YYMM.pdf` |
| `fs_resume.json` | Full Stack | `Aryan_FS_YYMM.pdf` |
| `applied_ai_resume.json` | Applied AI / ML | `Aryan_AAI_YYMM.pdf` |
| `data_engineer_resume.json` | Data Engineering | *(see meta.code inside)* |

The output filename is determined by `meta.code` inside each JSON:
```json
{
  "meta": {
    "code": "BE"
  },
  ...
}
```

---

## 🚀 How to Run

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Step 1 — Build the Docker image (first time only)
```bash
docker-compose build
```
This installs Python 3.11 + the full LaTeX suite (`texlive`) inside the container. Takes a few minutes the first time; subsequent builds are cached.

### Step 2 — Generate a PDF

**Generate with the default file (`fs_resume.json`):**
```bash
docker-compose run --rm builder python -m src.main
```

**Generate for a specific role:**
```bash
# Backend resume
docker-compose run --rm builder python -m src.main --input backend_resume.json

# Applied AI resume
docker-compose run --rm builder python -m src.main --input applied_ai_resume.json

# Data Engineer resume
docker-compose run --rm builder python -m src.main --input data_engineer_resume.json
```

The generated PDF will appear in your local `output/` folder (volumes are mounted, so it syncs instantly).

---

## ➕ Creating a New Resume Variant

### 1. Copy an existing JSON as your starting point
```bash
# Example: create a "product engineer" variant
cp data/backend_resume.json data/product_resume.json
```

### 2. Set the `meta.code` for the new role
Open `data/product_resume.json` and change:
```json
{
  "meta": {
    "code": "PE"
  }
}
```
This controls the output filename → `Aryan_PE_YYMM.pdf`

### 3. Edit the content fields in the JSON
Update `basics.summary`, the `work` array, `skills`, `projects`, and `education` as needed.

### 4. Generate the PDF
```bash
docker-compose run --rm builder python -m src.main --input product_resume.json
```

Your new PDF will appear in `output/Aryan_PE_YYMM.pdf`.

---

## 📝 JSON Structure Reference

```jsonc
{
  "meta": { "code": "BE" },            // Controls output filename
  "basics": {
    "name": { "full": "Aryan Walia" },
    "contact": { "phone": {...}, "email": "..." },
    "profiles": {                       // Social links (rendered in header)
      "linkedin": { "network": "LinkedIn", "url": "..." }
    },
    "summary": "One-liner shown below name"
  },
  "work": [                             // Array of jobs
    {
      "company": "...", "location": "...",
      "position": "...", "startDate": "...", "endDate": "...",
      "highlights": ["bullet 1", "bullet 2"]  // Supports **bold** and [links](url)
    }
  ],
  "skills": [
    { "category": "Backend", "keywords": ["Node.js", "Django"] }
  ],
  "projects": [
    { "name": "Project Name", "description": "What it is" }
  ],
  "education": [
    {
      "institution": "...", "degree": "...", "completionDate": "...",
      "score": { "label": "CGPA", "value": "8.5" }
    }
  ]
}
```

> **Tip:** `highlights` and `description` support `**bold**` and `[link text](url)` — these are auto-converted to LaTeX by `utils.py`.

---

## ⚙️ Tech Stack

| Component | Technology |
|---|---|
| Container | Docker + Python 3.11 slim |
| PDF compiler | `pdflatex` (texlive-latex-extra) |
| Template engine | Jinja2 (with custom LaTeX-safe delimiters) |
| Resume data | JSON |
