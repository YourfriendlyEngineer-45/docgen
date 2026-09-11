#!/usr/bin/env python3
"""
DOCGEN — reads input, applies business rules via Lua, renders HTML via Ruby.

Three languages, one job each:
  Python: read files, call the others, write the output
  Lua:    compute discounts, VAT, totals
  Ruby:   render HTML from a data hash

Usage: python3 docgen.py [items.csv] [customer.json] [out_dir]
"""
import csv
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


LUA_BINS = ["lua5.4", "lua5.3", "lua54", "lua53", "lua"]


# ============================================================
# Helpers
# ============================================================
def find_lua():
    for b in LUA_BINS:
        p = shutil.which(b)
        if p:
            return p
    return None


def parse_money(s):
    if s is None:
        return 0.0
    s = str(s).strip().replace("£", "").replace("$", "").replace("€", "")
    s = s.replace(",", "")
    if s == "" or s.lower() in ("n/a", "none", "-"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_int(s, default=0):
    try:
        return int(str(s).strip())
    except (ValueError, TypeError):
        return default


def load_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [
            (h or "").strip().lower().replace(" ", "_")
            for h in reader.fieldnames
        ]
        for r in reader:
            if not any((v or "").strip() for v in r.values()):
                continue
            rows.append({k: (v or "").strip() for k, v in r.items()})
    return rows


def load_customer(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_invoice(customer, items):
    line_items = []
    for row in items:
        qty = parse_int(row.get("quantity", "1"), 1) or 1
        unit = parse_money(row.get("unit_price", "0"))
        line_items.append({
            "sku": row.get("sku", ""),
            "description": row.get("description", ""),
            "quantity": qty,
            "unit_price": unit,
            "line_total": round(qty * unit, 2),
        })
    subtotal = round(sum(i["line_total"] for i in line_items), 2)
    return {
        "invoice_number": customer.get("next_invoice_number", "INV-0000"),
        "date": customer.get("invoice_date", date.today().isoformat()),
        "due_days": customer.get("payment_terms_days", 30),
        "customer": {
            "name": customer.get("name", "Unknown"),
            "email": customer.get("email", ""),
            "country": customer.get("country", "GB"),
            "vat_number": customer.get("vat_number", ""),
        },
        "tier": customer.get("tier", "standard"),
        "years_customer": customer.get("years_customer", 0),
        "currency": customer.get("currency", "GBP"),
        "items": line_items,
        "subtotal": subtotal,
    }


# ============================================================
# Lua — business math
# ============================================================
def lua_literal(v):
    if isinstance(v, dict):
        parts = [f"[{lua_literal(str(k))}] = {lua_literal(val)}"
                 for k, val in v.items()]
        return "{ " + ", ".join(parts) + " }"
    if isinstance(v, list):
        return "{ " + ", ".join(lua_literal(x) for x in v) + " }"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if v is None:
        return "nil"
    s = str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'


def call_lua(lua_bin, invoice, custom_path):
    script = f"""
local data = {lua_literal(invoice)}
dofile("{custom_path}")
local result = compute(data)
for k, v in pairs(result) do
  if type(v) == "number" then
    print(k .. "=" .. string.format("%.6f", v))
  elseif type(v) == "string" or type(v) == "boolean" then
    print(k .. "=" .. tostring(v))
  end
end
""".strip()

    proc = subprocess.run(
        [lua_bin, "-"],
        input=script,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"lua failed:\n{proc.stderr.strip()}")

    result = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        try:
            result[k] = float(v)
        except ValueError:
            if v == "true":
                result[k] = True
            elif v == "false":
                result[k] = False
            else:
                result[k] = v
    return result


# ============================================================
# Ruby — HTML rendering
# ============================================================
def call_ruby(invoice):
    proc = subprocess.run(
        ["ruby", "render.rb"],
        input=json.dumps(invoice),
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ruby failed:\n{proc.stderr.strip()}")
    return proc.stdout


# ============================================================
# Main
# ============================================================
def main():
    items_path = sys.argv[1] if len(sys.argv) > 1 else "sample/invoices.csv"
    cust_path = sys.argv[2] if len(sys.argv) > 2 else "sample/customer.json"
    out_dir = Path(sys.argv[3] if len(sys.argv) > 3 else "out")

    lua_bin = find_lua()
    if not lua_bin:
        print("error: lua not found (pkg install lua54)", file=sys.stderr)
        sys.exit(1)

    custom_path = Path("custom.lua").resolve()
    if not custom_path.exists():
        print(f"error: {custom_path} not found", file=sys.stderr)
        sys.exit(1)

    render_path = Path("render.rb").resolve()
    if not render_path.exists():
        print(f"error: {render_path} not found", file=sys.stderr)
        sys.exit(1)

    # 1. Python reads
    items = load_csv(items_path)
    customer = load_customer(cust_path)
    invoice = build_invoice(customer, items)

    # 2. Lua computes
    try:
        invoice["lua"] = call_lua(lua_bin, invoice, str(custom_path))
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Ruby renders
    try:
        html = call_ruby(invoice)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Python writes
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"{invoice['invoice_number']}.html"
    html_path.write_text(html, encoding="utf-8")

  # optional: also write a PDF next to the HTML
    try:
        from weasyprint import HTML as WeasyHTML
        pdf_path = out_dir / f"{invoice['invoice_number']}.pdf"
        WeasyHTML(filename=str(html_path)).write_pdf(str(pdf_path))
        print(f"docgen: wrote {html_path} and {pdf_path}")
    except ImportError:
        print(f"docgen: wrote {html_path}  (install weasyprint for PDF)")

if __name__ == "__main__":
    main()
