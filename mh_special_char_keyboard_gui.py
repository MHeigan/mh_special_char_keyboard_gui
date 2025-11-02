#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mh_special_char_keyboard_gui.py

A Tkinter GUI that presents a "keyboard" of special characters and symbols.
Click any symbol to copy it to the clipboard. Shift‑Click (or Right‑Click → Append)
will append the symbol to the builder text area for later saving to a .txt file.

Design choices follow the user's usual preferences:
- Centered window
- Default Tk theme with light grey buttons
- Contents inside a sticky labelled frame titled "mh_tools"
- Clean, compact layout (Butterworth‑style inspiration), no external deps

Tested with Python 3.8+.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import unicodedata
import sys
import platform

APP_TITLE = "Special Character Keyboard"
FRAME_LABEL = "mh_tools"

# ---------------------------- Helper: window centering ---------------------------- #

def center_window(win: tk.Tk, width: int, height: int) -> None:
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

# ---------------------------- Tooltip helper ---------------------------- #

class Tooltip:
    def __init__(self, widget, text_fn, delay=350):
        self.widget = widget
        self.text_fn = text_fn  # function returning dynamic text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        self.widget.bind("<Enter>", self._enter)
        self.widget.bind("<Leave>", self._leave)
        self.widget.bind("<Motion>", self._motion)

    def _enter(self, _):
        self._schedule()

    def _leave(self, _):
        self._unschedule()
        self._hide()

    def _motion(self, _):
        # restart timer to avoid stale display while moving
        self._unschedule()
        self._schedule()

    def _schedule(self):
        self._unschedule()
        self.id = self.widget.after(self.delay, self._show)

    def _unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def _show(self):
        if self.tipwindow or not self.widget.winfo_viewable():
            return
        text = self.text_fn() if callable(self.text_fn) else str(self.text_fn)
        if not text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=text, justify=tk.LEFT, relief=tk.SOLID, bd=1,
                         bg="#ffffe0", fg="#000000", padx=6, pady=4, font=("TkDefaultFont", 9))
        label.pack(ipadx=1)

    def _hide(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# ---------------------------- Symbol data ---------------------------- #

# Core categories with curated symbols. This keeps startup fast and practical.
CATEGORIES = {
    "Punctuation": list("…•—––—―！？¿¡¶§†‡#@&©®™°·•‧¦|‖※") + ["‚","„","‘","’","‚","‛","“","”","„","‟","‹","›","«","»"],
    "Quotes": ["'", '"', "‘", "’", "‚", "‛", "“", "”", "„", "‟", "‹", "›", "«", "»", "′", "″"],
    "Currency": ["$","€","£","¥","₹","₽","₩","₺","₴","₦","₨","₫","฿","₿","¢"],
    "Math": ["±","×","÷","≈","≠","≤","≥","∞","√","∛","∜","∑","∏","∫","∂","∇","∩","∪","∈","∉","∅","∧","∨","¬","⇒","⇔","≈","≅","≡","∝","∴","∵","‰","‱"],
    "Arrows": ["←","↑","→","↓","↔","↕","⇐","⇑","⇒","⇓","⇔","↩","↪","↖","↗","↘","↙","⟵","⟶","⟷","⟸","⟹","⟺"],
    "Bullets & Stars": ["•","◦","▪","▫","●","○","★","☆","✦","✧","✩","✪","✫","✬","✭","✮","✯","✰","◆","◇","■","□","◻","◼","◉","◎"],
    "Brackets": ["(", ")", "[", "]", "{", "}", "〈", "〉", "⟨", "⟩", "❪", "❫", "❬", "❭", "❮", "❯"],
    "Letters (Latin Diacritics)": list("àáâãäåæçèéêëìíîïñòóôõöøùúûüýÿÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝÞþßŒœŠšŽž") + ["Ł","ł","Đ","đ","Ħ","ħ","Ŋ","ŋ","Ŧ","ŧ"],
    "Greek": list("αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ") + ["π","Π","µ","Μ","Ω"],
    "Technical": ["°","µ","Ω","‰","℃","℉","§","¶","№","℗","℠","™","©","®","♠","♣","♥","♦","♭","♮","♯","✓","✔","✗","✘","⚠","⌘","⌥","⌃","⎋"],
    "Box Drawing": ["─","━","│","┃","┌","┏","┐","┓","└","┗","┘","┛","├","┝","┤","┥","┬","┯","┴","┷","┼","┿","╭","╮","╯","╰","╴","╵","╶","╷","╲","╱","╳"],
}

# ---------------------------- Utilities for symbol info ---------------------------- #

def symbol_info(ch: str) -> dict:
    cp = ord(ch)
    hex_cp = f"U+{cp:04X}"
    dec_cp = str(cp)
    try:
        name = unicodedata.name(ch)
    except ValueError:
        name = "<no name>"
    html_dec = f"&#{cp};"
    html_hex = f"&#x{cp:X};"
    # Windows Alt code works for extended ASCII range using codepage (approx 32..255)
    alt_hint = f"Alt+{cp}" if 32 <= cp <= 255 and platform.system() == "Windows" else "—"
    return {
        "char": ch,
        "name": name,
        "hex": hex_cp,
        "dec": dec_cp,
        "html_dec": html_dec,
        "html_hex": html_hex,
        "alt": alt_hint,
    }

# ---------------------------- Main Application ---------------------------- #

class SpecialCharKeyboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg="#ececec")  # default light grey background
        center_window(self, 1280, 820)

        self._builder_var = tk.StringVar(value="")
        self._last_symbol = None

        outer = ttk.LabelFrame(self, text=FRAME_LABEL)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_bar = tk.Frame(outer, bg="#ececec")
        top_bar.pack(fill=tk.X, pady=(6, 4))

        tk.Label(top_bar, text="Search:", bg="#ececec").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(top_bar, textvariable=self.search_var, width=32)
        search_entry.pack(side=tk.LEFT, padx=6)
        tk.Button(top_bar, text="Find", bg="#d9d9d9", command=self._do_search).pack(side=tk.LEFT)
        tk.Button(top_bar, text="Clear", bg="#d9d9d9", command=self._clear_search).pack(side=tk.LEFT, padx=(6,0))

        # Main split: left = tabs; right = details + builder
        main = tk.PanedWindow(outer, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(main)
        right = tk.Frame(main)
        main.add(left, stretch="always")
        main.add(right, minsize=360)

        # Tabs with categories
        self.tabs = ttk.Notebook(left)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.category_frames = {}
        for cat, items in CATEGORIES.items():
            frame = self._make_scrollable_category(self.tabs, cat, items)
            self.tabs.add(frame, text=cat)
            self.category_frames[cat] = frame

        # Search tab (lazy created)
        self.search_tab = None

        # Right side: info + builder
        info_frame = ttk.LabelFrame(right, text="Symbol Info")
        info_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.char_big = tk.Label(info_frame, text="", font=("Segoe UI", 40))
        self.char_big.grid(row=0, column=0, rowspan=2, sticky="w", padx=(8,8), pady=6)

        grid = tk.Frame(info_frame)
        grid.grid(row=0, column=1, sticky="nw", padx=(0,8), pady=6)

        self.name_var = tk.StringVar()
        self.hex_var = tk.StringVar()
        self.dec_var = tk.StringVar()
        self.html_dec_var = tk.StringVar()
        self.html_hex_var = tk.StringVar()
        self.alt_var = tk.StringVar()

        def add_row(r, label, var):
            tk.Label(grid, text=label+":").grid(row=r, column=0, sticky="e", padx=4, pady=1)
            tk.Entry(grid, textvariable=var, width=36).grid(row=r, column=1, sticky="w", padx=4, pady=1)

        add_row(0, "Name", self.name_var)
        add_row(1, "Unicode", self.hex_var)
        add_row(2, "Code (dec)", self.dec_var)
        add_row(3, "HTML &#;", self.html_dec_var)
        add_row(4, "HTML &#x;", self.html_hex_var)
        add_row(5, "Keyboard (Win Alt)", self.alt_var)

        btn_row = tk.Frame(info_frame)
        btn_row.grid(row=1, column=1, sticky="w", padx=4, pady=(0,6))
        tk.Button(btn_row, text="Copy Symbol", bg="#d9d9d9", command=self._copy_current).pack(side=tk.LEFT)
        tk.Button(btn_row, text="Append to Builder", bg="#d9d9d9", command=self._append_current).pack(side=tk.LEFT, padx=6)

        builder = ttk.LabelFrame(right, text="Builder (use Shift‑Click on symbols to append)")
        builder.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        self.builder_text = tk.Text(builder, height=10, wrap=tk.WORD)
        self.builder_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        bbar = tk.Frame(builder)
        bbar.pack(fill=tk.X, padx=8, pady=(0,8))
        tk.Button(bbar, text="Copy All", bg="#d9d9d9", command=self._copy_all).pack(side=tk.LEFT)
        tk.Button(bbar, text="Clear", bg="#d9d9d9", command=self._clear_builder).pack(side=tk.LEFT, padx=6)
        tk.Button(bbar, text="Save to .txt", bg="#d9d9d9", command=self._save_to_txt).pack(side=tk.LEFT, padx=(6,0))

        # Status bar
        self.status = tk.StringVar(value="Ready. Click a symbol to copy. Shift‑Click to append.")
        sbar = tk.Label(self, textvariable=self.status, anchor="w", bg="#e0e0e0")
        sbar.pack(fill=tk.X, side=tk.BOTTOM)

    # ---------------------------- Category grid builder ---------------------------- #

    def _make_scrollable_category(self, parent, cat_name, items):
        container = tk.Frame(parent)
        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        inner = tk.Frame(canvas)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", on_config)

        # Build grid of symbol buttons
        COLS = 14
        for idx, ch in enumerate(items):
            btn = tk.Button(inner, text=ch, width=4, height=1, bg="#d9d9d9", font=("Segoe UI", 18),
                            command=lambda c=ch: self._on_symbol_click(c))
            r, c = divmod(idx, COLS)
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            btn.bind("<Shift-Button-1>", lambda e, c=ch: self._append_symbol(c))
            btn.bind("<Button-3>", lambda e, c=ch: self._context_menu(e, c))
            Tooltip(btn, lambda c=ch: self._tooltip_text(c))

        # make columns expand evenly
        for c in range(COLS):
            inner.grid_columnconfigure(c, weight=1)
        return container

    # ---------------------------- Actions ---------------------------- #

    def _on_symbol_click(self, ch: str):
        self.clipboard_clear()
        self.clipboard_append(ch)
        self._last_symbol = ch
        self._update_info(ch)
        self.status.set(f"Copied: '{ch}' to clipboard.")

    def _append_symbol(self, ch: str):
        self.builder_text.insert(tk.END, ch)
        self._last_symbol = ch
        self._update_info(ch)
        self.status.set(f"Appended: '{ch}' to builder.")

    def _context_menu(self, event, ch: str):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copy", command=lambda: self._on_symbol_click(ch))
        menu.add_command(label="Append to Builder", command=lambda: self._append_symbol(ch))
        menu.tk_popup(event.x_root, event.y_root)

    def _tooltip_text(self, ch: str) -> str:
        info = symbol_info(ch)
        return f"{ch}  \n{info['name']}\n{info['hex']} (dec {info['dec']})\nHTML: {info['html_dec']}  {info['html_hex']}\nKeyboard: {info['alt']}"

    def _update_info(self, ch: str):
        info = symbol_info(ch)
        self.char_big.config(text=ch)
        self.name_var.set(info["name"])
        self.hex_var.set(info["hex"])
        self.dec_var.set(info["dec"])
        self.html_dec_var.set(info["html_dec"])
        self.html_hex_var.set(info["html_hex"])
        self.alt_var.set(info["alt"])

    def _copy_current(self):
        if not self._last_symbol:
            messagebox.showinfo("Nothing Selected", "Click a symbol first.")
            return
        self._on_symbol_click(self._last_symbol)

    def _append_current(self):
        if not self._last_symbol:
            messagebox.showinfo("Nothing Selected", "Click a symbol first.")
            return
        self._append_symbol(self._last_symbol)

    def _copy_all(self):
        text = self.builder_text.get("1.0", tk.END).rstrip("\n")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status.set("Builder contents copied to clipboard.")

    def _clear_builder(self):
        self.builder_text.delete("1.0", tk.END)
        self.status.set("Builder cleared.")

    def _save_to_txt(self):
        text = self.builder_text.get("1.0", tk.END)
        if not text.strip():
            if not messagebox.askyesno("Empty Text", "Builder is empty. Save an empty file?"):
                return
        path = filedialog.asksaveasfilename(title="Save as .txt", defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.status.set(f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file:\n{e}")

    # ---------------------------- Search ---------------------------- #

    def _do_search(self):
        q = self.search_var.get().strip().lower()
        if not q:
            self._clear_search()
            return
        results = []
        for cat, items in CATEGORIES.items():
            for ch in items:
                name = ""
                try:
                    name = unicodedata.name(ch).lower()
                except ValueError:
                    pass
                if q in ch.lower() or (name and q in name):
                    results.append((ch, cat))
        self._show_search_results(results, q)

    def _clear_search(self):
        self.search_var.set("")
        if self.search_tab is not None:
            idx = self.tabs.index(self.search_tab)
            self.tabs.forget(idx)
            self.search_tab = None
        self.status.set("Search cleared.")

    def _show_search_results(self, results, query):
        if self.search_tab is not None:
            idx = self.tabs.index(self.search_tab)
            self.tabs.forget(idx)
            self.search_tab = None
        frame = self._make_scrollable_category(self.tabs, "Search Results", [ch for ch, _ in results])
        count = len(results)
        label = f"Search: '{query}' ({count} result{'s' if count != 1 else ''})"
        self.search_tab = frame
        self.tabs.add(frame, text=label)
        self.tabs.select(frame)
        self.status.set(label)

# ---------------------------- main ---------------------------- #

def main():
    app = SpecialCharKeyboard()
    app.mainloop()

if __name__ == "__main__":
    main()
