#!/bin/zsh
# Double-clickable wrapper for macOS to process STEP files via FreeCADCmd.
# Behavior:
# - Looks for STEP files in STEP-INPUT/ (next to this script)
# - Outputs STL to STL-OUTPUT/
# - Moves processed STEP files into STEP-INPUT/_processed/

set -euo pipefail
cd "$(dirname "$0")"

# Ensure FreeCADCmd is available
if [ -d "/Applications/FreeCAD.app/Contents/Resources/bin" ]; then
  export PATH="/Applications/FreeCAD.app/Contents/Resources/bin:$PATH"
fi

if command -v FreeCADCmd >/dev/null 2>&1; then
  FCMD=FreeCADCmd
elif [ -x "/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd" ]; then
  FCMD="/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd"
else
  echo "FreeCADCmd not found. Please install FreeCAD or add FreeCADCmd to PATH." >&2
  echo "Hint (Homebrew): brew install --cask freecad" >&2
  read -k "?Press any key to close..." 2>/dev/null || true
  exit 1
fi

"$FCMD" -c "import sys,runpy; sys.argv=['step2stl.py']; runpy.run_path('step2stl.py', run_name='__main__')"

echo
echo "All done. Check the STL-OUTPUT/ folder."
read -k "?Press any key to close..." 2>/dev/null || true

