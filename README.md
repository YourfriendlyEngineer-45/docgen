# DOCGEN

Reads a CSV of line items and a JSON client config, applies your discount
and VAT rules, produces a PDF invoice.

Free. Runs locally. No subscription. No account. Your data never leaves your machine.

## Install

Termux:
    pkg install python lua54 ruby
    pip install weasyprint

Ubuntu/Debian:
    apt install python3 lua5.4 ruby
    pip install weasyprint

## Use

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
