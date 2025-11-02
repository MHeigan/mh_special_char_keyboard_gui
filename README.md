# mh_special_char_keyboard

A lightweight Tkinter app that gives you a visual **keyboard of special characters & symbols**.  
Click any symbol to **copy to clipboard**, **Shift‑click to append** it to a builder panel, and **save the result to .txt**.

> Built to match the `mh_tools` style: centered window, default Tk theme, light grey buttons, all content inside a labeled frame **“mh_tools”**.

---

## Features

- **One‑click copy:** Click a symbol and it goes straight to the clipboard.
- **Append builder:** Shift‑click (or right‑click → *Append*) to add symbols to a text builder.
- **Save to file:** Export builder contents to `.txt`.
- **Symbol details:** Live panel shows name, Unicode code point, decimal code, HTML entities, and Windows Alt‑code hint (when applicable).
- **Search:** Find by character or Unicode name; results open in a temporary tab.
- **Categories:** Punctuation, Quotes, Currency, Math, Arrows, Bullets & Stars, Brackets, Latin Diacritics, Greek, Technical, Box Drawing.
- **Bigger UI:** Large symbol buttons (Segoe UI 18) and large preview glyph (Segoe UI 40).

---

## Requirements

- **Python 3.8+** (recommended 3.12).  
- **No external packages** required. Tkinter is included with most Python installers (on Windows & macOS). On some Linux distros you may need to install `python3-tk` via your package manager.

This repository includes a `requirements.txt` that’s intentionally empty (no third‑party deps).

---

## Quick Start

```bash
# 1) (Optional) create a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install (no deps, but this keeps workflow consistent)
pip install -r requirements.txt

# 3) Run
python mh_special_char_keyboard_gui.py
```

> If `tkinter` is missing on Linux, install it via your package manager, e.g.:
>
> Ubuntu/Debian:
> ```bash
> sudo apt-get update && sudo apt-get install -y python3-tk
> ```

---

## Files

- `mh_special_char_keyboard_gui.py` — The app.
- `requirements.txt` — Empty on purpose (no external libs).
- `create_venv.bat` — Windows helper to create & activate a venv.
- `create_venv.sh` — macOS/Linux helper to create & activate a venv.
- `.python-version` — Optional pin for local tools (set to `3.12` as a hint).
- `.gitignore` — Standard Python ignore list.

---

## Packaging (Optional)

If you want a single-file executable (Windows), install PyInstaller in your venv and build:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed ^
  --name mh_special_char_keyboard ^
  mh_special_char_keyboard_gui.py
```

The binary will appear in `dist/`.

---

## Keyboard equivalence notes

- The info panel shows a **Windows Alt‑code hint** when it’s applicable for extended ASCII (roughly U+0020..U+00FF).
- For full Unicode entry, prefer copy‑paste from this app, or OS‑level emoji & symbol pickers.

---

## License

MIT (or add your preferred license here).

---

## Credits

Designed with the **mh_tools** GUI conventions in mind.


## Manual

See `mh_special_char_keyboard_manual.rtf`.
