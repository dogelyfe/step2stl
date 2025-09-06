# step2stl — Drag-and-Drop STEP→STL Converter

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.6+-blue.svg) ![FreeCAD](https://img.shields.io/badge/FreeCAD-0.21%2B-orange.svg)

Convert STEP files to STL with good defaults. No GUI, just drag and drop.

## Quick Start

1. **Clone:** `git clone https://github.com/dogelyfe/step2stl.git`
2. **Install FreeCAD:** `brew install --cask freecad` (macOS) or download from [freecad.org](https://www.freecad.org)
3. **Drop:** Put `.step/.stp` files in `STEP-INPUT/` folder
4. **Run:** Double-click `step2stl.command` (macOS) or `step2stl.bat` (Windows)

→ STL files appear in `STL-OUTPUT/`, originals move to `STEP-INPUT/_processed/`

## How It Works

**Drop-Folder Mode:** The default workflow designed for ease of use:
- Processes all STEP files in `STEP-INPUT/`
- Outputs STL files to `STL-OUTPUT/` 
- Moves processed STEP files to `STEP-INPUT/_processed/` (so reruns skip them)
- High quality conversion with Y→Z orientation by default

## Install FreeCAD

**macOS:**
```bash
brew install --cask freecad
```

**Windows:**
Download installer from [freecad.org](https://www.freecad.org)

**Linux:**
```bash
sudo apt-get install freecad
```

## Advanced Usage

### Command Line
Convert single file:
```bash
FreeCADCmd -c "import sys,runpy; sys.argv=['step2stl.py','file.step']; runpy.run_path('step2stl.py', run_name='__main__')"
```

Convert folder:
```bash
FreeCADCmd -c "import sys,runpy; sys.argv=['step2stl.py','/path/to/folder']; runpy.run_path('step2stl.py', run_name='__main__')"
```

### Options
- `-q/--quality`: `high` (default), `medium`, `low`, `custom`
- `--binary`: Output binary STL (smaller files)
- `-o/--out`: Custom output directory
- `--source-up {x|y|z}` / `--target-up {x|y|z}`: Orientation control

### Configuration
Edit `step2stl.config.json` to change defaults for drop-folder mode:
```json
{
  "quality": "high",
  "source_up": "y",
  "target_up": "z",
  "binary": false
}
```

## Troubleshooting

**macOS "App can't be opened":** Right-click → Open the first time to bypass security

**Windows console flashes:** Open Command Prompt and run `step2stl.bat` to see error messages

**"FreeCADCmd not found":** Make sure FreeCAD is installed and in your PATH

**No output:** Check that STEP files are in `STEP-INPUT/` and not already in `_processed/`