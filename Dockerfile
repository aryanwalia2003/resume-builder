# Base Image: Official Python Slim (Debian-based)
FROM python:3.11-slim

# Metdata
LABEL maintainer="your_email@example.com"
LABEL description="Resume Builder Environment: Python + LaTeX"

# 1. Install System Dependencies (The heavy stuff)
# - texlive-latex-base: The compiler (pdflatex)
# - texlive-fonts-recommended: Standard fonts
# - texlive-latex-extra: Crucial for resume templates (geometry, hyperref, etc)
# - build-essential: Sometimes needed for python extensions (optional but safe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-fonts-extra \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Set up Python Environment
WORKDIR /app

# Install dependencies (This layer is cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Default Command
# We set this to a shell so the container stays alive for us to inspect, 
# or we can override it in docker-compose.
CMD ["/bin/bash"]