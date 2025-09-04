Step2STL — Drop-Folder STEP→STL Converter (FreeCAD)

What It Does (Simple)
- Converts `.step/.stp` to `.stl` with good defaults.
- Double‑click to run. Drop STEP files into `STEP-INPUT/`. Results land in `STL-OUTPUT/`.
- Moves processed STEP files into `STEP-INPUT/_processed/` so re‑runs skip them.
- Works on macOS and Windows. Linux supported via command line.

Built‑in Defaults (Ready to Go)
- Quality: high (good surface fidelity)
- Orientation: assumes STEP is Y‑up and converts to Z‑up STL
- Folders already included: `STEP-INPUT/` and `STL-OUTPUT/`

What’s in the bundle
- `step2stl.py`: Core converter. Two modes:
  - Drop‑folder (default when run without args):
    - Reads from `STEP-INPUT/` next to the script
    - Outputs to `STL-OUTPUT/`
    - Moves processed files into `STEP-INPUT/_processed/`
  - CLI mode (when given an input path):
    - `FreeCADCmd -c "...runpy... step2stl.py <input>"`
    - Accepts a file or directory and optional flags (`-q`, `-o`, etc.)
- `Step2Stl.command` (macOS): Double‑click to run drop‑folder mode.
- `Step2Stl.bat` (Windows): Double‑click to run drop‑folder mode.

Install FreeCAD
- macOS (easiest)
  - Install: `brew install --cask freecad`
  - One‑time approval if needed: open the app once from Applications, then quit.
  - Optional (Terminal use): `export PATH="/Applications/FreeCAD.app/Contents/Resources/bin:$PATH"`
  - Verify: `FreeCADCmd --version` (or `freecadcmd --version`)

- Windows 10/11
  - Download/Install: https://www.freecad.org (includes `FreeCADCmd.exe`).
  - Verify: open Command Prompt and run:
    - `"C:\\Program Files\\FreeCAD 1.0\\bin\\FreeCADCmd.exe" --version` (or `0.21` path)
  - If not in PATH, the provided `Step2Stl.bat` will try common install paths.

- Linux (Debian/Ubuntu)
  - Install: `sudo apt-get update && sudo apt-get install -y freecad`
  - Verify: `freecadcmd --version`

Quick Start (Double‑Click)
- macOS: double‑click `Step2Stl.command` in Finder
  1) If asked, allow running (Right‑click → Open the first time)
  2) Drop `.step/.stp` files into `STEP-INPUT/`
  3) Double‑click `Step2Stl.command` again to convert
  4) Find `.stl` in `STL-OUTPUT/` and your original STEP in `STEP-INPUT/_processed/`

- Windows: double‑click `Step2Stl.bat` in File Explorer
  1) If a console flashes and closes, open Command Prompt and run `Step2Stl.bat` to see messages
  2) Drop `.step/.stp` files into `STEP-INPUT/`
  3) Double‑click `Step2Stl.bat` again to convert
  4) Find `.stl` in `STL-OUTPUT/` and your original STEP in `STEP-INPUT/_processed/`

Command Line (Optional)
- Single file:
  - macOS/Linux: `FreeCADCmd -c "import sys,runpy; sys.argv=['$(pwd)/step2stl.py','$(pwd)/path/to/file.step']; runpy.run_path('$(pwd)/step2stl.py', run_name='__main__')"`
  - Windows (PowerShell): `& 'C:\\Program Files\\FreeCAD 1.0\\bin\\FreeCADCmd.exe' -c "import sys,runpy; p='C:/path/to/step2stl.py'; f='C:/path/to/file.step'; sys.argv=[p,f]; runpy.run_path(p, run_name='__main__')"`
- Whole folder:
  - `FreeCADCmd -c "import sys,runpy; sys.argv=['$(pwd)/step2stl.py','$(pwd)/path/to/folder']; runpy.run_path('$(pwd)/step2stl.py', run_name='__main__')"`

Options
- `-q/--quality`: `high` (default), `medium`, `low`, or `custom`
- `--linear-deflection`, `--angular-deflection`, `--relative`: for `--quality custom`
- `-o/--out`: custom output directory (CLI mode). In drop‑folder mode, outputs to `STL-OUTPUT/` by default.
- Orientation/rotation:
  - `--source-up {x|y|z}` and `--target-up {x|y|z}` (defaults set in config: `y` → `z`)
  - `--rotate-x DEG`, `--rotate-y DEG`, `--rotate-z DEG` (applied after up‑mapping)

Defaults for double‑click mode
- A `step2stl.config.json` is already included with sensible defaults:
  {
    "quality": "high",
    "source_up": "y",
    "target_up": "z",
    "rotate_x": 0,
    "rotate_y": 0,
    "rotate_z": 0
  }
  Change those values if your CAD uses a different up‑axis.

Notes and tips
- FreeCAD version compatibility: tested with 0.21.x; also works with 1.0.x. If a file crashes Import, the script first tries a direct Shape read, then a document import.
- STL format: ASCII for broad compatibility; if you prefer binary STLs, mention it and we can add a `--binary` switch.
- If you see the FreeCAD banner only and nothing happens when using `FreeCADCmd <script> <args>`, switch to the `-c` invocation shown above; it guarantees the script runs as `__main__`.

Troubleshooting
- macOS “App can’t be opened”: Right‑click `Step2Stl.command` → Open once. Or open the FreeCAD app once to approve it.
- Windows console flashes and closes: open Command Prompt, `cd` to this folder, and run `Step2Stl.bat` to read any messages.
- “FreeCADCmd not found”: make sure FreeCAD is installed (see above), or edit PATH as noted for your OS.

Troubleshooting
- “FreeCADCmd not found”: ensure FreeCAD is installed and CLI is in PATH (see Install FreeCAD).
- macOS double‑click does nothing: Right‑click → Open the first time to bypass Gatekeeper. Or run the `.command` from Terminal to see output.
- Windows double‑click flashes and closes: Open `cmd.exe`, run `Step2Stl.bat`, and check any error messages (path to `FreeCADCmd.exe`, permissions, etc.).
