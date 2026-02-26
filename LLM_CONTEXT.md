# Resume Builder: LLM Context Document

Welcome, fellow LLM. This document provides the architectural context, data flows, and constraints for the Full-Stack ATS-optimized Resume Builder application you are about to help build.

## 🌟 Product Vision
A modular, programmatic resume management system. Users can maintain a single "source of truth" JSON payload for their career history, and selectively generate highly-targeted, beautifully typeset ATS-friendly PDF variants (e.g., Software Engineering, Data Science, Product Management) using LaTeX.

The system prevents manual Word/Google Docs formatting hell by separating data (JSON) from presentation (LaTeX -> PDF).

---

## 🏗️ System Architecture

The project is split into two distinct layers that communicate largely via MongoDB.

### 1. The Core Engine (Python + Docker)
This repository contains the backend compile engine.
- **Role:** Takes a validated JSON schema, merges it into a LaTeX template (`templates/base_resume.tex`) using Jinja2, compiles the `.tex` into a `.pdf` using `pdflatex`, and optionally uploads it to Google Drive.
- **AI Parity:** Contains an AI Pipeline (`src/ai_pipeline.py`) utilizing Google's Gemini 2.5 Flash SDK (`google-genai`). It can ingest any existing PDF resume and expertly extract the contents into our strict JSON schema.
- **Deployment:** Containerized via Docker to guarantee `texlive` dependencies exist. Scripts like `scripts/parse_pdf.py` and `src/main.py` handle execution.

### 2. The Full-Stack Web App (Next.js - *To Be Built*)
This is the application you will be building. It serves as the UI and API layer.
- **Frontend Framework:** Next.js App Router (React), Tailwind CSS.
- **Database:** MongoDB.
- **Functionality:**
  - **Upload:** Users upload a base JSON (or PDF to be routed to the AI parser).
  - **Dashboard:** Displays distinct resume profiles grouped by `meta.code` (e.g., grouped by SWE, PM, DATA roles).
  - **Editor Form:** A complex, modular UI with a sidebar that lets users edit granular sections (`basics`, `work`, `skills`, `education`, `projects`) of the JSON payload independently.
  - **Version Control:** Edits don't just update the document; they save immutable snapshots to a `resume_versions` collection.
  - **Generation Queue:** When a user clicks "Generate PDF", the Next.js API pushes a job to a MongoDB `generations` collection. The Python Docker worker polls (or listens via Change Streams) for these jobs, compiles the PDF, uploads it to Drive, and updates the MongoDB document with the Drive link.
  - **Preview UI:** A polling screen that watches the Mongo generation job status and shows a "Download/Drive" button upon completion.

---

## 🗄️ Database Models (MongoDB)

You will need to implement these collections in the Next.js API layer.

1. **`resumes`**: The active state of a resume payload.
   - `user_id`: Reference to owner.
   - `meta_code`: String (e.g., "SWE").
   - `title`: Display name.
   - `data`: The actual JSON payload matching `resume.schema.json`.
   - `current_version`: Integer.

2. **`resume_versions`**: Immutable history.
   - `resume_id`: Parent reference.
   - `version_number`: Sequence.
   - `data`: The snapshot of the JSON payload.

3. **`generations`**: The Job Queue connecting Next.js to Python.
   - `resume_id`, `version_number`.
   - `status`: "PENDING", "COMPLETED", "FAILED".
   - `drive_link`: URL populated by the Python worker.
   - `error_log`: String, populated if compilation fails.

---

## 📜 The Core JSON Schema constraint
The entire ecosystem adheres strictly to an offline schema parser. Every JSON block edited in the Next.js frontend **MUST** conform to this shape.

```json
{
  "meta": { "code": "SWE" },
  "basics": {
    "name": { "full": "John Doe" },
    "contact": {
      "email": "john@example.com",
      "phone": { "display": "+1 555-0100" }
    },
    "summary": "Optional top-level summary.",
    "profiles": {
      "github": { "network": "GitHub", "url": "https://github.com/..." }
    }
  },
  "work": [
    {
      "company": "Tech Corp",
      "position": "Backend Engineer",
      "location": "Remote",
      "startDate": "Jan 2021",
      "endDate": "Present",
      "highlights": [
        "Scaled architecture servicing 1M DAU.",
        "Supports *Markdown* formatting."
      ]
    }
  ],
  "skills": [
    {
      "category": "Languages",
      "keywords": ["Python", "TypeScript", "Go"]
    }
  ],
  "projects": [
    {
      "name": "Open Source Tool",
      "description": "Built a tool using React."
    }
  ],
  "education": [
    {
       "institution": "University of Tech",
       "degree": "B.S. Computer Science",
       "completionDate": "May 2020",
       "score": { "label": "GPA", "value": "3.8/4.0" }
    }
  ]
}
```

## 🛠️ Your Goal
Your user wants to build the Next.js frontend/backend (separated from the Python engine codebase). Focus on:
1. Creating premium, visually stunning Tailwind CSS layouts with smooth interactions.
2. Building robust Next.js API routes that interact cleanly with the MongoDB schemas outlined above.
3. Building a highly modular Editor UI that breaks that giant JSON schema down into manageable, easy-to-use form inputs.
