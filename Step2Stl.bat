@echo off
REM Double-clickable wrapper for Windows to process STEP files via FreeCADCmd.
REM Behavior:
REM  - Looks for STEP files in STEP-INPUT\ (next to this script)
REM  - Outputs STL to STL-OUTPUT\
REM  - Moves processed STEP files into STEP-INPUT\_processed\

setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

set FCMD=
if exist "%ProgramFiles%\FreeCAD 1.0\bin\FreeCADCmd.exe" set FCMD="%ProgramFiles%\FreeCAD 1.0\bin\FreeCADCmd.exe"
if exist "%ProgramFiles%\FreeCAD 0.21\bin\FreeCADCmd.exe" set FCMD="%ProgramFiles%\FreeCAD 0.21\bin\FreeCADCmd.exe"
if not defined FCMD (
  for %%G in (FreeCADCmd.exe) do (
    where %%G >nul 2>nul && set FCMD=%%G
  )
)

if not defined FCMD (
  echo FreeCADCmd.exe not found. Please install FreeCAD or add it to PATH.
  echo Download: https://www.freecad.org
  pause
  exit /b 1
)

REM Use Python runpath so __main__ executes with no args (drop-folder mode)
set SCRIPT=%~dp0step2stl.py

%FCMD% -c "import sys,runpy; p=r'%SCRIPT%'; sys.argv=[p]; runpy.run_path(p, run_name='__main__')"

echo.
echo All done. Check the STL-OUTPUT\ folder.
pause

