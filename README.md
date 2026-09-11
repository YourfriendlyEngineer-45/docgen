# DOCGEN

Reads a CSV of line items and a JSON client config, applies your discount
and VAT rules, produces a PDF invoice.

Free. Runs locally. No subscription. No account. Your data never leaves your machine.

## Install

Termux:
    pkg install -y python lua54 ruby python-tkinter
    pip install weasyprint

Ubuntu/Debian:
    sudo apt install -y python3 lua5.4 ruby python3-tk
    pip install weasyprint

Windows / macOS:
    Install Python from python.org (includes tkinter).
    Install Lua: https://www.lua.org/download.html
    Install Ruby: https://www.ruby-lang.org/en/downloads/
    pip install weasyprint

## Use — Graphical

Windows:   double-click DOCGEN.bat
macOS:     double-click DOCGEN.command
           (first time: right-click → Open → Open)
Linux:     double-click DOCGEN.desktop
           (first time: right-click → Allow Launching)

A window opens. Pick a CSV, pick a JSON, click Generate.
The invoice appears in the out/ folder.

## Use — Command line

    ./run.sh path/to/invoices.csv path/to/customer.json out/

Example:

    ./run.sh sample/invoices.csv sample/customer.json out/

Output: out/INV-XXXX.html and out/INV-XXXX.pdf

## Edit the rules

Open `custom.lua`. Everything is commented.
Change a rate, add a rule, run again. No rebuild needed.

## Files

- `run.sh`      — entry point
- `docgen.py`   — reads input, calls Lua and Ruby
- `custom.lua`  — YOUR rules, edit this
- `render.rb`   — HTML template
- `sample/`     — example files to copy from

## License

MIT. Do what you want. No warranty.
