#!/usr/bin/env python3
"""
docgen-gui.py — a window around docgen.py.

Double-click this file (or run `python3 docgen-gui.py`) to open
a window. Pick two files. Click Generate. Get an invoice.

Requires: python3 with tkinter (bundled on Windows/macOS, one install
on Linux: apt install python3-tk / pkg install python-tkinter).
"""
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

HERE = Path(__file__).resolve().parent

root = tk.Tk()
root.title("DOCGEN — Invoice Generator")
root.geometry("560x230")
root.configure(padx=24, pady=20)
root.resizable(False, False)

csv_var = tk.StringVar()
json_var = tk.StringVar()


def pick_csv():
    f = filedialog.askopenfilename(
        title="Choose line items (CSV)",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    )
    if f:
        csv_var.set(f)


def pick_json():
    f = filedialog.askopenfilename(
        title="Choose customer config (JSON)",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )
    if f:
        json_var.set(f)


def generate():
    if not csv_var.get() or not json_var.get():
        messagebox.showwarning(
            "Missing files",
            "Please pick both a CSV and a JSON file.",
        )
        return

    try:
        result = subprocess.run(
            [sys.executable, str(HERE / "docgen.py"),
             csv_var.get(), json_var.get(), "out"],
            capture_output=True, text=True, cwd=str(HERE),
        )
    except Exception as e:
        messagebox.showerror("Failed to run docgen", str(e))
        return

    if result.returncode == 0:
        out_dir = HERE / "out"
        pdfs = sorted(out_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
        if pdfs:
            try:
                if sys.platform.startswith("linux") or "com.termux" in str(HERE):
                    subprocess.Popen(["termux-open", str(pdfs[0])])
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", str(pdfs[0])])
                elif sys.platform == "win32":
                    subprocess.Popen(["start", str(pdfs[0])], shell=True)
            except Exception:
                pass
        messagebox.showinfo("Invoice generated", result.stdout.strip())
    else:
        messagebox.showerror("Failed", result.stderr.strip() or "Unknown error")


# --- layout ---

tk.Label(root, text="Invoice line items (CSV):",
         anchor="w", font=("", 10, "bold")).pack(fill="x")
row1 = tk.Frame(root)
row1.pack(fill="x", pady=(2, 12))
tk.Entry(row1, textvariable=csv_var, font=("", 10)).pack(
    side="left", fill="x", expand=True, ipady=4)
tk.Button(row1, text="Browse", command=pick_csv, width=10).pack(
    side="right", padx=(8, 0))

tk.Label(root, text="Customer config (JSON):",
         anchor="w", font=("", 10, "bold")).pack(fill="x")
row2 = tk.Frame(root)
row2.pack(fill="x", pady=(2, 18))
tk.Entry(row2, textvariable=json_var, font=("", 10)).pack(
    side="left", fill="x", expand=True, ipady=4)
tk.Button(row2, text="Browse", command=pick_json, width=10).pack(
    side="right", padx=(8, 0))

tk.Button(root, text="Generate Invoice",
          bg="#0a66c2", fg="white", font=("", 11, "bold"),
          height=2, command=generate).pack(fill="x")

tk.Label(root, text="Output appears in the 'out' folder.",
         fg="#666", font=("", 8)).pack(pady=(10, 0))

root.mainloop()
