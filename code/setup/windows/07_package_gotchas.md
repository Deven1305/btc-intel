# setup/windows/07_package_gotchas.md

Checked each flagged package in `requirements.txt` against current
Windows/Anaconda compatibility (June 2026). Most of `requirements.txt`
installs cleanly with a plain `pip install -r requirements.txt` in an
Anaconda Prompt — these three need one extra step beyond that.

## pyzbar

**Extra step needed: install the Visual C++ Redistributable for Visual
Studio 2013 (x64).** The `pyzbar` Windows wheel bundles the actual
`libzbar-64.dll` it needs — you do NOT need to separately install zbar
itself, unlike on Linux (`apt install libzbar0`). But the bundled DLL
itself depends on the 2013 VC++ runtime being present, and on a fresh
Windows install it often isn't, producing a
`FileNotFoundError: Could not find module 'libzbar-64.dll' (or one of its
dependencies)` error that's actually a missing-runtime error in disguise.

[Windows browser]
Download and run **vcredist_x64.exe** from Microsoft:
https://www.microsoft.com/en-us/download/details.aspx?id=40784
(this is the 2013 redistributable specifically — pyzbar's bundled DLL was
built against this version; a newer VC++ redistributable does not
necessarily satisfy this same dependency).

After installing it, `pip install pyzbar` (already in `requirements.txt`)
works with no further steps.

## pytesseract

**Extra step needed: install the Tesseract OCR engine itself — `pip
install pytesseract` only installs the Python wrapper, not the engine.**
This is genuinely two separate things on every OS, but it's easy to miss
on Windows specifically because there's no equivalent of Linux's single
`apt install tesseract-ocr` command bundling both.

[Windows cmd/PowerShell — if you have winget, which ships by default on
Windows 11 and recent Windows 10]
```
winget install -e --id UB-Mannheim.TesseractOCR
```
This installs to `C:\Program Files\Tesseract-OCR\` by default and adds it
to PATH.

If you don't have winget, download the installer directly from the
UB Mannheim project (the de facto standard Windows build, since the
Tesseract project itself doesn't publish official Windows installers):
https://github.com/UB-Mannheim/tesseract/wiki — pick the 64-bit installer
for the current version, run it, accept defaults (English language data
is enough for this project), and manually add
`C:\Program Files\Tesseract-OCR` to your PATH if the installer doesn't
offer to.

Verify:
```
tesseract --version
```

If `pytesseract` still can't find the engine after this (e.g. if you
skipped the PATH step), point to it explicitly in code:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## PGPy (used in services/content/pgp_extract.py)

**Not a Windows-specific issue, but worth flagging since you'll hit it
regardless of OS:** the original `PGPy` 0.6.0 release on PyPI breaks on
Python 3.13+ because it references the `imghdr` standard-library module,
which Python removed in 3.13. `requirements.txt` already uses **`PGPy13`**
instead — a maintained drop-in fork that patches exactly this — so a plain
`pip install -r requirements.txt` avoids the issue. It still imports as
`import pgpy` in code (only the PyPI package name changed, not the
Python import name) — see `services/content/pgp_extract.py`.

## psycopg2-binary

**No extra step needed on Windows/Anaconda.** Unlike on some minimal
Linux base images (where `psycopg2-binary`'s wheel sometimes still needs
`libpq` present at runtime), the Windows wheel bundles everything it
needs. `pip install psycopg2-binary` (already in `requirements.txt`) just
works.

## Everything else in requirements.txt

No other package in the list needs a Windows-specific extra step as of
June 2026 — `pip install -r requirements.txt` in your Anaconda Prompt
handles the rest, including the BigQuery client, scikit-learn, SHAP,
Neo4j driver, and the Gemini/Hugging Face SDKs.
