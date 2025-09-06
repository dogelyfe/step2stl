@echo off
REM Windows wrapper for step2stl.py - double-click friendly
REM Runs in drop-folder mode using FreeCADCmd

cd /d "%~dp0"

REM Try to find FreeCADCmd.exe in common installation paths
set FREECAD_CMD=
if exist "C:\Program Files\FreeCAD 1.0\bin\FreeCADCmd.exe" (
    set "FREECAD_CMD=C:\Program Files\FreeCAD 1.0\bin\FreeCADCmd.exe"
) else if exist "C:\Program Files\FreeCAD 0.21\bin\FreeCADCmd.exe" (
    set "FREECAD_CMD=C:\Program Files\FreeCAD 0.21\bin\FreeCADCmd.exe"
) else if exist "C:\Program Files (x86)\FreeCAD 1.0\bin\FreeCADCmd.exe" (
    set "FREECAD_CMD=C:\Program Files (x86)\FreeCAD 1.0\bin\FreeCADCmd.exe"
) else if exist "C:\Program Files (x86)\FreeCAD 0.21\bin\FreeCADCmd.exe" (
    set "FREECAD_CMD=C:\Program Files (x86)\FreeCAD 0.21\bin\FreeCADCmd.exe"
) else (
    where FreeCADCmd.exe >nul 2>&1
    if %errorlevel%==0 (
        set "FREECAD_CMD=FreeCADCmd.exe"
    ) else (
        echo ERROR: FreeCADCmd.exe not found. Install FreeCAD first:
        echo   Download from https://www.freecad.org
        echo   Make sure to install FreeCAD with command line tools.
        pause
        exit /b 1
    )
)

echo Using FreeCAD: %FREECAD_CMD%
echo Running step2stl converter in drop-folder mode...
echo.

REM Run the converter using FreeCADCmd with the runpy approach for reliability
"%FREECAD_CMD%" -c "import sys,runpy; p=r'%CD%\step2stl.py'; sys.argv=[p]; runpy.run_path(p, run_name='__main__')"

echo.
echo Conversion complete. Check STL-OUTPUT\ for results.
pause