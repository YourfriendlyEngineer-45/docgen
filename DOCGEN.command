#!/bin/bash
# DOCGEN — macOS launcher
# Double-click this file in Finder to run the invoice generator.

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed."
    echo "Download it from https://www.python.org/downloads/"
    read -p "Press Enter to close..."
    exit 1
fi

python3 docgen-gui.py
