#!/bin/bash

echo "========================================"
echo "   RESUME BUILDER: HEALTH CHECK LOGS    "
echo "========================================"

# 1. CHECK PYTHON
echo -e "\n[1] Checking Python Environment..."
python3 --version
if [ $? -eq 0 ]; then echo "✅ Python is accessible"; else echo "❌ Python Failed"; fi

# 2. CHECK JINJA2
echo -e "\n[2] Checking Python Dependencies..."
pip show jinja2 | grep Version
if [ $? -eq 0 ]; then echo "✅ Jinja2 is installed"; else echo "❌ Jinja2 MISSING"; fi

# 3. CHECK LATEX COMPILER
echo -e "\n[3] Checking LaTeX Compiler (pdflatex)..."
pdflatex --version | head -n 1
if [ $? -eq 0 ]; then echo "✅ pdflatex is accessible"; else echo "❌ pdflatex FAILED"; fi

# 4. CHECK COMMON RESUME PACKAGES
echo -e "\n[4] Checking Critical LaTeX Packages..."
# kpsewhich is a tool to find latex files
PACKAGES=("geometry.sty" "hyperref.sty" "enumitem.sty" "fontawesome5.sty")

for pkg in "${PACKAGES[@]}"; do
    path=$(kpsewhich $pkg)
    if [ ! -z "$path" ]; then
        echo "✅ Found $pkg at $path"
    else
        echo "⚠️  WARNING: $pkg NOT FOUND (Resume templates using this might fail)"
    fi
done

# 5. CHECK VOLUME MOUNTS
echo -e "\n[5] Checking File System Permissions..."
# We try to touch a file in the output directory to see if we have write access
touch /app/output/test_write_permission.txt 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Write permission to /app/output successful"
    rm /app/output/test_write_permission.txt
else
    echo "❌ CANNOT WRITE to /app/output (Check Docker Volume Permissions)"
fi

echo -e "\n========================================"
echo "   HEALTH CHECK COMPLETE                "
echo "========================================"