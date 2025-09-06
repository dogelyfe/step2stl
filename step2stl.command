#!/bin/bash
# macOS wrapper for step2stl.py - double-click friendly
# Runs in drop-folder mode using FreeCADCmd

cd "$(dirname "$0")"

# Try to find FreeCADCmd in common locations
FREECAD_CMD=""
if command -v freecadcmd >/dev/null 2>&1; then
    FREECAD_CMD="freecadcmd"
elif command -v FreeCADCmd >/dev/null 2>&1; then
    FREECAD_CMD="FreeCADCmd"
elif [ -x "/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd" ]; then
    FREECAD_CMD="/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd"
elif [ -x "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd" ]; then
    FREECAD_CMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
else
    echo "ERROR: FreeCADCmd not found. Install FreeCAD first:"
    echo "  brew install --cask freecad"
    echo "Or add FreeCAD to your PATH."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Using FreeCAD: $FREECAD_CMD"
echo "Running step2stl converter in drop-folder mode..."
echo

# Run the converter using FreeCADCmd with the runpy approach for reliability
"$FREECAD_CMD" -c "import sys,runpy; sys.argv=['$(pwd)/step2stl.py']; runpy.run_path('$(pwd)/step2stl.py', run_name='__main__')"

echo
echo "Conversion complete. Check STL-OUTPUT/ for results."
read -p "Press Enter to exit..."